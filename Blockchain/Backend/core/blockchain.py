import os
import sys
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from a .env file

# Get the blockchain path from environment variables
blockchain_path = os.getenv("BLOCKCHAIN_PATH")
sys.path.append(blockchain_path)  # Add the blockchain path to the Python path so modules can be imported

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
ZERO_HASH = "0" * 64  # Genesis block's previous hash is a string of 64 zeroes
VERSION = 1  # Block version number
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000  # Difficulty target for mining

class Blockchain:
    """
    Blockchain class manages the creation and addition of blocks to the chain,
    including the genesis block and handling UTXOs and transactions.
    """
    def __init__(self, utxos, MemPool):
        self.utxos = utxos  # Dictionary of unspent transaction outputs
        self.MemPool = MemPool  # Memory pool containing pending transactions
        self.current_target = INITIAL_TARGET  # Set the current difficulty target
        self.bits = target_to_bits(INITIAL_TARGET)  # Convert difficulty target to compact bits format

    def write_on_disk(self, block):
        """
        Writes a block to the persistent database.
        """
        blockchainDB = BlockchainDB()  # Instantiate database interface
        blockchainDB.write(block)  # Write the block to disk

    def fetch_last_block(self):
        """
        Retrieves the most recent block from the blockchain database.
        """
        blockchainDB = BlockchainDB()
        return blockchainDB.lastBlock()

    def GenesisBlock(self):
        """
        Creates the very first block in the blockchain with height 0.
        """
        BlockHeight = 0
        preBlockHash = ZERO_HASH
        self.addBlock(BlockHeight, preBlockHash)

    def store_uxtos_in_cache(self):
        """
        Adds the transaction outputs of the new block to the UTXO cache.
        """
        for tx in self.addTransactionsInBlock:
            print(f"Transaction added {tx.TxId} ")
            self.utxos[tx.TxId] = tx

    def remove_spent_Transactions(self):
        """
        Removes the spent transaction outputs from the UTXO cache.
        """
        for txId_index in self.remove_spent_transactions:
            if txId_index[0].hex() in self.utxos:
                if len(self.utxos[txId_index[0].hex()].tx_outs) < 2:
                    print(f" Spent Transaction removed {txId_index[0].hex()} ")
                    del self.utxos[txId_index[0].hex()]
                else:
                    prev_trans = self.utxos[txId_index[0].hex()]
                    self.utxos[txId_index[0].hex()] = prev_trans.tx_outs.pop(txId_index[1])

    def read_transaction_from_memorypool(self):
        """
        Reads all pending transactions from the memory pool and prepares them for inclusion in the block.
        """
        self.Blocksize = 80  # Initial block size (header size)
        self.TxIds = []  # List of transaction IDs
        self.addTransactionsInBlock = []  # List of transaction objects to include
        self.remove_spent_transactions = []  # Track which inputs have been spent

        for tx in self.MemPool:
            self.TxIds.append(bytes.fromhex(tx))
            self.addTransactionsInBlock.append(self.MemPool[tx])
            self.Blocksize += len(self.MemPool[tx].serialize())  # Accumulate block size

            for spent in self.MemPool[tx].tx_ins:
                self.remove_spent_transactions.append([spent.prev_tx, spent.prev_index])

    def remove_transactions_from_memorypool(self):
        """
        Removes transactions that were included in the block from the memory pool.
        """
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                del self.MemPool[tx.hex()]

    def convert_to_json(self):
        """
        Converts the transactions in the block to JSON format for storage.
        """
        self.TxJson = []
        for tx in self.addTransactionsInBlock:
            self.TxJson.append(tx.to_dict())

    def calculate_fee(self):
        """
        Calculates the total transaction fee by comparing input and output amounts.
        """
        self.input_amount = 0
        self.output_amount = 0

        # Sum of all input amounts
        for TxId_index in self.remove_spent_transactions:
            if TxId_index[0].hex() in self.utxos:
                self.input_amount += (
                    self.utxos[TxId_index[0].hex()].tx_outs[TxId_index[1]].amount
                )

        # Sum of all output amounts
        for tx in self.addTransactionsInBlock:
            for tx_out in tx.tx_outs:
                self.output_amount += tx_out.amount

        self.fee = self.input_amount - self.output_amount  # Total fee earned by miner

    def addBlock(self, BlockHeight, prevBlockHash):
        """
        Constructs and adds a new block to the blockchain.
        """
        self.read_transaction_from_memorypool()
        self.calculate_fee()
        timestamp = int(time.time())  # Get current UNIX timestamp

        # Create the coinbase transaction and adjust the reward
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTransaction = coinbaseInstance.CoinbaseTransaction()
        self.Blocksize += len(coinbaseTransaction.serialize())
        coinbaseTransaction.tx_outs[0].amount += self.fee  # Add fees to miner reward

        # Add coinbase transaction at the beginning of the block
        self.TxIds.insert(0, bytes.fromhex(coinbaseTransaction.id()))
        self.addTransactionsInBlock.insert(0, coinbaseTransaction)

        # Calculate the merkle root
        merkleRoot = merkle_root(self.TxIds)[::-1].hex()

        # Create and mine the block header
        blockheader = BlockHeader(
            VERSION, prevBlockHash, merkleRoot, timestamp, self.bits
        )
        blockheader.mine(self.current_target)

        # Update the UTXO set and clean up the memory pool
        self.remove_spent_Transactions()
        self.remove_transactions_from_memorypool()
        self.store_uxtos_in_cache()
        self.convert_to_json()

        print(f"Block {BlockHeight} is mined with nonce value of {blockheader.nonce}")
        
        # Construct the full block
        block = Block(
            BlockHeight,
            self.Blocksize,
            blockheader.__dict__,
            1,  # Tx count or version
            self.TxJson
        ).__dict__

        self.write_on_disk([block])  # Save the block

    def main(self):
        """
        Main loop to continuously generate and append blocks to the chain.
        """
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.GenesisBlock()

        while True:
            lastBlock = self.fetch_last_block()
            blockHeight = lastBlock["Height"] + 1
            prevBlockHash = lastBlock["BlockHeader"]["blockHash"]
            self.addBlock(blockHeight, prevBlockHash)

# Entry point for execution
if __name__ == "__main__":
    with Manager() as manager:
        utxos = manager.dict()  # Shared memory dictionary for UTXOs
        MemPool = manager.dict()  # Shared memory dictionary for pending transactions

        # Launch web application in a separate process
        webapp = Process(target=main, args=(utxos, MemPool))
        webapp.start()

        # Start the blockchain node
        blockchain = Blockchain(utxos, MemPool)
        blockchain.main()
