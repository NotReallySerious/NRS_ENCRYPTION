import hashing, Convertbase64, salt, SHA256, XOR 
from hashing import hash
from Convertbase64 import Convert2Base64
from salt import key
import decryption
from decryption import nrs_decrypt_files
from SHA256 import convert2SHA256
from XOR import the_actual_XOR, generate_key, the_actual_XOR_for_password
import encrypt_file
from encrypt_file import nrs_encrypt_files
import string
import colorama
import pyfiglet
from colorama import Style, init, Fore
import os
import pathlib 
from pathlib import Path

init(autoreset=True)

def password_generate_policy(x):
    letters_uppercase = list(string.ascii_uppercase)
    letters_lowercase = list(string.ascii_lowercase)
    numbers = list(string.digits)
    special_chars = list(string.punctuation)

    uppercase_count = lowercase_count = number_count = special_count = 0

    if len(x) < 12:
        print(Fore.RED + 'Password must be at least 12 characters')
        return False

    for char in x:
        if char in letters_lowercase: lowercase_count += 1
        elif char in letters_uppercase: uppercase_count += 1
        elif char in numbers: number_count += 1
        elif char in special_chars: special_count += 1
        else: return False

    if lowercase_count < 1 or uppercase_count < 1 or number_count < 1 or special_count < 1:
        print(Fore.RED + 'Password must contain: 1 uppercase, 1 lowercase, 1 digit, and 1 special char')
        return False

    print(Fore.GREEN + "Password criteria met. Proceeding...")
    return True

def nrs_password_encrypt(password):
    first_round = hash(password)
    second_round = the_actual_XOR_for_password(first_round)
    third_round = Convert2Base64(second_round)
    final_password = convert2SHA256(third_round)
    return final_password

def main():
    formatted = pyfiglet.figlet_format("NRS _ ENCRYPTION", font='doom', width=800)
    print(Fore.LIGHTCYAN_EX + formatted)
    print(Fore.CYAN + '-' * 50 + "\nAuthor: Mr Hoodie | Version: 1.0\n" + '-' * 50)

    while True:
        print("\n1. Encrypting a folder\n2. Decrypting a folder\n3. Exit")
        choice = input('Enter your choice: ')
        
        if choice == '1':
            while True:
                master_pass = input('Enter your Password: ').strip()
                if password_generate_policy(master_pass):
                    encrypted_pass_seal = nrs_password_encrypt(master_pass)
                    break
            
            folder_path = input('Enter the FULL path: ').strip()
            path_obj = Path(os.path.abspath(folder_path))

            if path_obj.exists() and path_obj.is_dir():
                key_file = path_obj / ".nrs_lock"
                with open(key_file, 'w') as f:
                    f.write(encrypted_pass_seal)

                nrs_encrypt_files(str(path_obj), master_pass)
                print(Fore.GREEN + "[✓] Vault Created Successfully.")
            else:
                print(Fore.RED + "Invalid folder path!")

        elif choice == '2':
            folder_path = input('Enter path to unlock: ').strip()
            path_obj = Path(os.path.abspath(folder_path))
            key_file = path_obj / ".nrs_lock"

            if not key_file.exists():
                print(Fore.RED + "[!] No lock file found.")
                continue

            attempt = input('Enter Master Password: ').strip()
            hashed_attempt = nrs_password_encrypt(attempt) 

            with open(key_file, 'r') as f:
                stored_seal = f.read().strip()

            if hashed_attempt == stored_seal:
                print(Fore.GREEN + "[✓] Access Granted.")
                nrs_decrypt_files(str(path_obj), attempt)
                if key_file.exists():
                    key_file.unlink()
            else:
                print(Fore.RED + "[X] Incorrect Password.")

        elif choice == '3':
            break
        else:
            print(Fore.YELLOW + "Please choose 1, 2, or 3.")

if __name__ == '__main__':
    main()