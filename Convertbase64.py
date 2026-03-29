import base64

def Convert2Base64(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    
    bytes_to_base64 = base64.b64encode(x)
    return bytes_to_base64