import hashlib

def convert2SHA256(x) -> str:
    if isinstance(x, (bytes, bytearray)):
        data = bytes(x)
    else:
        data = str(x).encode('utf-8')   

    try:
        return hashlib.sha256(data, usedforsecurity=False).hexdigest()
    except TypeError:
        return hashlib.sha256(data).hexdigest()