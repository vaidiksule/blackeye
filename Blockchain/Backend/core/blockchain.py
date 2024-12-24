import sys
# Adding a directory to the module search path for importing other modules
sys.path.append('/Coding/Python-Blockchain')

# Importing necessary modules and classes from the Blockchain package
from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256
from Blockchain.Backend.core.database.database import BlockchainDB
from Blockchain.Backend.core.Tx import CoinbaseTx
import time

# Constants used in the blockchain
ZERO_HASH = "0" * 64  # A string of 64 zeroes representing a hash of all zeros (used for the genesis block)
VERSION = 1  # Block version

class Blockchain:
    """
    Blockchain class manages the creation of new blocks in the blockchain, 
    handling the genesis block and adding new blocks to the chain.
    """
    def __init__(self):
        """
        Constructor for the Blockchain class.
        Initializes the blockchain by creating the Genesis block.
        """
        self.GenesisBlock()

    def write_on_disk(self, block):
        """
        Writes the given block to the database (disk).
        
        Parameters:
        block (dict): The block to be written to disk.
        """
        blockchainDB = BlockchainDB()  # Instantiate the BlockchainDB class to interact with the database
        blockchainDB.write(block)  # Write the block data to the database

    def fetch_last_block(self):
        """
        Fetches the last block from the blockchain.

        Returns:
        dict: The last block's data if it exists, otherwise None.
        """
        blockchainDB = BlockchainDB()  # Instantiate the BlockchainDB class
        return blockchainDB.lastBlock()  # Fetch the last block from the database

    def GenesisBlock(self):
        """
        Creates the first block in the blockchain (the Genesis block).
        """
        BlockHeight = 0  # The height of the Genesis block is always 0
        preBlockHash = ZERO_HASH  # The previous block hash is set to zero for the Genesis block
        self.addBlock(BlockHeight, preBlockHash)  # Add the Genesis block to the blockchain

    def addBlock(self, BlockHeight, prevBlockHash):
        """
        Adds a new block to the blockchain.
        
        Parameters:
        BlockHeight (int): The height of the block to be added (incremental from the last block).
        prevBlockHash (str): The hash of the previous block, which is required to maintain the chain.
        """
        timestamp = int(time.time())  # Current time in seconds since the epoch (timestamp for block creation)
        
        # Create a Coinbase transaction for the block (a special transaction to reward miners)
        coinbaseInstance = CoinbaseTx(BlockHeight)  # Instantiate CoinbaseTx for the current block height
        coinbaseTransaction = coinbaseInstance.CoinbaseTransaction()  # Generate the coinbase transaction
        
        merkleRoot = ' '  # Placeholder for the Merkle root (used for transaction validation, currently empty)
        bits = 'fff0001f'  # The target difficulty for mining (used in proof of work)
        
        # Create a block header with all necessary details
        blockheader = BlockHeader(VERSION, prevBlockHash, merkleRoot, timestamp, bits)
        
        # Start the mining process to find a valid hash for the block
        blockheader.mine()
        
        # Create the block using the block header and the coinbase transaction
        # The block height, size, header, transaction count, and transaction list are passed as arguments
        self.write_on_disk([Block(BlockHeight, 1, blockheader.__dict__, 1, coinbaseTransaction).__dict__])

    def main(self):
        """
        The main loop that continuously adds blocks to the blockchain.
        Fetches the last block, increments the block height, and uses the previous block's hash to add a new block.
        """
        while True:
            # Fetch the last block from the blockchain
            lastBlock = self.fetch_last_block()
            
            # If there is no last block, the loop cannot proceed. Ideally, handle this case with a break or raise an exception.
            if lastBlock is None:
                print("No previous block found.")
                break

            # Increment the block height by 1 based on the last block
            blockHeight = lastBlock["Height"] + 1
            
            # Fetch the hash of the last block's header to use as the previous block hash for the new block
            prevBlockHash = lastBlock["BlockHeader"]["blockHash"]
            
            # Add a new block to the blockchain using the new height and previous block's hash
            self.addBlock(blockHeight, prevBlockHash)


if __name__ == "__main__":
    """
    Entry point for the program. Instantiates the Blockchain class and starts the main loop.
    """
    blockchain = Blockchain()  # Create a new instance of the Blockchain class
    blockchain.main()  # Start the main loop to continuously add blocks
