from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

# Generate random bytes for AES key
key = get_random_bytes(16)
print(f"AES key: {key}")