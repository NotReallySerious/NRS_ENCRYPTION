import encrypt_file
from encrypt_file import nrs_encrypt_files
import os
import pathlib
from pathlib import Path

def nrs_encrypt_folder(path, password):
    folder_path = Path(path)

    if folder_path.is_dir():
        print(f'[!] Starting encryption on {folder_path}')
        nrs_encrypt_files(path, password)
        print(f"{folder_path} encrypted succesfully")
    else:
        print("[!] NOT a folder")