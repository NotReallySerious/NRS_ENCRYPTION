import salt
import random
import string
from salt import key 

def hash(x):
    input_to_hex = x.encode('utf-16').hex()
    salt = key(input_to_hex)
    chars_repo = list(string.ascii_letters + string.digits)
    result = []
    for i in range(len(x) + 10):
        random_match = random.choice(chars_repo)
        result.append(random_match)
    
    final_result = ''.join(result)
    return final_result


