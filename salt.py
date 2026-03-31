import random
import string

_CHARS   = string.ascii_letters
_DIGITS  = string.digits
_SPECIAL = string.punctuation
_ALL     = _CHARS + _DIGITS + _SPECIAL


def key(x: str) -> list:
    rng      = random.Random()          
    key_size = len(x)

    return [
        f"{rng.choice(_CHARS)}{rng.choice(_DIGITS)}{rng.choice(_SPECIAL)}"
        for _ in range(key_size)
    ]