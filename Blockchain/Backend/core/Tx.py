# Import necessary modules for handling Bitcoin scripts and utility functions.
from Blockchain.Backend.core.Script import Script
from Blockchain.Backend.util.util import int_to_little_endian, bytes_needed, decode_base58, little_endian_to_int

# Constants used in the coinbase transaction
ZERO_HASH = b'\0' * 32  # A hash of all zeroes (used for the previous transaction in a coinbase transaction)
REWARD = 50  # The reward given to miners for creating a new block (in bitcoins)

# A sample private key (this would typically be used for signing transactions but is not used in this code)
PREIVATE_KEY = '69104275339346012321509628518060309105808373833167498880180456747310225564096'

# The miner's address where the reward is sent
MINER_ADDRESS = '13W597B4FRM4MccU8ki68bceYyRaxdGba2'

class CoinbaseTx:
    """
    The CoinbaseTx class creates a coinbase transaction, which is the first transaction in a block.
    This type of transaction is used to reward the miner who successfully mined the block.
    It contains no inputs (except a special "coinbase" input), and the output sends the reward to a miner's address.
    """
    def __init__(self, BlockHeight):
        """
        Initializes the Coinbase transaction with the block height.
        
        Parameters:
        BlockHeight (int): The height of the block (used in the script signature of the coinbase transaction).
        """
        # Convert the block height into little-endian format (as expected by Bitcoin transactions)
        self.BlochHeightInLittleEndian = int_to_little_endian(BlockHeight, bytes_needed(BlockHeight))

    def CoinbaseTransaction(self):
        """
        Creates the coinbase transaction, which includes:
        1. A special input with prev_tx set to zero hash.
        2. A script signature containing the block height (in little-endian format).
        3. A single output that sends the reward to the miner's address.

        Returns:
        Tx: The fully constructed coinbase transaction.
        """
        prev_tx = ZERO_HASH  # The previous transaction hash (zero hash for the first transaction)
        prev_index = 0  # The previous index (usually 0 for a coinbase transaction)

        # Creating the input (TxIn) for the coinbase transaction
        tx_ins = []
        tx_ins.append(TxIn(prev_tx, prev_index))  # Adding an input with zero hash and index 0

        # The script signature contains the block height (in little-endian format)
        tx_ins[0].script_sig.cmds.append(self.BlochHeightInLittleEndian)  # Add the block height to the input's script_sig

        # Creating the output (TxOut) for the coinbase transaction
        tx_outs = []
        target_amount = REWARD * 100000000  # Reward for the miner, converted to satoshis (1 BTC = 100,000,000 satoshis)
        target_h160 = decode_base58(MINER_ADDRESS)  # Decode the miner's address into a 160-bit hash
        target_script = Script.p2pkh_script(target_h160)  # Generate the script for the public key hash of the miner's address
        tx_outs.append(TxOut(amount=target_amount, script_pubkey=target_script))  # Add the output with the reward and script

        # Return the constructed coinbase transaction
        return Tx(1, tx_ins, tx_outs, 0)  # Return the transaction with version 1, the inputs, and outputs

class Tx:
    """
    Represents a general transaction in the blockchain.
    """
    def __init__(self, version, tx_ins, tx_outs, locktime):
        """
        Initializes a transaction with the given parameters.

        Parameters:
        version (int): The version of the transaction.
        tx_ins (list): The list of transaction inputs.
        tx_outs (list): The list of transaction outputs.
        locktime (int): The locktime for the transaction (unused here, set to 0).
        """
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime

    def is_coinbase(self):
        """
        Checks if the transaction is a coinbase transaction.

        Returns:
        bool: True if the transaction is a coinbase, False otherwise.
        """
        # A coinbase transaction must have exactly 1 input
        if len(self.tx_ins) != 1:
            return False

        first_input = self.tx_ins[0]

        # The previous transaction hash of the coinbase input must be a zero hash
        if first_input.prev_tx != b"\x00" * 32:
            return False

        # The previous index of the coinbase input must be 0xffffffff (indicating it's a coinbase)
        if first_input.prev_index != 0xffffffff:
            return False

        return True

    def to_dict(self):
        """
        Converts the transaction to a dictionary for easier serialization or display.

        Returns:
        dict: The transaction converted to a dictionary format.
        """
        if self.is_coinbase():
            # Convert the previous transaction hash to hex and the block height to an integer
            self.tx_ins[0].prev_tx = self.tx_ins[0].prev_tx.hex()
            self.tx_ins[0].script_sig.cmds[0] = little_endian_to_int(self.tx_ins[0].script_sig.cmds[0])
            self.tx_ins[0].script_sig = self.tx_ins[0].script_sig.__dict__  # Convert the script_sig to a dict
            
        self.tx_ins[0] = self.tx_ins[0].__dict__  # Convert the tx_in to a dict

        # Convert the transaction outputs to a dictionary
        self.tx_outs[0].script_pubkey.cmds[2] = self.tx_outs[0].script_pubkey.cmds[2].hex()  # Convert the script_pubkey to hex
        self.tx_outs[0].script_pubkey = self.tx_outs[0].script_pubkey.__dict__  # Convert the script_pubkey to a dict
        self.tx_outs[0] = self.tx_outs[0].__dict__  # Convert the tx_out to a dict

        return self.__dict__  # Return the transaction as a dictionary

class TxIn:
    """
    Represents an input in a transaction.
    """
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        """
        Initializes a transaction input.

        Parameters:
        prev_tx (bytes): The previous transaction's hash.
        prev_index (int): The index of the output in the previous transaction.
        script_sig (Script): The script signature (optional).
        sequence (int): The sequence number (defaults to 0xffffffff).
        """
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()  # Initialize an empty script if none is provided
        else:
            self.script_sig = script_sig
        self.sequence = sequence

class TxOut:
    """
    Represents an output in a transaction.
    """
    def __init__(self, amount, script_pubkey):
        """
        Initializes a transaction output.

        Parameters:
        amount (int): The amount to be sent in satoshis.
        script_pubkey (Script): The public key script that locks the output.
        """
        self.amount = amount
        self.script_pubkey = script_pubkey
