import hashing, Convertbase64, salt, SHA256, XOR 
from hashing import hash
from Convertbase64 import Convert2Base64
from salt import key
import decryption
from decryption import nrs_decrypt_files
from SHA256 import convert2SHA256
from XOR import the_actual_XOR, generate_key, the_actual_XOR_for_password
import encrypt_file
import encrypt_folder
from encrypt_folder import nrs_encrypt_folder
from encrypt_file import nrs_encrypt_files
import string
import colorama
import pyfiglet
from colorama import Style,init,Fore
import os
import pathlib 
from pathlib import Path
import random

def password_generate_policy(x):
    letters_uppercase = list(string.ascii_uppercase)
    letters_lowercase = list(string.ascii_lowercase)
    numbers = list(string.digits)
    special_chars = list(string.punctuation)

    uppercase_count = 0
    lowercase_count = 0
    number_count = 0
    special_count = 0

    if len(x) < 12:
        print('Password must be at least 12 characters')
        return False

    for char in x:
        if char in letters_lowercase:
            lowercase_count += 1
        elif char in letters_uppercase:
            uppercase_count += 1
        elif char in numbers:
            number_count += 1
        elif char in special_chars:
            special_count += 1
        else:
            return False

    if lowercase_count < 1:
        print('Password must have at least 1 lowercase')
        return False
    elif uppercase_count < 1:
        print('Password must have at least 1 uppercase')
        return False
    elif number_count < 1:
        print('Password must have at least 1 digit number')
        return False
    elif special_count < 1:
        print('Password must have at least 1 special character')
        return False

    print(f"{x} matches all criteria. Proceeding")
    return True

def nrs_password_encrypt(password):

    print(Fore.WHITE + f"Initial Password: {password}")
    first_round = hash(password)
    print(Fore.GREEN + f"[1] First Round result: {first_round}")
    second_round = the_actual_XOR_for_password(first_round)
    print(Fore.RED + f"[2] Second Round result: {second_round}")
    third_round = Convert2Base64(second_round)
    print(Fore.CYAN + f"[3] Third Round result: {third_round}")
    final_password = convert2SHA256(third_round)
    print(Fore.YELLOW + f"[4] fourth Round result: {final_password}")
    
    return final_password

def main():
    # Top banner
    Banner_text = "N R S _ E N C R Y P T I O N"
    formatted = pyfiglet.figlet_format(Banner_text, font='larry3d', width=800)
    colored = Fore.LIGHTCYAN_EX + formatted
    print(colored)
    print(Fore.CYAN + '-' * 50)
    print(Fore.CYAN + "Author: Mr Hoodie")
    print(Fore.CYAN + "Version: 1.0")
    print(Fore.CYAN + "Encrypt your secrets with totally random key")
    print(Fore.CYAN + '-' * 50)

    while True:
        print("1. Encrypting a folder")
        print("2. Decrypting a folder")
        print("3. Exit")
        choice = int(input('Enter your choice: '))
        if choice not in [1,2,3]:
            print("please choose between 1, 2 and 3 only")
        else:
            match choice:
                    case 1:
                        while True:
                            master_pass = input('Enter your Password: ').strip()
                        
                            if password_generate_policy(master_pass):
                                encrypted_pass_seal = nrs_password_encrypt(master_pass)
                                break
                            else:
                                print(Fore.RED + "Lineage check failed. Please try again.\n")                        
                        
                        folder_path = input('Enter the FULL path: ').strip()
                        path_obj = Path(folder_path)

                        if path_obj.exists() and path_obj.is_dir():

                            key_file = path_obj / ".nrs_lock"
                            with open(key_file, 'w') as f:
                                f.write(encrypted_pass_seal)

                            nrs_encrypt_folder(folder_path, master_pass)
                            
                            print(f"{Fore.GREEN}[✓] Vault Created Successfully.")
                        else:
                            print(Fore.RED + "Invalid folder path!")
                    
                    case 2:
                        folder_path = input('Enter path to unlock: ').strip()
                        path_obj = Path(folder_path)
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
                            nrs_decrypt_files(folder_path, attempt)

                            key_file.unlink()
                        else:
                            print(Fore.RED + "[X] Incorrect Password.")

                    case 3:
                        break
            
if __name__ == '__main__':
    main()


