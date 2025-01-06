import hashlib
from Crypto.Hash import RIPEMD160
from hashlib import sha256
from math import log

from Blockchain.Backend.core.EllepticCurve.EllepticCurve import BASE58_ALPHABET

# Perform two rounds of SHA256 hashing on the input bytes.
def hash256(s):
    """ 
    Hash the input using SHA256 twice.
    
    This is commonly used in blockchain to produce a secure hash.
    First, it applies SHA256 on the input, and then SHA256 is applied again on the result.
    
    Parameters:
    s (bytes): The input data to hash.

    Returns:
    bytes: The resulting hash after two rounds of SHA256.
    """
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

# Perform SHA256 followed by RIPEMD160 hashing on the input bytes.
def hash160(s):
    """ 
    Hash the input using SHA256 followed by RIPEMD160.
    
    This is commonly used for creating Bitcoin-style addresses.
    The first hashing with SHA256 is done, followed by a second hashing using RIPEMD160.
    
    Parameters:
    s (bytes): The input data to hash.

    Returns:
    bytes: The resulting hash after applying SHA256 followed by RIPEMD160.
    """
    return RIPEMD160.new(sha256(s).digest()).digest()

# Convert an integer to a little-endian byte sequence of the specified length.
def int_to_little_endian(n, length):
    """
    Convert an integer to a little-endian byte sequence of the specified length.
    
    Little-endian means the least significant byte is stored first.
    
    Parameters:
    n (int): The integer to convert.
    length (int): The length of the byte sequence.

    Returns:
    bytes: The little-endian byte sequence representing the integer.
    """
    return n.to_bytes(length, "little")

# Determine the number of bytes needed to represent an integer.
def bytes_needed(n):
    """ 
    Calculate the number of bytes needed to represent the given integer n.
    
    Parameters:
    n (int): The integer whose byte size is to be determined.
    
    Returns:
    int: The number of bytes required to represent n.
    """
    if n == 0:
        return 1
    return int(log(n, 256)) + 1

# Convert a little-endian byte sequence to an integer.
def little_endian_to_int(b):
    """
    Convert a little-endian byte sequence to an integer.
    
    Little-endian means the least significant byte comes first. This function reverses
    that byte order to convert it to an integer.
    
    Parameters:
    b (bytes): The little-endian byte sequence to convert.
    
    Returns:
    int: The resulting integer from the byte sequence.
    """
    return int.from_bytes(b, "little")

# Decode a Base58 encoded address and check its checksum.
def decode_base58(address):
    """
    Decode a Base58 encoded address and check its checksum.
    
    Base58 is a commonly used encoding in Bitcoin and other cryptocurrencies to make addresses 
    more user-friendly. This function decodes the address and verifies its integrity by checking the checksum.
    
    Parameters:
    address (str): The Base58 encoded address to decode.
    
    Returns:
    bytes: The decoded bytes after removing the version byte and checksum.
    Raises ValueError if the address is invalid.
    """
    num = 0

    # Decode Base58 string to an integer.
    for char in address:
        num *= 58
        num += BASE58_ALPHABET.index(char)

    # Convert the integer to a 25-byte sequence (with the version and checksum).
    combined = num.to_bytes(25, byteorder= 'big')
    checksum = combined[-4:]

    # Verify the checksum.
    # The checksum is the first 4 bytes of the hash256 of the address (without the checksum).
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError(f"Bad Address {checksum} {hash256(combined[:-4][:4])}.")

    # Return the decoded address, which is the 20-byte payload (excluding version and checksum).
    return combined[1:-4]

# Encodes an integer into a variable-length integer format, which is used for encoding sizes in blockchain protocols.
def encode_varint(i):
    """ 
    Encodes an integer as a varint (variable-length integer).
    
    Varints are used in blockchain protocols to encode integer values with an optimized size.
    The function encodes the integer into one or more bytes depending on its size.

    Parameters:
    i (int): The integer to encode.

    Returns:
    bytes: The encoded variable-length integer.
    """
    if i < 0xFD:
        return bytes([i])  # Single byte encoding for values less than 0xFD
    elif i < 0x10000:
        return b"\xfd" + int_to_little_endian(i, 2)  # Encoding with 2 bytes for values less than 0x10000
    elif i < 0x100000000:
        return b"\xfe" + int_to_little_endian(i, 4)  # Encoding with 4 bytes for values less than 0x100000000
    elif i < 0x10000000000000000:
        return b"\xff" + int_to_little_endian(i, 8)  # Encoding with 8 bytes for larger values
    else:
        raise ValueError("Integer too large: {}".format(i))  # Raise error for values that cannot be encoded

def merkle_parent_level(hashes):
    """takes a list of binary hashes and returns a list that's half of the length"""

    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])

    parent_level = []

    for i in range(0, len(hashes), 2):
        parent = hash256(hashes[i] + hashes[i + 1])
        parent_level.append(parent)
    return parent_level


def merkle_root(hashes):
    """Takes a list of binary hashes and return the merkle root"""
    current_level = hashes

    while len(current_level) > 1:
        current_level = merkle_parent_level(current_level)

    return current_level[0]


def target_to_bits(target):
    """Turns a target integer back into bits"""
    raw_bytes = target.to_bytes(32, "big")
    raw_bytes = raw_bytes.lstrip(b"\x00")  # <1>
    if raw_bytes[0] > 0x7F:  # <2>
        exponent = len(raw_bytes) + 1
        coefficient = b"\x00" + raw_bytes[:2]
    else:
        exponent = len(raw_bytes)  # <3>
        coefficient = raw_bytes[:3]  # <4>
    new_bits = coefficient[::-1] + bytes([exponent])  # <5>
    return new_bits