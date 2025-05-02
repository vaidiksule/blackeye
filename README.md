# BlackEye: A Python Blockchain Implementation

BlackEye is a basic blockchain implementation in Python, built from scratch for educational and experimental purposes. It includes essential blockchain components such as the genesis block, mining algorithm, proof-of-work, public/private key cryptography for client wallets, and basic transaction handling.

---

## 🚀 Features

- Genesis block creation
- SHA-256-based Proof-of-Work mining
- Blockchain validation
- Simple wallet generation using public/private keys (ECDSA)
- Basic peer-to-peer transaction model
- Block addition through mining

---

## 🛠 Installation & Setup

Make sure you have **Python 3.8+** installed. Follow these steps to set up the environment and run the project:

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/blackeye.git
cd blackeye
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

```bash
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🧠 How It Works
### 🔐 Wallets
Each user/client has a public/private key pair generated using ECDSA. The public key acts as the wallet address, and the private key is used to sign transactions securely.

### 📦 Genesis Block
The blockchain starts with a genesis block, the first block in the chain. It is hardcoded and acts as the foundation for all subsequent blocks.

### 🪙 Mining & Proof of Work
Each block requires a computational puzzle to be solved before it's added to the blockchain (Proof of Work). The difficulty level determines how complex this puzzle 

### 📦 Data Storage
- Wallets and blockchain data are saved in JSON format inside the data/ directory.
- You can inspect transaction history and balances manually if needed.

### 🔗 Blockchain'

Blocks contain:
-Index
-Timestamp
-List of transactions
-Previous block hash
-Nonce (for mining)

---

## ▶️ Running the Application
Locate the blockchain.py and run it to start the application.
```bash
python blockchain.py

```

You'll see logs for:
- Wallet key generation
- Block creation and mining
- Blockchain status
- Current hash

### 📂 Project Structure
```bash
blackeye/
├── Blockchain/
│ ├── Backend/
│ │ ├── core/
│ │ │ ├── database/
│ │ │ │ └── database.py # Block storage to disk
│ │ │ ├── EllepticCurve/ # ECC logic (key gen, signing)
│ │ │ ├── block.py # Block class
│ │ │ ├── blockchain.py # Main blockchain logic
│ │ │ ├── blockheader.py # Block header with mining logic
│ │ │ ├── Script.py # Transaction script evaluation
│ │ │ └── Tx.py # Transaction class and handling
│ │ └── util/ # Utility functions (hashing, merkle, etc.)
│ ├── client/
│ │ ├── account.py # Wallet/account creation
│ │ └── sendBEYE.py # Send BEYE tokens from wallet
│ └── Frontend/
│   ├── static/
│   │ └── css/
│   │   └── style.css # Basic styling
│   ├── templates/
│   │ └── wallet.html # HTML wallet interface
│   └── run.py # Launch Flask app
├── data/
│ ├── account/ # Wallet JSON files (public/private keys)
│ └── blockchain/ # Blockchain blocks stored as JSON
└── requirements.txt # Python dependencies
```


### 🧪 Notes
- This project is not production-ready.
- Intended for learning, prototyping, and blockchain experimentation.

### 📜 License
This project is open-source and available under the MIT License.


