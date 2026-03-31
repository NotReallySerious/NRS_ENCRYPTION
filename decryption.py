import os
import json
import platform
import signal
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from XOR import the_actual_XOR

exiting = False

def signal_handler(sig, frame):
    global exiting
    exiting = True

def decrypt_worker(item, password, name_map):
    try:
        with open(item, "rb") as f:
            combined_data = f.read()

        separator = b"||"
        sep_index = combined_data.find(separator)
        if sep_index == -1:
            return None

        original_ext = combined_data[:sep_index].decode('utf-8')
        xor_payload = combined_data[sep_index + len(separator):]

        original_bytes = the_actual_XOR(xor_payload, password)

        original_name = name_map.get(item.name)
        if not original_name:
            original_name = f"restored_{item.stem}{original_ext}"
        
        restored_path = item.parent / original_name

        with open(restored_path, "wb") as f:
            f.write(original_bytes)

        item.unlink()
        return original_name
    except Exception:
        return None

def nrs_decrypt_files(path, password):
    global exiting
    exiting = False
    signal.signal(signal.SIGINT, signal_handler)

    abs_path = os.path.abspath(path)
    if platform.system() == "Windows" and not abs_path.startswith("\\\\?\\"):
        abs_path = "\\\\?\\" + abs_path
    
    folder_path = Path(abs_path)
    manifest_file = folder_path / ".nrs_manifest"
    
    name_map = {}
    if manifest_file.exists():
        try:
            with open(manifest_file, 'rb') as f:
                encrypted_manifest = f.read()
            decrypted_manifest_bytes = the_actual_XOR(encrypted_manifest, password)
            name_map = json.loads(decrypted_manifest_bytes.decode('utf-8'))
        except Exception:
            pass

    encrypted_files = list(folder_path.rglob("*.nrs"))
    total_files = len(encrypted_files)
    
    if total_files == 0:
        print("[!] No .nrs files found to decrypt.")
        return

    # Initialize the Progress Bar
    pbar = tqdm(total=total_files, desc="Unlocking Vault", unit="file", bar_format='{l_bar}{bar:30}{r_bar}')

    try:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {executor.submit(decrypt_worker, f, password, name_map): f for f in encrypted_files}
            
            for future in as_completed(futures):
                if exiting:
                    executor.shutdown(wait=True, cancel_futures=True)
                    break
                
                # Update description with current filename
                current_file = futures[future]
                pbar.set_description(f"Restoring: {current_file.name[:20]}...")
                
                result = future.result()
                pbar.update(1)

    finally:
        pbar.close()
        if not exiting and manifest_file.exists():
            manifest_file.unlink()
        
        if exiting:
            print("\n[!] Decryption interrupted. Progress saved.")
            sys.exit(0)

    print(f"\n[✓] NRS Vault Decryption Complete.")