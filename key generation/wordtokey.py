from hashlib import sha256
from Cryptodome.Cipher import AES

def word_to_aes_key(word: str, key_size: int = 256) -> bytes:
    """
    Converts a word (string) into an AES key of the specified size.
    
    Args:
        word (str): The word to convert into an AES key.
        key_size (int): The desired AES key size in bits (128, 192, or 256). Defaults to 256 bits.
        
    Returns:
        bytes: A valid AES key of the specified size.
        
    Raises:
        ValueError: If an invalid key size is provided.
    """
    # Ensure valid key size (128, 192, or 256 bits)
    if key_size not in [128, 192, 256]:
        raise ValueError("Invalid key size. Choose from 128, 192, or 256 bits.")
    
    # Convert the word to bytes (UTF-8 encoding)
    word_bytes = word.encode('utf-8')
    
    # Hash the word using SHA-256
    hash_bytes = sha256(word_bytes).digest()
    
    # Select the correct number of bytes for the AES key based on the desired key size
    if key_size == 128:
        return hash_bytes[:16]  # Use the first 16 bytes for a 128-bit key
    elif key_size == 192:
        return hash_bytes[:24]  # Use the first 24 bytes for a 192-bit key
    elif key_size == 256:
        return hash_bytes  # Use the full 32 bytes for a 256-bit key

# Example usage
word = "apple"
aes_key = word_to_aes_key(word, key_size=256)
print(f"AES Key (256-bit): {aes_key.hex()}")
