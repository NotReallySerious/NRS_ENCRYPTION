import os
import json
import platform
import signal
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from XOR import the_actual_XOR
from hashing import hash
from SHA256 import convert2SHA256

exiting = False

def signal_handler(sig, frame):
    global exiting
    exiting = True

def encrypt_worker(item, password):
    try:
        original_name = item.name
        original_suffix = item.suffix

        xor_data = the_actual_XOR(item, password)
        header = f"{original_suffix}||".encode('utf-8')
        
        with open(item, 'wb') as f:
            f.write(header + xor_data)

        stage1 = hash(item.stem)
        stage3 = convert2SHA256(stage1)
        final_name = f"{stage3[:15]}.nrs"
        
        new_path = item.parent / final_name
        item.rename(new_path)
        
        return (final_name, original_name)
    except Exception:
        return None

def nrs_encrypt_files(path, password):
    global exiting
    exiting = False
    signal.signal(signal.SIGINT, signal_handler)

    abs_path = os.path.abspath(path)
    if platform.system() == "Windows" and not abs_path.startswith("\\\\?\\"):
        abs_path = "\\\\?\\" + abs_path
    
    file_path = Path(abs_path)
    all_items = list(file_path.rglob("*"))
    files_to_process = [
        f for f in all_items 
        if f.is_file() and 
        f.suffix not in ['.py', '.nrs'] and 
        f.name not in ['.nrs_lock', '.nrs_manifest']
    ]
    
    name_manifest = {}

    try:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {executor.submit(encrypt_worker, f, password): f for f in files_to_process}
            
            for future in as_completed(futures):
                if exiting:
                    executor.shutdown(wait=True, cancel_futures=True)
                    break
                
                res = future.result()
                if res:
                    new_nrs, old_real = res
                    name_manifest[new_nrs] = old_real

    finally:
        if name_manifest:
            manifest_path = file_path / ".nrs_manifest"
            manifest_data = json.dumps(name_manifest).encode('utf-8')
            encrypted_manifest = the_actual_XOR(manifest_data, password)
            
            with open(manifest_path, 'wb') as f:
                f.write(encrypted_manifest)
            
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(manifest_path), 2)

        if exiting:
            sys.exit(0)