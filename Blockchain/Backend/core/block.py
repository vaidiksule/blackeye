class Block:
    """
    Block is a storage container that stores transactions.
    """

    def __init__(self, Height, Blocksize, BlockHeader, TxCount, Txs):
        """
        Initialize a new Block.
        
        Parameters:
        Height (int): The height of the block in the blockchain.
        Blocksize (int): The size of the block in bytes.
        BlockHeader (str): The header information(metadata) of the block.
        TxCount (int): The number of transactions included in the block.
        Txs (list): The list of transactions contained in the block.
        """
        self.Height = Height  # The height of the block in the blockchain.
        self.Blocksize = Blocksize  # The size of the block in bytes.
        self.BlockHeader = BlockHeader  # The information of the block.
        self.Txcount = TxCount  # The number of transactions included in the block.
        self.Txs = Txs  # The list of transactions contained in the block.


