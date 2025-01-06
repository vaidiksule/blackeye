from Blockchain.Backend.util.util import decode_base58
from Blockchain.Backend.core.Script import Script
from Blockchain.Backend.core.Tx import TxIn, TxOut, Tx
from Blockchain.Backend.core.database.database import AccountDB
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import PrivateKey
import time

class SendBEYE:
    """
    Class to handle the creation and signing of a transaction to send BEYE cryptocurrency.
    It prepares inputs (UTXOs) and outputs, calculates fees, and signs the transaction.
    """
    def __init__(self, fromAccount, toAccount, Amount, UTXOS):
        """
        Initializes the SendBEYE instance with sender, receiver, amount, and UTXOs.

        Parameters:
        fromAccount (str): Public address of the sender.
        toAccount (str): Public address of the receiver.
        Amount (float): Amount of BEYE to send (in decimal, converted to satoshis).
        UTXOS (dict): Unspent Transaction Outputs available to the sender.
        """
        self.COIN = 100000000  # Conversion factor for BEYE to satoshis.
        self.FromPublicAddress = fromAccount
        self.toAccount = toAccount
        self.Amount = Amount * self.COIN  # Convert amount to satoshis.
        self.utxos = UTXOS

    def scriptPubKey(self, PublicAddress):
        """
        Generates the scriptPubKey (locking script) for the provided public address.

        Parameters:
        PublicAddress (str): Public address of the recipient.

        Returns:
        script_pubkey: The locking script for the address.
        """
        h160 = decode_base58(PublicAddress)  # Decode the Base58 address to a public hash.
        script_pubkey = Script().p2pkh_script(h160)  # Generate Pay-to-Public-Key-Hash script.
        return script_pubkey

    def getPrivateKey(self):
        """
        Retrieves the private key associated with the sender's public address from the account database.

        Returns:
        str: The private key of the sender.
        """
        AllAccounts = AccountDB().read()  # Read all accounts from the database.
        for account in AllAccounts:
            if account["PublicAddress"] == self.FromPublicAddress:
                return account["privateKey"]  # Return the private key if it matches the public address.

    def prepareTxIn(self):
        """
        Prepares the transaction inputs (UTXOs) for the sender.

        Returns:
        list: A list of transaction inputs.
        """
        TxIns = []  # List to store transaction inputs.
        self.Total = 0  # Total balance to be used.

        # Convert the sender's public address into a public hash to match UTXOs.
        self.From_address_script_pubkey = self.scriptPubKey(self.FromPublicAddress)
        self.fromPubKeyHash = self.From_address_script_pubkey.cmds[2]

        newutxos = {}

        # Convert managed dict to a normal dict (retry if not immediately available).
        try:
            while len(newutxos) < 1:
                newutxos = dict(self.utxos)
                time.sleep(2)
        except Exception as e:
            print(f"Error in converting the Managed Dict to Normal Dict")

        # Iterate over UTXOs to find matching outputs locked to the sender's address.
        for Txbyte in newutxos:
            if self.Total < self.Amount:  # Stop if total balance is sufficient.
                TxObj = newutxos[Txbyte]

                # Check each transaction output for a match with the sender's public key hash.
                for index, txout in enumerate(TxObj.tx_outs):
                    if txout.script_pubkey.cmds[2] == self.fromPubKeyHash:
                        self.Total += txout.amount  # Add the amount from the matching output.
                        prev_tx = bytes.fromhex(TxObj.id())  # Convert transaction ID to bytes.
                        TxIns.append(TxIn(prev_tx, index))  # Create a transaction input.
            else:
                break

        # Check if the sender has enough balance for the transaction.
        self.isBalanceEnough = True
        if self.Total < self.Amount:
            self.isBalanceEnough = False

        return TxIns

    def prepareTxOut(self):
        """
        Prepares the transaction outputs for the receiver and change.

        Returns:
        list: A list of transaction outputs.
        """
        TxOuts = []  # List to store transaction outputs.
        to_scriptPubkey = self.scriptPubKey(self.toAccount)  # Locking script for the receiver.
        TxOuts.append(TxOut(self.Amount, to_scriptPubkey))  # Add the amount to the receiver.

        # Calculate the transaction fee and change amount.
        self.fee = self.COIN  # Fixed transaction fee (1 BEYE).
        self.changeAmount = self.Total - self.Amount - self.fee  # Calculate change.
        TxOuts.append(TxOut(self.changeAmount, self.From_address_script_pubkey))  # Add change output.
        return TxOuts

    def signTx(self):
        """
        Signs the transaction inputs using the sender's private key.
        """
        secret = self.getPrivateKey()  # Retrieve the sender's private key.
        priv = PrivateKey(secret=secret)  # Create a PrivateKey object.

        # Sign each input with the private key.
        for index, input in enumerate(self.TxIns):
            self.TxObj.sign_input(index, priv, self.From_address_script_pubkey)

    def prepareTransaction(self):
        """
        Prepares and signs the transaction if the sender has enough balance.

        Returns:
        Tx or bool: A signed transaction object if successful, or False if insufficient balance.
        """
        self.TxIns = self.prepareTxIn()  # Prepare transaction inputs.

        if self.isBalanceEnough:
            self.TxOuts = self.prepareTxOut()  # Prepare transaction outputs.
            self.TxObj = Tx(1, self.TxIns, self.TxOuts, 0)  # Create the transaction object.
            self.TxObj.TxId = self.TxObj.id()  # Assign a unique transaction ID.
            self.signTx()  # Sign the transaction inputs.
            return self.TxObj  # Return the signed transaction.

        return False  # Return False if balance is insufficient.
