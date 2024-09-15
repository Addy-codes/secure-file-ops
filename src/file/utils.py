from cryptography.fernet import Fernet

def generate_key(secret_key):
    """
    Generate a new encryption key by combining a generated key with a secret key.

    Args:
        secret_key (str): The secret key to be combined with the generated key.

    Returns:
        bytes: The combined encryption key.
    """
    return Fernet.generate_key() + secret_key.encode()

def encrypt_data(key, data):
    """
    Encrypt data using the provided encryption key.

    Args:
        key (bytes): The encryption key.
        data (str): The data to be encrypted.

    Returns:
        bytes: The encrypted data.
    """
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt_data(key, encrypted_data):
    """
    Decrypt data using the provided encryption key.

    Args:
        key (bytes): The encryption key.
        encrypted_data (bytes): The data to be decrypted.

    Returns:
        str: The decrypted data.
    """
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data
