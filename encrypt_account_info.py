from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import json


def get_key(SERVER_CONFIG_FILE):
    with open(SERVER_CONFIG_FILE, 'r') as file:
        server_api_data = json.load(file)

    # Update the key in the JSON data
    return server_api_data["enc_key"]

def generate_key(SERVER_CONFIG_FILE):
    """Generate a random AES-256 key."""
    # Generate a random key
    key = get_random_bytes(32)

    with open(SERVER_CONFIG_FILE, 'r') as file:
        server_api_data = json.load(file)

    # Update the key in the JSON data
    server_api_data["enc_key"] = key.hex()

    # Save the updated JSON data to the file
    with open(SERVER_CONFIG_FILE, 'w') as file:
        json.dump(server_api_data, file, indent=4)

def encrypt(data, key):
    """Encrypt the given data using AES-256."""
    key = bytes.fromhex(key)
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = _pad_data(data)
    encrypted_data = iv + cipher.encrypt(padded_data.encode())
    return encrypted_data

def decrypt(encrypted_data, key):
    """Decrypt the given encrypted data using AES-256."""
    key = bytes.fromhex(key)
    iv = encrypted_data[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_data[AES.block_size:]).decode()
    unpadded_data = _unpad_data(decrypted_data)
    return unpadded_data

def _pad_data(data):
    """Pad the given data to match the block size."""
    block_size = AES.block_size
    pad_size = block_size - (len(data) % block_size)
    padded_data = data + chr(pad_size) * pad_size
    return padded_data

def _unpad_data(data):
    """Remove the padding from the given data."""
    pad_size = ord(data[-1])
    unpadded_data = data[:-pad_size]
    return unpadded_data

def save_encrypt_account_data(SOUNDBOARD_DATABASE):
    account_data_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json")

    key = get_key()

    # Read the JSON file
    with open(account_data_file_path) as file:
        data = file.read()

    # Encrypt the data
    encrypted_data = encrypt(data, key)

    # Save the encrypted data to a file
    with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data_encrypt.bin"), 'wb') as file:
        file.write(encrypted_data)

def load_encrypt_account_data(SOUNDBOARD_DATABASE):
    # Read the encrypted data from the file
    with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data_encrypt.bin"), 'rb') as file:
        encrypted_data = file.read()

    key = get_key()

    # Decrypt the data
    decrypted_data = decrypt(encrypted_data, key)

    # Convert the decrypted data to JSON
    account_data = json.loads(decrypted_data)

    # Save the decrypted JSON data to a file
    with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data_decrypt.json"), 'w') as file:
        json.dump(account_data, file, indent=4)
