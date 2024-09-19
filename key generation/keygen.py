from hashlib import sha256
from Cryptodome.Cipher import AES
import os

# Generate an access key using SHA-256
def generate_access_key(input_value):
    return sha256(input_value.encode()).digest()

# Encrypt the data using AES and the access key
def encrypt_data(access_key, data):
    cipher = AES.new(access_key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return nonce, ciphertext, tag

# Decrypt the data using AES and the access key
def decrypt_data(access_key, nonce, ciphertext, tag):
    cipher = AES.new(access_key, AES.MODE_GCM, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data.decode()

# Example usage
unique_id = "device-or-user-specific-identifier"
data = "data"

# Step 1: Generate an access key
access_key = generate_access_key(unique_id)

# Step 2: Encrypt data using the generated key
nonce, ciphertext, tag = encrypt_data(access_key, data)
print("Encrypted:", ciphertext)

# Step 3: Decrypt the data using the same access key
decrypted_data = decrypt_data(access_key, nonce, ciphertext, tag)
print("Decrypted:", decrypted_data)
