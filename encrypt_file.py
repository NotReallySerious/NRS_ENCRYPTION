import os
import json
import platform
import signal
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from XOR import encrypt_file_bytes, encrypt_manifest
from hashing import hash
from SHA256 import convert2SHA256
import hashlib

exiting = False


def signal_handler(sig, frame):
    global exiting
    exiting = True


def encrypt_worker(args):
    item_str, password = args
    try:
        if platform.system() == "Windows" and not item_str.startswith("\\\\?\\"):
            item_str = "\\\\?\\" + os.path.abspath(item_str)

        item          = Path(item_str)
        original_name = item.name
        original_stem = item.stem      # e.g. "photo"
        original_ext  = item.suffix    # e.g. ".jpg"

        # Read original file
        with open(item, "rb") as fh:
            original_data = fh.read()

        # Calculate checksum of original data for integrity verification
        checksum = hashlib.sha256(original_data).hexdigest()[:16]

        # Encrypt file content
        encrypted_bytes = encrypt_file_bytes(item, password)

        # Header format: ext||stem||checksum||encrypted_data
        # This ensures unique mapping and integrity checking
        header = f"{original_ext}||{original_stem}||{checksum}||".encode("utf-8")

        # Write encrypted file with header
        with open(item, "wb") as fh:
            fh.write(header + encrypted_bytes)

        # Create unique encrypted filename using BOTH stem and extension
        # This fixes the bug where photo.jpg and photo.png would collide
        unique_input = f"{original_stem}{original_ext}"
        stage1       = hash(unique_input)
        stage3       = convert2SHA256(stage1)
        final_name   = f"{stage3[:15]}.nrs"
        new_path     = item.parent / final_name

        # Atomic rename to avoid inconsistent state
        item.rename(new_path)

        return (final_name, original_name)
    except Exception as e:
        tqdm.write(f"[!] Failed: {Path(item_str).name} → {type(e).__name__}: {e}")
        return None


def nrs_encrypt_files(path: str, password: str):
    global exiting
    exiting = False
    signal.signal(signal.SIGINT, signal_handler)

    abs_path = os.path.abspath(path)
    if platform.system() == "Windows" and not abs_path.startswith("\\\\?\\"):
        abs_path = "\\\\?\\" + abs_path

    folder = Path(abs_path)
    files_to_process = [
        f for f in folder.rglob("*")
        if f.is_file()
        and f.suffix not in (".py", ".nrs")
        and f.name not in (".nrs_lock", ".nrs_manifest")
    ]

    total = len(files_to_process)
    if total == 0:
        print("No files found to encrypt.")
        return

    name_manifest = {}
    pbar = tqdm(total=total, desc="Securing Vault", unit="file",bar_format="{l_bar}{bar:30}{r_bar}")
    worker_args = [(str(f), password) for f in files_to_process]
    cpu_count = os.cpu_count() or 2

    try:
        with ProcessPoolExecutor(max_workers=cpu_count) as executor:
            futures = {
                executor.submit(encrypt_worker, arg): arg[0]
                for arg in worker_args
            }

            for future in as_completed(futures):
                if exiting:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

                pbar.set_description(f"Encrypting: {Path(futures[future]).name[:20]}...")
                result = future.result()
                if result:
                    new_nrs, old_real = result
                    name_manifest[new_nrs] = old_real
                pbar.update(1)

    finally:
        pbar.close()

        if name_manifest:
            manifest_path = folder / ".nrs_manifest"
            # Manifest uses password-only derived key (same chain, no stem)
            manifest_data      = json.dumps(name_manifest).encode("utf-8")
            encrypted_manifest = encrypt_manifest(manifest_data, password)
            with open(manifest_path, "wb") as fh:
                fh.write(encrypted_manifest)

            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(manifest_path), 2)

        if exiting:
            print("\n[!] Encryption interrupted.")
            sys.exit(0)