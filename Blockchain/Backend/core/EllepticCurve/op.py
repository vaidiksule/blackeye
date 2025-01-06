from Blockchain.Backend.util.util import hash160
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import Sha256Point, Signature

# Function for OP_DUP operation: Duplicates the top item of the stack
def op_dup(stack):
    if len(stack) < 1:  # Check if the stack has less than 1 item
        return False  # Return False if the stack is empty
    stack.append(stack[-1])  # Duplicate the top item by appending it again
    return True  # Successfully duplicated the item

# Function for OP_HASH160 operation: Performs hash160 on the top item of the stack
def op_hash160(stack):
    if len(stack) < 1:  # Ensure the stack has at least one element
        return False  # Return False if the stack is empty
    element = stack.pop()  # Pop the top element
    h160 = hash160(element)  # Apply hash160 (RIPEMD-160 after SHA-256)
    stack.append(h160)  # Push the result of hash160 back onto the stack
    return True  # Successfully hashed and pushed the result

# Function for OP_EQUAL operation: Compares the top two items on the stack
def op_equal(stack):
    if len(stack) < 2:  # Ensure the stack has at least two elements
        return False  # Return False if not enough elements
    element1 = stack.pop()  # Pop the first element
    element2 = stack.pop()  # Pop the second element
    if element1 == element2:  # Check if both elements are equal
        stack.append(1)  # Push 1 onto the stack if equal
    else:
        stack.append(0)  # Push 0 onto the stack if not equal
    return True  # Successfully compared the elements

# Function for OP_VERIFY operation: Verifies if the top item on the stack is non-zero
def op_verify(stack):
    if len(stack) < 1:  # Check if the stack has at least one item
        return False  # Return False if the stack is empty
    element = stack.pop()  # Pop the top element
    if element == 0:  # If the element is 0, the verification fails
        return False
    return True  # Return True if the element is non-zero (valid)

# Function for OP_EQUALVERIFY operation: Checks for equality and verifies the result
def op_equalverify(stack):
    return op_equal(stack) and op_verify(stack)  # First checks equality, then verifies the result

# Function for OP_CHECKSIG operation: Verifies a signature using a public key and a hash (z)
def op_checksig(stack, z):
    if len(stack) < 1:  # Ensure the stack has at least one element
        return False  # Return False if the stack is empty
    sec_pubkey = stack.pop()  # Pop the public key from the stack
    der_signature = stack.pop()[:-1]  # Pop the signature and remove the last byte (for DER format)

    try:
        # Parse the public key and signature using elliptic curve cryptography
        point = Sha256Point.parse(sec_pubkey)
        sig = Signature.parse(der_signature)
    except Exception as e:
        return False  # Return False if there is an error parsing the key or signature

    # Verify the signature against the hash (z) and public key
    if point.verify(z, sig):
        stack.append(1)  # Push 1 onto the stack if the signature is valid
        return True
    else:
        stack.append(0)  # Push 0 onto the stack if the signature is invalid
        return False

# Dictionary mapping OP_CODE to their respective function
OP_CODE_FUNCTION = {
    118: op_dup,        # OP_DUP
    136: op_equalverify,  # OP_EQUALVERIFY
    169: op_hash160,     # OP_HASH160
    172: op_checksig,    # OP_CHECKSIG
}
