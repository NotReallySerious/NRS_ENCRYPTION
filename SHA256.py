import hashlib


def convert2SHA256(x) -> str:
    """
    Convert input to SHA256 hash (hex digest).
    Handles bytes, bytearray, and string inputs.
    """
    if isinstance(x, (bytes, bytearray)):
        data = bytes(x)
    else:
        data = str(x).encode('utf-8')

    try:
        return hashlib.sha256(data, usedforsecurity=False).hexdigest()
    except TypeError:
        # Fallback for older Python versions without usedforsecurity parameter
        return hashlib.sha256(data).hexdigest()