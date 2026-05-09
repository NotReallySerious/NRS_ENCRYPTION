import os
import string
import hashlib
import base64
from pathlib import Path
 
import colorama
import pyfiglet
from colorama import Style, init, Fore
 
from hashing import hash
from Convertbase64 import Convert2Base64
from SHA256 import convert2SHA256
from XOR import the_actual_XOR, the_actual_XOR_for_password
from encrypt_file import nrs_encrypt_files
from decryption import nrs_decrypt_files
 
init(autoreset=True)
 
# Pre-build sets once at module level — O(1) lookup, not rebuilt per call
_LOWER   = set(string.ascii_lowercase)
_UPPER   = set(string.ascii_uppercase)
_DIGITS  = set(string.digits)
_SPECIAL = set(string.punctuation)
_ALLOWED = _LOWER | _UPPER | _DIGITS | _SPECIAL
 
 
def password_generate_policy(x: str) -> bool:
    """Validate password meets security criteria."""
    if len(x) < 12:
        print(Fore.RED + 'Password must be at least 12 characters')
        return False
 
    lower = upper = digit = special = 0
    for ch in x:
        if ch not in _ALLOWED:
            print(Fore.RED + f"Password contains an invalid character: {repr(ch)}")
            return False
        if ch in _LOWER:    lower   += 1
        elif ch in _UPPER:  upper   += 1
        elif ch in _DIGITS: digit   += 1
        else:               special += 1
 
    if lower < 1 or upper < 1 or digit < 1 or special < 1:
        print(Fore.RED + 'Password must contain: 1 uppercase, 1 lowercase, 1 digit, and 1 special char')
        return False
 
    print(Fore.GREEN + "Password criteria met. Proceeding...")
    return True
 
 
def nrs_password_encrypt(password: str) -> str:
    """Hash password through multiple rounds for security."""
    first_round  = hash(password)
    second_round = the_actual_XOR_for_password(first_round)
    third_round  = Convert2Base64(second_round)
    final        = convert2SHA256(third_round)
    return final
 
 
def main():
    formatted = pyfiglet.figlet_format("NRS _ ENCRYPTION", font='doom', width=800)
    print(Fore.LIGHTCYAN_EX + formatted)
    print(Fore.CYAN + '-' * 50 + "\nAuthor: Mr Hoodie | Version: 2.0 (Fixed)\n" + '-' * 50)
 
    while True:
        print("\n1. Encrypting a folder\n2. Decrypting a folder\n3. Exit")
        choice = input('Enter your choice: ').strip()
 
        if choice == '1':
            while True:
                master_pass = input('Enter your Password: ').strip()
                if password_generate_policy(master_pass):
                    encrypted_pass_seal = nrs_password_encrypt(master_pass)
                    break
 
            folder_path = input('Enter the FULL path (without quotes): ').strip()
            path_obj    = Path(os.path.abspath(folder_path))
 
            if path_obj.exists() and path_obj.is_dir():
                key_file = path_obj / ".nrs_lock"
                try:
                    with open(key_file, 'w') as f:
                        f.write(encrypted_pass_seal)
                    
                    print(Fore.CYAN + "[*] Starting encryption...")
                    nrs_encrypt_files(str(path_obj), master_pass)
                    print(Fore.GREEN + "[✓] Vault Created Successfully.")
                except Exception as e:
                    print(Fore.RED + f"[!] Encryption failed: {e}")
                    if key_file.exists():
                        key_file.unlink()
            else:
                print(Fore.RED + "Invalid folder path!")
 
        elif choice == '2':
            folder_path = input('Enter path to unlock: ').strip()
            path_obj    = Path(os.path.abspath(folder_path))
            key_file    = path_obj / ".nrs_lock"
 
            if not key_file.exists():
                print(Fore.RED + "[!] No lock file found.")
                continue
 
            try:
                attempt        = input('Enter Master Password: ').strip()
                hashed_attempt = nrs_password_encrypt(attempt)
 
                with open(key_file, 'r') as f:
                    stored_seal = f.read().strip()
 
                if hashed_attempt == stored_seal:
                    print(Fore.GREEN + "[✓] Access Granted.")
                    print(Fore.CYAN + "[*] Starting decryption...")
                    nrs_decrypt_files(str(path_obj), attempt)
                    if key_file.exists():
                        key_file.unlink()
                        print(Fore.GREEN + "[✓] Lock file removed.")
                else:
                    print(Fore.RED + "[X] Incorrect Password.")
            except Exception as e:
                print(Fore.RED + f"[!] Decryption error: {e}")
 
        elif choice == '3':
            print(Fore.YELLOW + "Exiting...")
            break
        else:
            print(Fore.YELLOW + "Please choose 1, 2, or 3.")

if __name__ == '__main__':
    main()