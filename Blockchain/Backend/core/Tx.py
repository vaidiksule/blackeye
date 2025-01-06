# Import necessary modules for handling scripts and utility functions.
from Blockchain.Backend.core.Script import Script
from Blockchain.Backend.util.util import (int_to_little_endian, 
    bytes_needed, decode_base58, little_endian_to_int, 
    encode_varint, hash256)

# Constants used in the coinbase transaction
ZERO_HASH = b'\0' * 32  # A hash of all zeroes (used for the previous transaction in a coinbase transaction)
REWARD = 50  # The reward given to miners for creating a new block

# A sample private key (this would typically be used for signing transactions but is not used in this code)
PRIVATE_KEY = '28098573616843794914490468776754733965400966030730111741462969690344809832748'

# The miner's address where the reward is sent
MINER_ADDRESS = '16DwL3KGZHXMM2fr8egKMhazsk2zvkXg58'
SIGHASH_ALL = 1

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
        # Convert the block height into little-endian format (as expected by transactions, used for signature)
        self.BlockHeightInLittleEndian = int_to_little_endian(BlockHeight, bytes_needed(BlockHeight))

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
        prev_index = 0xffffffff 

        # Creating the input (TxIn) for the coinbase transaction
        tx_ins = []
        tx_in = TxIn(prev_tx, prev_index)  # Create the TxIn object
        tx_ins.append(tx_in)  # Append the TxIn object
        tx_in.script_sig.cmds = [self.BlockHeightInLittleEndian]  # Directly modify the script_sig

        # Creating the output (TxOut) for the coinbase transaction
        tx_outs = []
        target_amount = REWARD * 100000000  # Reward for the miner, converted to satoshis (1 BTC = 100,000,000 satoshis)
        target_h160 = decode_base58(MINER_ADDRESS)  # Decode the miner's address into a 160-bit hash
        target_script = Script.p2pkh_script(target_h160)  # Generate the script for the public key hash of the miner's address
        tx_out = TxOut(amount=target_amount, script_pubkey=target_script)
        tx_outs.append(tx_out)  # Append the object itself, not its dictionary representation
        coinBaseTx =  Tx(1, tx_ins, tx_outs, 0)
        coinBaseTx.TxId =  coinBaseTx.id()
        # Return the constructed coinbase transaction
        return  coinBaseTx # Return the transaction with version 1, the inputs, and outputs

class Tx:
    """
    Represents a general transaction in the blockchain.
    This class handles the creation, serialization, and signing of a transaction.
    """
    def __init__(self, version, tx_ins, tx_outs, locktime):
        """
        Initializes a transaction with the given parameters.

        Parameters:
        version (int): The version of the transaction.
        tx_ins (list): The list of transaction inputs (TxIn objects).
        tx_outs (list): The list of transaction outputs (TxOut objects).
        locktime (int): The locktime for the transaction (unused here, set to 0).
        """
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime

    def id(self):
        """Returns a human-readable transaction ID."""
        return self.hash256().hex()

    def hash256(self):
        """Returns the hash of the serialized transaction (double SHA-256)."""
        return hash256(self.serialize())[::-1]

    def serialize(self):
        """
        Serializes the transaction into bytes format.

        Returns:
        bytes: The serialized transaction data.
        """
        result = int_to_little_endian(self.version, 4)
        
        # Serializing inputs
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()

        # Serializing outputs
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()

        result += int_to_little_endian(self.locktime, 4)

        return result
    
    def sigh_hash(self, input_index, script_pubkey):
        """
        Calculates the sighash (hash of the transaction data for signing).

        Parameters:
        input_index (int): The index of the input being signed.
        script_pubkey (Script): The public key script associated with the input.

        Returns:
        int: The sighash of the transaction.
        """
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.tx_ins))

        for i, tx_in in enumerate(self.tx_ins):
            if i == input_index:
                s += TxIn(tx_in.prev_tx, tx_in.prev_index, script_pubkey).serialize()
            else:
                s += TxIn(tx_in.prev_tx, tx_in.prev_index).serialize()

        s += encode_varint(len(self.tx_outs))

        for tx_out in self.tx_outs:
            s += tx_out.serialize()

        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)
        h256 = hash256(s)
        return int.from_bytes(h256, "big")

    def sign_input(self, input_index, private_key, script_pubkey):
        """
        Signs an input in the transaction.

        Parameters:
        input_index (int): The index of the input being signed.
        private_key (PrivateKey): The private key used to sign the input.
        script_pubkey (Script): The public key script of the input.
        """
        z = self.sigh_hash(input_index, script_pubkey)
        der = private_key.sign(z).der()
        sig = der + SIGHASH_ALL.to_bytes(1, "big")
        sec = private_key.point.sec()
        self.tx_ins[input_index].script_sig = Script([sig, sec])

    def verify_input(self, input_index, script_pubkey):
        """
        Verifies the signature of a transaction input.

        Parameters:
        input_index (int): The index of the input being verified.
        script_pubkey (Script): The public key script for the input.

        Returns:
        bool: True if the signature is valid, False otherwise.
        """
        tx_in = self.tx_ins[input_index]
        z = self.sigh_hash(input_index, script_pubkey)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)
    
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
        Converts the transaction to a dictionary format, with the inputs and outputs in a readable format.

        Returns:
        dict: The transaction represented as a dictionary.
        """
        for tx_index, tx_in in enumerate(self.tx_ins):
            if self.is_coinbase():
                tx_in.script_sig.cmds[0] = little_endian_to_int(
                    tx_in.script_sig.cmds[0]
                )

            tx_in.prev_tx = tx_in.prev_tx.hex()

            for index, cmd in enumerate(tx_in.script_sig.cmds):
                if isinstance(cmd, bytes):
                    tx_in.script_sig.cmds[index] = cmd.hex()

            tx_in.script_sig = tx_in.script_sig.__dict__
            self.tx_ins[tx_index] = tx_in.__dict__

        # Convert Transaction Output to dict
        for index, tx_out in enumerate(self.tx_outs):
            tx_out.script_pubkey.cmds[2] = tx_out.script_pubkey.cmds[2].hex()
            tx_out.script_pubkey = tx_out.script_pubkey.__dict__
            self.tx_outs[index] = tx_out.__dict__

        return self.__dict__

class TxIn:
    """
    Represents an input in a blockchain transaction.
    Contains the reference to the previous transaction, the index of the output,
    and the script signature (unlocking the output).
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
        self.script_sig = script_sig if script_sig else Script()
        self.sequence = sequence

    def serialize(self):
        """
        Serializes the transaction input into bytes format.

        Returns:
        bytes: The serialized input.
        """
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result
    
    def to_dict(self):
        """
        Converts the input into a dictionary format.

        Returns:
        dict: The input represented as a dictionary.
        """
        return {
            "prev_tx" : self.prev_tx.hex(),
            "prev_index": self.prev_index,
            "script_sig": self.script_sig.to_dict(),
            "sequence": self.sequence
        }

class TxOut:
    """
    Represents an output in a blockchain transaction.
    Contains the amount of currency and the script public key (locking the output).
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

    def serialize(self):
        """
        Serializes the transaction output into bytes format.

        Returns:
        bytes: The serialized output.
        """
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result
    
    def to_dict(self):
        """
        Converts the output into a dictionary format.

        Returns:
        dict: The output represented as a dictionary.
        """
        return { 
            "amount": self.amount, 
            "script_pubkey": self.script_pubkey.to_dict()
        }
