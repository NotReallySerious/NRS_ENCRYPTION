import random
import string


def hash(x: str) -> str:
    hex_seed  = x.encode('utf-16').hex()      
    rng       = random.Random(hex_seed)         
    chars     = string.ascii_letters + string.digits
    return ''.join(rng.choices(chars, k=16))  