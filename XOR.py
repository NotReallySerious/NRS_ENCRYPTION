import random
import string

def generate_key(x):
    len_key = len(x) * len(x)
    chars = string.ascii_letters + string.digits + string.punctuation
    key = []
    for i in range(len_key):
        c = random.choice(chars)
        d = random.choice(chars)
        e = random.choice(chars)
        key.append(f"{c}{d}{e}")
    return ''.join(key)

def the_actual_XOR(x):
    input_to_hex = x.encode('utf-16').hex()
    key_string = generate_key(input_to_hex)
    key_to_bytes = key_string.encode('utf-8')
    
    XORed = []
    for i, char in enumerate(input_to_hex):   
        key_byte = key_to_bytes[i % len(key_to_bytes)]
        xor_result = ord(char) ^ key_byte     
        XORed.append(xor_result)

    print(f"Original  : {x}")
    print(f"Hex input : {input_to_hex}")
    print(f"XORed     : {bytes(XORed).hex()}")
    return XORed

