import sqlite3
from Cryptodome.Cipher import AES
import struct
import logging

# Constants
ACCESS_KEY = b"\xe5m=\xeaw\x17\xe6L,\xde\xc8+]\x00\x00'"  # Example key, should be securely managed in production
DB_FILE = 'testshortened copy.db'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def bytes_to_float(data_bytes: bytes) -> float:
    return struct.unpack('d', data_bytes)[0]

def decrypt_data(access_key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> float:
    """
    Decrypts the encrypted float data using AES-GCM mode.
    
    Args:
        access_key (bytes): The AES key.
        nonce (bytes): The nonce used for encryption.
        ciphertext (bytes): The encrypted data.
        tag (bytes): The authentication tag.
        
    Returns:
        float: The decrypted float value.
    """
    try:
        logger.info(f"Nonce: {nonce}, Ciphertext: {ciphertext}, Tag: {tag}")
        cipher = AES.new(access_key, AES.MODE_GCM, nonce=nonce)
        decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        decrypted_value = bytes_to_float(decrypted_bytes)
        return decrypted_value
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise


def fetch_and_decrypt_entry_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT entry_id, axial_strain, vol_strain, excess_pwp, p, deviator_stress, void_ratio, shear_induced_pwp,
                   axial_strain_nonce, vol_strain_nonce, excess_pwp_nonce, p_nonce, deviator_stress_nonce, void_ratio_nonce, shear_induced_pwp_nonce,
                   axial_strain_tag, vol_strain_tag, excess_pwp_tag, p_tag, deviator_stress_tag, void_ratio_tag, shear_induced_pwp_tag
            FROM entry
        """)
        rows = cursor.fetchall()

        for row in rows:
            entry_id = row[0]
            encrypted_values = row[1:8]
            nonces = row[8:15]
            tags = row[15:22]
            logger.info(f"Decrypting data for entry_id {entry_id}")

            decrypted_values = []
            for i, ciphertext in enumerate(encrypted_values):
                try:
                    decrypted_value = decrypt_data(ACCESS_KEY, nonces[i], ciphertext, tags[i])
                    decrypted_values.append(decrypted_value)
                    logger.info(f"Decrypted field {i+1} for entry_id {entry_id}: {decrypted_value}")
                except Exception as e:
                    logger.error(f"Decryption error for field {i+1} of entry_id {entry_id}: {e}")
                    decrypted_values.append(None)  # Append None if decryption fails

            # After decrypting, update the database with the decrypted values
            cursor.execute("""
                UPDATE entry SET 
                    axial_strain = ?, vol_strain = ?, excess_pwp = ?, p = ?, deviator_stress = ?, void_ratio = ?, shear_induced_pwp = ?
                WHERE entry_id = ?
            """, (*decrypted_values, entry_id))

        # Commit the changes to the database after processing all rows
        conn.commit()
        logger.info("Decrypted data successfully updated in the database")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in fetch_and_decrypt_entry_data: {e}")
        raise
    finally:
        cursor.close()


def main():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        fetch_and_decrypt_entry_data(conn)
    except Exception as e:
        logger.error(f"Main function error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
