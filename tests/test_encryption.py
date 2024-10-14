import sqlite3
from Cryptodome.Cipher import AES
from hashlib import sha256
import struct
import random
import math
from typing import Tuple



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


# Encrypt data
def encrypt_data_new(value: float, amplitude: float, frequency: float, phase: float, shift: float) -> float:
    return round(value + amplitude * math.sin(frequency * value + phase) + shift * value, 6)

def decrypt_data_new(value: float, amplitude: float, frequency: float, phase: float, shift: float) -> float:
    # Initial guess for the original value
    x = value / (1 + shift)  # A rough estimate for initial guess
    for _ in range(10):  # 10 iterations for convergence
        dynamic_shift = shift * x
        fx = x + amplitude * math.sin(frequency * x + phase) + dynamic_shift - value
        dfx = 1 + amplitude * frequency * math.cos(frequency * x + phase) + shift
        x = x - fx / dfx
    return round(x, 6)
    

def test(key, values):

    aeskey = word_to_aes_key(key)
    amp, freq, phase, shift = generate_encryption_parameters(aeskey)

    print("Using key:", key)
    print("Original:\tEnc:\tDec:\t")
    for i in values:
        enc_value = encrypt_data_new(i, amp, freq, phase, shift)
        dec_value = decrypt_data_new(enc_value, amp, freq, phase, shift)

        print(f"{i}\t{enc_value}\t{dec_value}")
    print("")
        

# Sample test code

key1 = "map"
values1 = [0.001, 0.01, 0.1, 1, 10, 100, 1000]

key2 = "cat"
values2 = [0.005, 0.05, 0.5, 5, 50, 500, 5000]

test(key1, values1)
test(key2, values2)