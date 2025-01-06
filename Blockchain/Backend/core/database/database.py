import os
import json

class BaseDB:
    """
    BaseDB provides a simple file-based database functionality.
    It allows reading and writing JSON data to a file, making it reusable
    for other classes needing persistent storage.
    """
    def __init__(self, filename):
        """
        Initializes the BaseDB instance.
        Ensures the 'data' directory exists and sets the path to the specified filename.
        
        Parameters:
        filename (str): The name of the file to be used for storing data.
        """
        self.basepath = 'data'  # The directory where the data will be stored.
        os.makedirs(self.basepath, exist_ok=True)  # Ensure the base directory exists (creates if not).
        self.filepath = os.path.join(self.basepath, filename)  # Set the path to the file where data is stored.
        
    def read(self):
        """
        Reads the data from the specified file and returns it as a Python object (list or dict).
        
        Returns:
        list or bool: The data read from the file, or False if the file does not exist or cannot be read.
        """
        if not os.path.exists(self.filepath):  # Check if the file exists
            print(f"File {self.filepath} not available")  # Print an error message if the file is not found
            return False  # Return False to indicate failure

        with open(self.filepath, 'r') as file:  # Open the file for reading
            raw = file.read()  # Read the first line (assuming the whole data fits on one line)
            if raw:  # If there is data in the file
                try:
                    data = json.loads(raw)  # Try to parse the raw data into a Python object (list/dict)
                except json.JSONDecodeError as e:  # Handle JSON parsing errors
                    print(f"Error reading JSON data: {e}")  # Print an error message if JSON is invalid
                    data = []  # If parsing fails, return an empty list
            else:
                data = []  # If the file is empty, return an empty list
            return data  # Return the parsed data

    def write(self, item):
        """
        Writes data to the specified file. If the data is not a list, it converts it into one.
        
        Parameters:
        item (any): The data to be written. It will be wrapped in a list if not already a list.
        """
        # Ensure the item is always a list
        if not isinstance(item, list):
            item = [item]  # If not already a list, convert the item into a list.

        # Read the existing data from the file 
        data = self.read()  # Fetch the existing data

        # Append the new data to the existing data
        # data.extend(item)  # Add the new item(s) to the existing data
        if data:
            data = data + item
        else:
            data = item
            
        # Write the combined data back to the file
        with open(self.filepath, 'w') as file:  # Open the file for writing
            try:
                file.write(json.dumps(data, indent=4))  # Serialize the data to JSON with indentation for readability
            except TypeError as e:  # Catch any error that occurs during serialization
                print(f"Error serializing data: {e}")  # Print an error message if serialization fails

class BlockchainDB(BaseDB):
    """
    BlockchainDB is a specialized database for storing blockchain data.
    It inherits from BaseDB to reuse the reading and writing functionality
    and adds methods specific to blockchain management.
    """
    def __init__(self):
        """
        Initializes the BlockchainDB instance, specifically for the blockchain data file.
        Calls the parent class constructor with the filename 'blockchain.json'.
        """
        filename = 'blockchain'  # The file that stores blockchain data
        super().__init__(filename)  # Call the parent class constructor with the filename

    def lastBlock(self):
        """
        Retrieves the last block from the blockchain data stored in the file.
        
        Returns:
        dict or None: The last block's data if available, or None if no data exists.
        """
        data = self.read()  # Read the blockchain data from the file
        if data:  # If data exists
            return data[-1]  # Return the last block (most recent entry)
        return None  # If no data exists, return None
            
class AccountDB(BaseDB):
    """
    AccountDB is a specialized database for storing account-related data.
    It inherits from BaseDB and uses a specific filename for account data.
    """
    def __init__(self):
        """
        Initializes the AccountDB instance, specifically for the account data file.
        Calls the parent class constructor with the filename 'account'.
        """
        self.filename = "account"  # The file that stores account data
        super().__init__(self.filename)  # Call the parent class constructor with the filename
