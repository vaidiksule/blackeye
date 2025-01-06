# Importing utility functions and operations for working with scripts and elliptic curve operations
from Blockchain.Backend.util.util import int_to_little_endian, encode_varint
from Blockchain.Backend.core.EllepticCurve.op import OP_CODE_FUNCTION

class Script:
    """
    The Script class represents a script in Bitcoin-like systems. A script is essentially a list of operations 
    and data that define how a transaction can be spent. Scripts are evaluated in a stack-based manner.
    
    This class allows you to work with these scripts by serializing them, converting them to a dictionary,
    and creating specific types of scripts like Pay-to-PubKey-Hash (P2PKH).
    """
    def __init__(self, cmds=None):
        """
        Initializes a Script instance with a list of commands (opcodes and data).
        
        Parameters:
        cmds (list): A list of commands (opcodes and data) to include in the script. If no cmds are provided, 
                     an empty list will be initialized.
        
        Example:
        cmds = [0x76, 0xA9, h160, 0x88, 0xAC]  # Example script for P2PKH
        """
        if cmds is None:
            self.cmds = []  # If no commands are provided, initialize an empty list
        else:
            self.cmds = cmds  # Otherwise, use the provided list of commands
    
    def __add__(self, other):
        return Script(self.cmds + other.cmds)

    def evaluate(self, z):
        cmds = self.cmds[:]
        stack = []

        while len(cmds) > 0:
            cmd = cmds.pop(0)

            if type(cmd) == int:
                operation = OP_CODE_FUNCTION[cmd]

                if cmd == 172:
                    if not operation(stack, z):
                        print(f"Error in Signature Verification")
                        return False

                elif not operation(stack):
                    print(f"Error in Signature Verification")
                    return False
            else:
                stack.append(cmd)
        return True

    def serialize(self):
        """
        Serializes the script into a byte format that can be used in Bitcoin transactions.
        
        The serialization process involves converting the script's commands (both opcodes and data) into 
        a compact binary format suitable for inclusion in a transaction. This includes encoding lengths 
        of data elements and the overall script.
        
        Returns:
        bytes: A serialized byte string representing the script.
        
        Example:
        script = Script([0x76, 0xA9, h160, 0x88, 0xAC])
        serialized_script = script.serialize()
        """
        result = b""  # Initialize an empty byte string to build the result
        
        for cmd in self.cmds:
            # if the cmd is an integer, it's an opcode
            if type(cmd) == int:
                # Convert the cmd (opcode) into a little-endian byte representation
                result += int_to_little_endian(cmd, 1)
            else:
                # Otherwise, this is an element (data)
                length = len(cmd)  # Get the length of the data
                # Handle data lengths based on specific ranges (e.g., less than 75, between 75 and 0x100, etc.)
                if length < 75:
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    result += int_to_little_endian(76, 1)  # Pushdata1 opcode
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    result += int_to_little_endian(77, 1)  # Pushdata2 opcode
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError("Too long a cmd")
                result += cmd  # Append the actual data

        # Serialize the total length of the script and prepend it to the result
        total = len(result)
        return encode_varint(total) + result  # Use varint encoding for the total length and return the full serialized script

    def to_dict(self):
        """
        Converts the script into a dictionary representation.
        
        The dictionary can be useful for debugging or for interacting with APIs that expect JSON-like structures.
        
        Returns:
        dict: A dictionary representing the script with commands in hex format if they are bytes.
        
        Example:
        script = Script([0x76, 0xA9, h160, 0x88, 0xAC])
        script_dict = script.to_dict()
        """
        return {"cmds": [cmd.hex() if isinstance(cmd, bytes) else cmd for cmd in self.cmds]}  # Convert each command to hex if it's a byte

    @classmethod
    def p2pkh_script(cls, h160):
        """
        Creates a Pay-to-PubKey-Hash (P2PKH) ScriptPubKey.
        
        A P2PKH script locks the output to a specific public key hash. It is one of the most commonly used 
        script types in Bitcoin transactions. A P2PKH script is unlocked by providing a signature and 
        the public key corresponding to the specified public key hash.
        
        Parameters:
        h160 (bytes): A 160-bit public key hash (RIPEMD-160(SHA-256(PublicKey)))
        
        Returns:
        Script: A Script object representing the P2PKH ScriptPubKey. The returned Script object contains 
                the necessary opcodes and public key hash to lock a transaction output.
        
        Example:
        h160 = b'\x89\xAB\xCD\xEF...'  # Public key hash
        p2pkh = Script.p2pkh_script(h160)
        """
        return Script([0x76, 0xA9, h160, 0x88, 0xAC])  # Return a Script object with the P2PKH byte sequence
