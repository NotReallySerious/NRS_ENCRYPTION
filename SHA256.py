import hashlib
import string
import Convertbase64

def convert2SHA256(x):
    if isinstance(x, bytes):
        data_to_hash = x
    else:
        data_to_hash = x.encode('utf-16')

    hash_object = hashlib.sha256(data_to_hash)
    return hash_object.hexdigest()

