import sys
# Adding a directory to the module search path for importing other modules
sys.path.append('/Source Code/blackeye')

# Importing necessary modules and classes from the Blockchain package
from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256, merkle_root, target_to_bits
from Blockchain.Backend.core.database.database import BlockchainDB
from Blockchain.Backend.core.Tx import CoinbaseTx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main
import time

# Constants used in the blockchain
ZERO_HASH = "0" * 64  # A string of 64 zeroes representing a hash of all zeros (used for the genesis block)
VERSION = 1  # Block version
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000

class Blockchain:
    """
    Blockchain class manages the creation of new blocks in the blockchain, 
    handling the genesis block and adding new blocks to the chain.
    """
    def __init__(self, utxos, MemPool):
        self.utxos = utxos
        self. MemPool = MemPool
        self.current_target = INITIAL_TARGET
        self.bits = target_to_bits(INITIAL_TARGET)

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

    def store_uxtos_in_cache(self):
        for tx in self.addTransactionsInBlock:
            print(f"Transaction added {tx.TxId} ")
            self.utxos[tx.TxId] = tx

    def remove_spent_Transactions(self):
        for txId_index in self.remove_spent_transactions:
            if txId_index[0].hex() in self.utxos:

                if len(self.utxos[txId_index[0].hex()].tx_outs) < 2:
                    print(f" Spent Transaction removed {txId_index[0].hex()} ")
                    del self.utxos[txId_index[0].hex()]
                else:
                    prev_trans = self.utxos[txId_index[0].hex()]
                    self.utxos[txId_index[0].hex()] = prev_trans.tx_outs.pop(
                        txId_index[1]
                    )


    """ Read Transactions from Memory Pool"""

    def read_transaction_from_memorypool(self):
        self.Blocksize = 80
        self.TxIds = []
        self.addTransactionsInBlock = []
        self.remove_spent_transactions = []

        for tx in self.MemPool:
            self.TxIds.append(bytes.fromhex(tx))
            self.addTransactionsInBlock.append(self.MemPool[tx])
            self.Blocksize += len(self.MemPool[tx].serialize())

            for spent in self.MemPool[tx].tx_ins:
                self.remove_spent_transactions.append([spent.prev_tx, spent.prev_index])

    def remove_transactions_from_memorypool(self):
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                del self.MemPool[tx.hex()]

    def convert_to_json(self):
        self.TxJson = []
        for tx in self.addTransactionsInBlock:
            self.TxJson.append(tx.to_dict())

    def calculate_fee(self):
        self.input_amount = 0
        self.output_amount = 0
        """ Calculate Input Amount """
        for TxId_index in self.remove_spent_transactions:
            if TxId_index[0].hex() in self.utxos:
                self.input_amount += (
                    self.utxos[TxId_index[0].hex()].tx_outs[TxId_index[1]].amount
                )

        """ Calculate Output Amount """
        for tx in self.addTransactionsInBlock:
            for tx_out in tx.tx_outs:
                self.output_amount += tx_out.amount

        self.fee = self.input_amount - self.output_amount

    def addBlock(self, BlockHeight, prevBlockHash):
        """
        Adds a new block to the blockchain.
        
        Parameters:
        BlockHeight (int): The height of the block to be added (incremental from the last block).
        prevBlockHash (str): The hash of the previous block, which is required to maintain the chain.
        """
        self.read_transaction_from_memorypool()
        self.calculate_fee()
        timestamp = int(time.time())
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTransaction = coinbaseInstance.CoinbaseTransaction()
        self.Blocksize += len(coinbaseTransaction.serialize())

        coinbaseTransaction.tx_outs[0].amount = coinbaseTransaction.tx_outs[0].amount + self.fee

        self.TxIds.insert(0, bytes.fromhex(coinbaseTransaction.id()))
        self.addTransactionsInBlock.insert(0, coinbaseTransaction)

        merkleRoot = merkle_root(self.TxIds)[::-1].hex()

        blockheader = BlockHeader(
            VERSION, prevBlockHash, merkleRoot, timestamp, self.bits
        )
        blockheader.mine(self.current_target)
        self.remove_spent_Transactions()
        self.remove_transactions_from_memorypool()
        self.store_uxtos_in_cache()
        self.convert_to_json()

        print(f"Block {BlockHeight} is mined with nonce value of {blockheader.nonce}")
        
        block = Block(BlockHeight, self.Blocksize, blockheader.__dict__, 1, self.TxJson).__dict__
        self.write_on_disk([block])

    def main(self):
        """
        The main loop that continuously adds blocks to the blockchain.
        Fetches the last block, increments the block height, and uses the previous block's hash to add a new block.
        """
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.GenesisBlock()

        while True:
            # Fetch the last block from the blockchain
            lastBlock = self.fetch_last_block()

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
    with Manager() as manager:
        utxos = manager.dict()
        MemPool = manager.dict()

        webapp = Process(target = main, args= (utxos, MemPool))
        webapp.start()
        blockchain = Blockchain(utxos, MemPool)  # Create a new instance of the Blockchain class
        blockchain.main()  # Start the main loop to continuously add blocks
