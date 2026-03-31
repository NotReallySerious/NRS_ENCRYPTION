import hashlib
import pathlib
import numpy as np

_PEPPER     = "NRS_VAULT_VERSION_1.0.0"
_CHUNK_SIZE = 4 * 1024 * 1024          # 4 MB per chunk

def _chunk_rng(seed_str: str, chunk_index: int) -> np.random.Generator:
    raw    = f"{seed_str}{_PEPPER}{chunk_index}".encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big"))


def _xor_bytes(data: bytes, seed_str: str) -> bytes:

    out         = bytearray()
    chunk_index = 0

    for offset in range(0, len(data), _CHUNK_SIZE):
        chunk    = data[offset : offset + _CHUNK_SIZE]
        key      = _chunk_rng(seed_str, chunk_index).integers(
                    0, 256, size=len(chunk), dtype=np.uint8)
        data_arr = np.frombuffer(chunk, dtype=np.uint8)
        out.extend((data_arr ^ key).tobytes())
        chunk_index += 1

    return bytes(out)

def the_actual_XOR(data, password: str) -> bytes:
    if isinstance(data, (str, pathlib.Path)):
        p = pathlib.Path(data)
        with open(p, "rb") as fh:
            raw = fh.read()
        seed = password + p.stem          # per-file uniqueness
    else:
        raw  = bytes(data)
        seed = password                   # blob / manifest

    return _xor_bytes(raw, seed)


def the_actual_XOR_for_password(user_input) -> bytes:
    if isinstance(user_input, str):
        raw  = user_input.encode("utf-16-le")
        seed = user_input
    else:
        raw  = bytes(user_input)
        seed = user_input.decode("utf-8", errors="replace")

    return _xor_bytes(raw, seed)


def generate_key(seed_str: str) -> str:
    import random, string as _s
    random.seed(seed_str + _PEPPER)
    n = len(seed_str) * random.randint(10, 9999)
    return "".join(random.choices(_s.ascii_letters + _s.digits + _s.punctuation, k=n))