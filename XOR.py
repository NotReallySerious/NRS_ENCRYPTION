import random
import string
import pathlib 
from random import randint
from colorama import Fore, Style, init

def generate_key(x):
    pepper = "NRS_VAULT_VERSION_1.0.0"
    random.seed(x + pepper)

    len_key = len(x) * randint(10, 999999)
    chars = string.ascii_letters + string.digits + string.punctuation
    key = []
    for i in range(len_key):
        key.append(f"{random.choice(chars)}{random.choice(chars)}{random.choice(chars)}")
    return ''.join(key)

def the_actual_XOR_for_password(user_input):

    if isinstance(user_input, str):
        input_to_bytes = user_input.encode('utf-16-le')
    else:
        input_to_bytes = user_input

    key_string = generate_key(user_input)
    key_to_bytes = key_string.encode('utf-8')
    
    XORed = bytearray()
    for i, byte in enumerate(input_to_bytes):   
        key_byte = key_to_bytes[i % len(key_to_bytes)]
        xor_result = byte ^ key_byte     
        XORed.append(xor_result)

    return bytes(XORed)

def the_actual_XOR(data, password_seed):
    if isinstance(data, (str, pathlib.Path)):
        with open(data, 'rb') as f:
            file_data = f.read()
        seed = str(data).encode().hex() 
    else:
        file_data = data
        seed = password_seed 

    random.seed(seed)
    
    key_string = generate_key(seed)
    key_to_bytes = key_string.encode('utf-8')

    final_data = bytearray()
    for i, b in enumerate(file_data):
        key_byte = key_to_bytes[i % len(key_to_bytes)] 
        final_data.append(b ^ key_byte)
    
    return bytes(final_data)