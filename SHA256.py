import hashlib
import string
import Convertbase64
from Convertbase64 import ConvertBase64

def convert2SHA256(x):
    string_encode = x.encode('utf-16')
    hash_object = hashlib.sha256(string_encode)
    hex_string = hash_object.hexdigest()
    return hex_string

