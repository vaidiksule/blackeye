from Blockchain.Backend.util.util import (
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    int_to_little_endian,
)

class BlockHeader:
    """
    BlockHeader represents the header of a block in the blockchain.
    It contains metadata and methods to mine the block.
    """
    def __init__(self, version, prevBlockHash, merkleRoot, timestamp, bits):
        """
        Initialize a new BlockHeader.

        Parameters:
        version (int): The version of the block.
        prevBlockHash (str): The hash of the previous block.
        merkleRoot (str): The Merkle root of the block's transactions.
        timestamp (int): The time at which the block is created.
        bits (bytes): The target threshold for the block's hash.
        """
        self.version = version  # The version of the block.
        self.prevBlockHash = prevBlockHash  # The hash of the previous block.
        self.merkleRoot = merkleRoot  # The Merkle root of the block's transactions.
        self.timestamp = timestamp  # The time at which the block is created.
        self.bits = bits  # The target threshold for the block's hash.
        self.nonce = 0  # The nonce used for mining.
        self.blockHash = ""  # The resulting hash of the block.

    def mine(self, target):
        self.blockHash = target + 1

        while self.blockHash > target:
            self.blockHash = little_endian_to_int(
                hash256(
                    int_to_little_endian(self.version, 4)
                    + bytes.fromhex(self.prevBlockHash)[::-1]
                    + bytes.fromhex(self.merkleRoot)
                    + int_to_little_endian(self.timestamp, 4)
                    + self.bits
                    + int_to_little_endian(self.nonce, 4)
                )
            )
            self.nonce += 1
            print(f"Mining Started {self.nonce}", end="\r")
        self.blockHash = int_to_little_endian(self.blockHash, 32).hex()[::-1]
        self.bits = self.bits.hex()
