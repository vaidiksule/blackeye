import hashlib
from Crypto.Hash import RIPEMD160
from hashlib import sha256
from math import log

from Blockchain.Backend.core.EllepticCurve.EllepticCurve import BASE58_ALPHABET

def hash256(s):
    """Perform two rounds of SHA256 hashing on the input bytes."""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def hash160(s):
    """Perform SHA256 followed by RIPEMD160 hashing on the input bytes."""
    return RIPEMD160.new(sha256(s).digest()).digest()

def int_to_little_endian(n, length):
    """
    Convert an integer to a little-endian byte sequence of the specified length.

    Parameters:
    n (int): The integer to convert.
    length (int): The length of the byte sequence.
    """
    return n.to_bytes(length, "little")

def bytes_needed(n):
    """
    Determine the number of bytes needed to represent an integer.

    Parameters:
    n (int): The integer to measure.

    Returns:
    int: The number of bytes needed.
    """
    if n == 0:
        return 1
    return int(log(n, 256)) + 1

def little_endian_to_int(b):
    """
    Convert a little-endian byte sequence to an integer.

    Parameters:
    b (bytes): The byte sequence to convert.

    Returns:
    int: The resulting integer.
    """
    return int.from_bytes(b, "little")

def decode_base58(address):
    """
    Decode a Base58 encoded address and check its checksum.

    Parameters:
    address (str): The Base58 encoded address.

    Returns:
    None: Raises an error if the address is invalid.
    """
    num = 0

    # Decode Base58 string to an integer
    for char in address:
        num *= 58
        num += BASE58_ALPHABET.index(char)

    # Convert the integer to a 25-byte sequence
    combined = num.to_bytes(25, byteorder="big")
    checksum = combined[-4:]

    # Verify the checksum
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError(f"bad Address {checksum} {hash256(combined[:-4][:4])}")

    return combined[1:-4]
