import hashlib
import pathlib
import hmac
from hashing import hash
from Convertbase64 import Convert2Base64
from SHA256 import convert2SHA256

_PEPPER     = "NRS_VAULT_VERSION_2.0.0"
_CHUNK_SIZE = 4 * 1024 * 1024         


def _derive_chunk_key(seed_str: str, chunk_index: int) -> bytes:
    """Derive deterministic key bytes for a chunk using HMAC-SHA256."""
    raw = f"{seed_str}{_PEPPER}{chunk_index}".encode("utf-8")
    return hashlib.sha256(raw).digest()


def _xor_bytes(data: bytes, seed_str: str) -> bytes:
    """XOR encrypt/decrypt (symmetric operation). Deterministic and reversible."""
    out         = bytearray()
    chunk_index = 0

    for offset in range(0, len(data), _CHUNK_SIZE):
        chunk    = data[offset : offset + _CHUNK_SIZE]
        key      = _derive_chunk_key(seed_str, chunk_index)
        
        # Extend key to match chunk length by repeating
        key_extended = (key * ((len(chunk) // len(key)) + 1))[:len(chunk)]
        
        # Pure Python XOR without NumPy
        xored = bytes(a ^ b for a, b in zip(chunk, key_extended))
        out.extend(xored)
        chunk_index += 1

    return bytes(out)



def derive_file_key(password: str, file_stem: str) -> str:
    """
    Derive encryption key specific to a file using password + file stem.
    This ensures different files have different keys, but same file always gets same key.
    """
    r1 = hash(password + file_stem)        # hashing.py
    r2 = the_actual_XOR_for_password(r1)   # XOR.py  (below)
    r3 = Convert2Base64(r2)                # Convertbase64.py
    r4 = convert2SHA256(r3)                # SHA256.py
    return r4


def derive_manifest_key(password: str) -> str:
    """Derive encryption key for the manifest using password only."""
    from hashing import hash
    from Convertbase64 import Convert2Base64
    from SHA256 import convert2SHA256

    r1 = hash(password)
    r2 = the_actual_XOR_for_password(r1)
    r3 = Convert2Base64(r2)
    r4 = convert2SHA256(r3)
    return r4

def encrypt_file_bytes(file_path: pathlib.Path, password: str) -> bytes:
    """Encrypt file contents using password-derived key."""
    key = derive_file_key(password, file_path.stem)
    with open(file_path, "rb") as fh:
        raw = fh.read()
    return _xor_bytes(raw, key)


def decrypt_file_bytes(encrypted_data: bytes, password: str, original_stem: str) -> bytes:
    """Decrypt file contents using original stem to regenerate correct key."""
    key = derive_file_key(password, original_stem)
    return _xor_bytes(encrypted_data, key)


def encrypt_manifest(data: bytes, password: str) -> bytes:
    """Encrypt the file name mapping manifest."""
    return _xor_bytes(data, derive_manifest_key(password))


def decrypt_manifest(data: bytes, password: str) -> bytes:
    """Decrypt the file name mapping manifest."""
    return _xor_bytes(data, derive_manifest_key(password))


def the_actual_XOR_for_password(user_input) -> bytes:
    """Apply XOR to password during key derivation chain for additional security."""
    if isinstance(user_input, str):
        raw = user_input.encode("utf-16-le")
    else:
        raw = bytes(user_input)

    return _xor_bytes(raw, raw.hex())


def the_actual_XOR(data, password: str) -> bytes:
    """Legacy entry point — routes to encrypt_file_bytes or encrypt_manifest."""
    if isinstance(data, (str, pathlib.Path)):
        return encrypt_file_bytes(pathlib.Path(data), password)
    return encrypt_manifest(bytes(data), password)


def generate_key(seed_str: str) -> str:
    """Legacy stub kept for import compatibility. Not used internally."""
    import random, string as _s
    random.seed(seed_str + _PEPPER)
    n = len(seed_str) * random.randint(10, 9999)
    return "".join(random.choices(
        _s.ascii_letters + _s.digits + _s.punctuation, k=n))