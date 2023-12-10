import os
from dotenv import load_dotenv

import bcrypt

load_dotenv()

SALT_ROUNDS = int(os.getenv('SALT_ROUNDS'))
GLOBAL_PEPPER = os.getenv('GLOBAL_PEPPER')


def create_user_password(password):
    """
    Creates a hashed password from the given password.
    :param password:
    :return:
    """
    pepper_password = password.encode() + GLOBAL_PEPPER.encode('utf-8')
    salt = bcrypt.gensalt(SALT_ROUNDS)

    return bcrypt.hashpw(pepper_password, salt).decode(), salt.decode()


def check_user_password(password_attempt, stored_hash, stored_salt):
    """
    Checks the given password attempt against the stored hash.
    :param password_attempt: The password attempt as a string.
    :param stored_hash: The stored hash as a string.
    :param stored_salt: The stored salt as a string.
    :return: True if the password attempt is correct, False otherwise.
    """
    # Pepper the password attempt
    peppered_password_attempt = password_attempt.encode() + GLOBAL_PEPPER.encode('utf-8')

    # Re-encode the stored hash and salt as they were decoded when stored
    stored_hash = stored_hash.encode()
    stored_salt = stored_salt.encode()

    # Hash the peppered password attempt with the stored salt
    hash_attempt = bcrypt.hashpw(peppered_password_attempt, stored_salt)

    # print(hash_attempt, stored_hash)
    # Compare the hash attempt to the stored hash
    return stored_hash == hash_attempt


def create_reset_token():
    pass

