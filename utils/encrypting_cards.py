from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from os import urandom

# This function generates a random key for encryption
def generate_key(password: str, salt: bytes = None) -> bytes:
    if not salt:
        salt = urandom(16)  # Generate a new salt

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = kdf.derive(password.encode())
    return key, salt

# This function encrypts the card data
def encrypt(data: str, key: bytes) -> (bytes, bytes, bytes):
    gcm_mode = modes.GCM(urandom(12))  # Create GCM mode object
    cipher = Cipher(algorithms.AES(key), gcm_mode, backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data.encode()) + encryptor.finalize()

    return (gcm_mode.nonce, ct, encryptor.tag)  # Access nonce from gcm_mode


# This function decrypts the card data
def decrypt(nonce: bytes, ciphertext: bytes, tag: bytes, key: bytes) -> str:
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# Example:
password = "your_super_secure_password"  # This should be kept securely
key, salt = generate_key(password)

# Encrypt card data
nonce, ciphertext, tag = encrypt("1234123412341234", key)

# Decrypt card data
decrypted_data = decrypt(nonce, ciphertext, tag, key)
print(decrypted_data.decode())
