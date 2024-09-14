from cryptography.fernet import Fernet

def generate_key(secret_key):
    return Fernet.generate_key() + secret_key.encode()

def encrypt_data(key, data):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt_data(key, encrypted_data):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data
