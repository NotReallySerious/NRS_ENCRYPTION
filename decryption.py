import os
import json
import platform
import signal
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from XOR import decrypt_file_bytes, decrypt_manifest
import hashlib

exiting = False
failed_files = []  # Track failed decryptions


def signal_handler(sig, frame):
    global exiting
    exiting = True


def decrypt_worker(args):
    item_str, password, name_map = args
    try:
        if platform.system() == "Windows" and not item_str.startswith("\\\\?\\"):
            item_str = "\\\\?\\" + os.path.abspath(item_str)

        item = Path(item_str)

        with open(item, "rb") as fh:
            combined = fh.read()

        # Parse header: ext||stem||checksum||encrypted_data
        first_sep = combined.find(b"||")
        if first_sep == -1:
            raise ValueError("Invalid file format: missing first separator")
        
        original_ext = combined[:first_sep].decode("utf-8")
        rest         = combined[first_sep + 2:]

        second_sep = rest.find(b"||")
        if second_sep == -1:
            raise ValueError("Invalid file format: missing second separator")
        
        original_stem = rest[:second_sep].decode("utf-8")
        rest2         = rest[second_sep + 2:]

        # Extract checksum from header
        third_sep = rest2.find(b"||")
        if third_sep == -1:
            raise ValueError("Invalid file format: missing checksum separator")
        
        checksum_stored = rest2[:third_sep].decode("utf-8")
        encrypted_bytes = rest2[third_sep + 2:]

        # Decrypt file data
        original_bytes = decrypt_file_bytes(encrypted_bytes, password, original_stem)

        # Verify integrity using checksum
        checksum_computed = hashlib.sha256(original_bytes).hexdigest()[:16]
        if checksum_stored != checksum_computed:
            raise ValueError(f"Integrity check failed: checksum mismatch. Data may be corrupted.")

        # Reconstruct original filename
        original_name = name_map.get(item.name) or f"{original_stem}{original_ext}"
        restored_path = item.parent / original_name

        # Handle name collision (shouldn't happen with new fixed encryption)
        counter = 1
        while restored_path.exists():
            base = f"{original_stem}_{counter}{original_ext}"
            restored_path = item.parent / base
            counter += 1

        # Write decrypted file
        with open(restored_path, "wb") as fh:
            fh.write(original_bytes)

        # Remove encrypted file
        item.unlink()
        return original_name
    except Exception as e:
        error_msg = f"[!] Failed: {Path(item_str).name} → {type(e).__name__}: {e}"
        tqdm.write(error_msg)
        failed_files.append((Path(item_str).name, str(e)))
        return None


def nrs_decrypt_files(path: str, password: str):
    global exiting, failed_files
    exiting = False
    failed_files = []
    signal.signal(signal.SIGINT, signal_handler)

    abs_path = os.path.abspath(path)
    if platform.system() == "Windows" and not abs_path.startswith("\\\\?\\"):
        abs_path = "\\\\?\\" + abs_path

    folder        = Path(abs_path)
    manifest_file = folder / ".nrs_manifest"

    # Decrypt manifest using password-only derived key
    name_map = {}
    if manifest_file.exists():
        try:
            with open(manifest_file, "rb") as fh:
                enc_manifest = fh.read()
            dec_manifest = decrypt_manifest(enc_manifest, password)
            name_map     = json.loads(dec_manifest.decode("utf-8"))
        except Exception as e:
            tqdm.write(f"[!] Warning: Could not decrypt manifest: {e}. Filenames may not be fully restored.")

    encrypted_files = list(folder.rglob("*.nrs"))
    total           = len(encrypted_files)

    if total == 0:
        print("[!] No .nrs files found to decrypt.")
        return

    pbar = tqdm(total=total, desc="Unlocking Vault", unit="file",bar_format="{l_bar}{bar:30}{r_bar}")
    cpu_count   = os.cpu_count() or 2
    worker_args = [(str(f), password, name_map) for f in encrypted_files]

    try:
        with ProcessPoolExecutor(max_workers=cpu_count) as executor:
            futures = {
                executor.submit(decrypt_worker, arg): arg[0]
                for arg in worker_args
            }

            for future in as_completed(futures):
                if exiting:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

                pbar.set_description(f"Restoring: {Path(futures[future]).name[:20]}...")
                future.result()
                pbar.update(1)

    finally:
        pbar.close()

        if not exiting and manifest_file.exists():
            manifest_file.unlink()

        if exiting:
            print("\n[!] Decryption interrupted. Progress saved.")
            sys.exit(0)

    # Report summary
    print("\n[✓] NRS Vault Decryption Complete.")
    if failed_files:
        print(f"\n[⚠] {len(failed_files)} file(s) failed to decrypt:")
        for filename, error in failed_files:
            print(f"   - {filename}: {error}")
    else:
        print("[✓] All files decrypted successfully.")