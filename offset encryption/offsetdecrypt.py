import sqlite3
import random
from hashlib import sha256

# Constants
DB_FILE = 'test copy.db'
WORD_FOR_KEY = "apple"  # Same word used for AES key generation in encryption
AES_KEY_SIZE = 256  # Key size (128, 192, or 256 bits)

# Generate AES key from word
def word_to_aes_key(word: str, key_size: int = 256) -> bytes:
    if key_size not in [128, 192, 256]:
        raise ValueError("Invalid key size. Choose from 128, 192, or 256 bits.")
    
    word_bytes = word.encode('utf-8')
    hash_bytes = sha256(word_bytes).digest()
    
    if key_size == 128:
        return hash_bytes[:16]
    elif key_size == 192:
        return hash_bytes[:24]
    elif key_size == 256:
        return hash_bytes

# Generate random linear function coefficients based on AES key (same as in encryption)
def generate_linear_function_coefficients(aes_key: bytes) -> tuple:
    random.seed(aes_key)
    a = random.uniform(0.5, 2.0)  # Same range as encryption
    b = random.uniform(-10, 10)   # Same range as encryption
    return a, b

# Reverse linear function to decrypt the data
def reverse_offset_data(encrypted_value: float, a: float, b: float) -> float:
    return (encrypted_value - b) / a

# Function to apply decryption (reverse offset) to float data in the entry table
def reverse_offset_for_entry_data(conn: sqlite3.Connection, aes_key: bytes):
    cursor = conn.cursor()
    
    # Generate coefficients based on the AES key (same as encryption)
    a, b = generate_linear_function_coefficients(aes_key)
    
    try:
        cursor.execute("""
            SELECT entry_id, axial_strain, vol_strain, excess_pwp, p, deviator_stress, void_ratio, shear_induced_pwp 
            FROM entry
        """)
        rows = cursor.fetchall()

        for row in rows:
            entry_id = row[0]
            encrypted_values = row[1:8]  # Selecting the encrypted float columns from axial_strain to shear_induced_pwp
            
            # Decrypt the values by reversing the linear transformation
            decrypted_values = [reverse_offset_data(value, a, b) for value in encrypted_values]
            
            cursor.execute("""
                UPDATE entry 
                SET axial_strain = ?, vol_strain = ?, excess_pwp = ?, p = ?, deviator_stress = ?, void_ratio = ?, shear_induced_pwp = ?
                WHERE entry_id = ?
            """, (*decrypted_values, entry_id))

        conn.commit()
        print("Offsets reversed (decrypted) successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error reversing offsets: {e}")
    finally:
        cursor.close()

# Main function
def main():
    aes_key = word_to_aes_key(WORD_FOR_KEY, AES_KEY_SIZE)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        reverse_offset_for_entry_data(conn, aes_key)
    except Exception as e:
        print(f"Main function error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
