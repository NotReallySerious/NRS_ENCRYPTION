import base64
import json
import os
import platform
from pathlib import Path
from XOR import the_actual_XOR

def nrs_decrypt_files(path, password):
    folder_path = Path(path)
    manifest_file = folder_path / ".nrs_manifest"
    
    name_map = {}
    if manifest_file.exists():
        try:
            with open(manifest_file, 'r') as f:
                name_map = json.load(f)
        except Exception as e:
            print(f"[!] Warning: Could not read manifest. Using generic names. {e}")

    encrypted_files = list(folder_path.rglob("*.nrs"))
    if not encrypted_files:
        print("[!] No .nrs files found in this directory.")
        return

    for item in encrypted_files:
        try:
            with open(item, "rb") as f:
                raw_data = f.read()

            separator = b"||"
            sep_index = raw_data.find(separator)
            if sep_index == -1:
                print(f"[!] Skip: {item.name} has no NRS header.")
                continue

            original_ext = raw_data[:sep_index].decode('utf-8')
            b64_content = raw_data[sep_index + len(separator):]

            xor_ready_data = base64.b64decode(b64_content)

            original_bytes = the_actual_XOR(xor_ready_data, password)

            original_name = name_map.get(item.name, f"restored_{item.stem}{original_ext}")
            restored_path = item.parent / original_name

            with open(restored_path, "wb") as f:
                f.write(original_bytes)

            item.unlink()
            print(f"[※] Restored: {original_name}")

        except Exception as e:
            print(f"[!] Critical Error on {item.name}: {e}")

        if manifest_file.exists():
            try:
                with open(manifest_file, 'rb') as f:
                    encrypted_data = f.read()
            
                decrypted_manifest_bytes = the_actual_XOR(encrypted_data, password)
            
                name_map = json.loads(decrypted_manifest_bytes.decode('utf-8'))
            except Exception:
                print("[!] Could not decrypt manifest. Wrong password or corrupted file.")
    
    print(f"\n[✓] NRS Vault Decryption Complete on {platform.system()}.")