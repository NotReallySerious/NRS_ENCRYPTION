import random
import string

def key(x):
    key_size = len(x)
    # The key elements
    chars = list(string.ascii_letters)
    numbers = list(string.digits)
    special_char = list(string.punctuation)
    key = []
    for _ in range(key_size):
        c = random.choice(chars)
        num = random.choice(numbers)
        sc = random.choice(special_char)
        key.append(f"{c}{num}{sc}")
    
    return key

