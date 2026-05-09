import base64


def Convert2Base64(x) -> bytes:
    """
    Convert input to Base64-encoded bytes.
    Handles str, bytes, bytearray, and memoryview inputs.
    """
    if isinstance(x, str):
        x = x.encode('utf-8')
    elif isinstance(x, (bytearray, memoryview)):
        x = bytes(x)
    elif not isinstance(x, bytes):
        raise TypeError(f"Expected str, bytes, bytearray, or memoryview, got {type(x)}")
    
    return base64.b64encode(x)