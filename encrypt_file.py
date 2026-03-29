import pathlib
from pathlib import Path
from XOR import the_actual_XOR
from Convertbase64 import Convert2Base64
from SHA256 import convert2SHA256
from hashing import hash
import json
import os
import platform 

def nrs_encrypt_files(path, password):
    file_path = Path(path)
    files = list(file_path.rglob("*"))
    
    name_manifest = {}
    manifest_file = file_path / ".nrs_manifest"

    if not file_path.exists() or not file_path.is_dir():
        print(f"Error: {file_path} is not a valid directory.")
        return

    for item in files:
        if (item.is_file() and 
            item.suffix not in ['.py', '.nrs'] and 
            item.name not in ['.nrs_lock', '.nrs_manifest', '.DS_Store', 'desktop.ini']):
            
            try:
                original_full_name = item.name 
                original_ext = item.suffix
                original_stem = item.stem

                xor_data = the_actual_XOR(item, password)
                b64_content = Convert2Base64(xor_data)
                
                header = f"{original_ext}||".encode('utf-8')
                with open(item, 'wb') as f:
                    f.write(header + b64_content)

                stage1 = hash(original_stem)
                stage2 = Convert2Base64(stage1.encode('utf-8')).decode('utf-8')
                stage3 = convert2SHA256(stage2)
                
                final_name = f"{stage3[:15]}.nrs"
                new_path = item.parent / final_name
                
                name_manifest[final_name] = original_full_name
                item.rename(new_path)
                print(f"[-] Secured: {final_name}")

            except Exception as e:
                print(f"[!] Error on {item.name}: {e}")

    if name_manifest:
        manifest_json = json.dumps(name_manifest).encode('utf-8')
        
        encrypted_manifest = the_actual_XOR(manifest_json, password)
        
        with open(manifest_file, 'wb') as f:
            f.write(encrypted_manifest)
        
        current_os = platform.system()
        if current_os == "Windows":
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(str(manifest_file), 2)

    print(f"\nNRS Vault Operation Complete. Compatible with {platform.system()}.")