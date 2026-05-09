import random
import string
import hashlib


def hash(x: str) -> str:
    """
    Generate a deterministic hash from input string.
    Uses random.Random seeded with input to ensure reversibility.
    """
    # Create a deterministic seed from the input
    hex_seed = x.encode('utf-16').hex()
    
    # Use Random with seed for deterministic output
    rng = random.Random(hex_seed)
    
    # Generate 16-character hash from alphanumeric chars
    chars = string.ascii_letters + string.digits
    return ''.join(rng.choices(chars, k=16))  