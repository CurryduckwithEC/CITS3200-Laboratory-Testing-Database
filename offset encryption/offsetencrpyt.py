import sqlite3
from Cryptodome.Cipher import AES
from hashlib import sha256
import struct
import random
import math
from typing import Tuple

# Constants
DB_FILE = 'test copy.db'
WORD_FOR_KEY = "apple"  # Example word for AES key generation
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

# Generate random parameters based on AES key
def generate_encryption_parameters(aes_key: bytes) -> tuple:
    random.seed(aes_key)
    amplitude = random.uniform(0.5, 2.0)
    frequency = random.uniform(0.1, 1.0)
    phase = random.uniform(0, 2 * math.pi)
    shift = random.uniform(-10, 10)
    return amplitude, frequency, phase, shift

# Encrypt data
def encrypt_data(value: float, amplitude: float, frequency: float, phase: float, shift: float) -> float:
    return round(value + amplitude * math.sin(frequency * value + phase) + shift, 6)

# Decrypt data
def decrypt_data(value: float, amplitude: float, frequency: float, phase: float, shift: float) -> float:
    # Use numerical method (Newton's method) to find the original value
    x = value - shift
    for _ in range(10):  # 10 iterations should be sufficient for convergence
        fx = x + amplitude * math.sin(frequency * x + phase) + shift - value
        dfx = 1 + amplitude * frequency * math.cos(frequency * x + phase)
        x = x - fx / dfx
    return round(x, 6)

# Function to apply encryption to float data in the entry table
def encrypt_entry_data(conn: sqlite3.Connection, aes_key: bytes):
    cursor = conn.cursor()
    
    # Generate parameters based on the AES key
    amplitude, frequency, phase, shift = generate_encryption_parameters(aes_key)
    
    try:
        cursor.execute("""
            SELECT entry_id, axial_strain, vol_strain, excess_pwp, p, deviator_stress, void_ratio, shear_induced_pwp 
            FROM entry
        """)
        rows = cursor.fetchall()

        for row in rows:
            entry_id = row[0]
            values = row[1:8]  # Selecting float columns from axial_strain to shear_induced_pwp
            
            encrypted_values = [encrypt_data(value, amplitude, frequency, phase, shift) for value in values]
            
            cursor.execute("""
                UPDATE entry 
                SET axial_strain = ?, vol_strain = ?, excess_pwp = ?, p = ?, deviator_stress = ?, void_ratio = ?, shear_induced_pwp = ?
                WHERE entry_id = ?
            """, (*encrypted_values, entry_id))

        conn.commit()
        print("Encryption applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error applying encryption: {e}")
    finally:
        cursor.close()

# Function to decrypt and print entry data
def decrypt_and_print_entry_data(conn: sqlite3.Connection, aes_key: bytes):
    cursor = conn.cursor()
    
    # Generate parameters based on the AES key
    amplitude, frequency, phase, shift = generate_encryption_parameters(aes_key)
    
    try:
        cursor.execute("""
            SELECT entry_id, axial_strain, vol_strain, excess_pwp, p, deviator_stress, void_ratio, shear_induced_pwp 
            FROM entry
        """)
        rows = cursor.fetchall()

        print("Decrypted Entry Data:")
        print("entry_id | axial_strain | vol_strain | excess_pwp | p | deviator_stress | void_ratio | shear_induced_pwp")
        print("-" * 100)

        for row in rows:
            entry_id = row[0]
            encrypted_values = row[1:8]
            
            decrypted_values = [decrypt_data(value, amplitude, frequency, phase, shift) for value in encrypted_values]
            
            print(f"{entry_id:8} | {' | '.join([f'{value:.6f}'.rjust(12) for value in decrypted_values])}")

    except Exception as e:
        print(f"Error decrypting and printing data: {e}")
    finally:
        cursor.close()

# Main function
def main():
    aes_key = word_to_aes_key(WORD_FOR_KEY, AES_KEY_SIZE)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        encrypt_entry_data(conn, aes_key)
        decrypt_and_print_entry_data(conn, aes_key)
    except Exception as e:
        print(f"Main function error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
