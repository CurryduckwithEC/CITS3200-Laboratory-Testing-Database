import sqlite3
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import struct
import logging
from typing import Tuple, List

# Constants
ACCESS_KEY = b"\xe5m=\xeaw\x17\xe6L,\xde\xc8+]\x00\x00'"  # Example key, should be securely managed in production
DB_FILE = 'testshortened copy.db'
BATCH_SIZE = 100  # Number of rows to process before committing

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def float_to_bytes(data: float) -> bytes:
    return struct.pack('d', data)

def bytes_to_float(data_bytes: bytes) -> float:
    return struct.unpack('d', data_bytes)[0]

def encrypt_data(access_key: bytes, data: float) -> Tuple[bytes, bytes, bytes]:
    try:
        cipher = AES.new(access_key, AES.MODE_GCM)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(float_to_bytes(data))
        logger.debug(f"Data before encryption: {data}, Ciphertext: {ciphertext}")
        return nonce, ciphertext, tag
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise

def decrypt_data(access_key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> float:
    try:
        cipher = AES.new(access_key, AES.MODE_GCM, nonce=nonce)
        decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        decrypted_value = bytes_to_float(decrypted_bytes)
        logger.debug(f"Decrypted bytes: {decrypted_bytes}, Decrypted value (float): {decrypted_value}")
        return decrypted_value
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise

def fetch_and_encrypt_entry_data(conn: sqlite3.Connection):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT entry_id, axial_strain, vol_strain, excess_pwp, p, deviator_stress, void_ratio, shear_induced_pwp FROM entry")
        rows = cursor.fetchall()

        for i, row in enumerate(rows):
            entry_id, *values = row
            logger.info(f"Processing entry_id {entry_id}")

            encrypted_values = []
            nonces = []
            tags = []
            
            for value in values:
                nonce, ciphertext, tag = encrypt_data(ACCESS_KEY, value)
                encrypted_values.append(ciphertext)
                nonces.append(nonce)
                tags.append(tag)

            cursor.execute("""
                UPDATE entry SET 
                    axial_strain = ?, vol_strain = ?, excess_pwp = ?, p = ?, deviator_stress = ?, void_ratio = ?, shear_induced_pwp = ?,
                    axial_strain_nonce = ?, vol_strain_nonce = ?, excess_pwp_nonce = ?, p_nonce = ?, deviator_stress_nonce = ?, void_ratio_nonce = ?, shear_induced_pwp_nonce = ?,
                    axial_strain_tag = ?, vol_strain_tag = ?, excess_pwp_tag = ?, p_tag = ?, deviator_stress_tag = ?, void_ratio_tag = ?, shear_induced_pwp_tag = ?
                WHERE entry_id = ?
            """, (*encrypted_values, *nonces, *tags, entry_id))

            if (i + 1) % BATCH_SIZE == 0:
                conn.commit()
                logger.info(f"Committed batch of {BATCH_SIZE} rows")

        conn.commit()
        logger.info("All data encrypted and stored")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in fetch_and_encrypt_entry_data: {e}")
        raise
    finally:
        cursor.close()

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
                decrypted_value = decrypt_data(ACCESS_KEY, nonces[i], ciphertext, tags[i])
                decrypted_values.append(decrypted_value)

            logger.info(f"Decrypted data for entry_id {entry_id}: {decrypted_values}")
    except Exception as e:
        logger.error(f"Error in fetch_and_decrypt_entry_data: {e}")
        raise
    finally:
        cursor.close()

def main():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        fetch_and_encrypt_entry_data(conn)
        fetch_and_decrypt_entry_data(conn)
    except Exception as e:
        logger.error(f"Main function error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
