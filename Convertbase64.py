import base64

def Convert2Base64(x) -> bytes:
    if isinstance(x, str):
        x = x.encode('utf-8')
    elif isinstance(x, (bytearray, memoryview)):
        x = bytes(x)
    return base64.b64encode(x)