from cryptography.fernet import Fernet
import requests
import os
# key = Fernet.generate_key()


def encrypt_data(plain_text: str) -> str:
    """
    Encrypts a plain text string.
    :param plain_text: The string to encrypt
    :return: Encrypted string
    """

    cipher_suite = Fernet(os.getenv('encryption_key'))
    
    encrypted_text = cipher_suite.encrypt(plain_text.encode('utf-8'))
    return encrypted_text.decode('utf-8')

def decrypt_data(encrypted_text: str) -> str:
    """
    Decrypts an encrypted string.
    :param encrypted_text: The string to decrypt
    :return: Decrypted string
    """
    
    cipher_suite = Fernet(os.getenv('encryption_key'))
    
    decrypted_text = cipher_suite.decrypt(encrypted_text.encode('utf-8'))
    return decrypted_text.decode('utf-8')

def split_string(value, prefix, max_length=64):
    """
    Splits a string into multiple parts if it exceeds the max_length.
    Returns a dictionary with split parts.
    """
    if len(value) <= max_length:
        return {prefix: value}
    
    split_parts = {}
    for i in range(0, len(value), max_length):
        split_parts[f"{prefix}_p{i // max_length + 1}"] = value[i:i + max_length]
    return split_parts
