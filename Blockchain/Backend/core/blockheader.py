from Blockchain.Backend.util.util import hash256

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

    def mine(self):
        # Keep mining until the block hash starts with '0000'
        while (self.blockHash[0:4]) != '0000':  
            # Concatenate the block attributes (version, prevBlockHash, merkleRoot, timestamp, bits, nonce)
            # and encode it to bytes before hashing. This forms the unique input for the mining process.
            block_data = (str(self.version) + self.prevBlockHash + self.merkleRoot + 
                        str(self.timestamp) + str(self.bits) + str(self.nonce)).encode()
            
            # Perform a double SHA-256 hash and convert the result to a hexadecimal string
            # This produces the block hash that will be checked to see if it satisfies the difficulty target.
            self.blockHash = hash256(block_data).hex()
            
            # Increment the nonce to try the next possible block hash in the next iteration
            self.nonce += 1
            
            # Print the current mining progress (show the current nonce) on the same line
            # The '\r' at the end allows us to overwrite the previous output in the terminal.
            print(f"mining started {self.nonce}", end='\r')

