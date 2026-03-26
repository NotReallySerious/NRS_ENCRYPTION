import base64
import string

def ConvertBase64(x):
    text_to_bytes = x.encode('utf-8')
    bytes_to_base64 = base64.b64encode(text_to_bytes)
    print(bytes_to_base64)
    return bytes_to_base64

