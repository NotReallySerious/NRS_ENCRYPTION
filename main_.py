import hashing, Convertbase64, salt, SHA256, XOR 
from hashing import hash
from Convertbase64 import ConvertBase64
from salt import key
from SHA256 import convert2SHA256
from XOR import the_actual_XOR, generate_key
import string
import colorama
import pyfiglet
from colorama import Style,init,Fore
import os
import pathlib 
from pathlib import Path

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

def encrypt_text_file(filepath, password):
    filepath = Path(filepath)   
    
    if filepath.exists() and filepath.is_file():
        file_size = filepath.stat().st_size
        key = generate_key(password)
        key_to_bytes = key.encode('utf-8')
    else:
        return False
    
    with open(filepath, 'rb') as f:
        data = bytearray(f.read())

        for i in range(len(data)):
            data[i] ^= key_to_bytes[i % len(key_to_bytes)]
        
        with open(filepath, 'wb') as w:
            w.write(data)

def main():
    # Top banner
    Banner_text = "N R S _ E N C R Y P T I O N"
    formatted = pyfiglet.figlet_format(Banner_text, font='larry3d', width=800)
    colored = Fore.LIGHTCYAN_EX + formatted
    print(Fore.CYAN + '-' * 50)
    print(Fore.CYAN + "Author: Mr Hoodie")
    print(Fore.CYAN + "Version: 1.0")
    print(Fore.CYAN + "Encrypt your secrets with totally random key")
    print(Fore.CYAN + '-' * 50)





