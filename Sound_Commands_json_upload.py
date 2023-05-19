import json
import os
import dropbox


def update_json_list_for_app(access_token, SOUND_DIRECTORY, SOUNDBOARD_DATABASE):
    json_file = os.path.join(os.getcwd(), SOUND_DIRECTORY, "audio_names.json")

    # Retrieve the names of MP3 files in the directory
    audio_names = [filename[:-4] for filename in os.listdir(SOUND_DIRECTORY) if filename.endswith(".mp3")]

    # Save the audio names as a JSON file
    with open(json_file, "w") as file:
        json.dump(audio_names, file)
        
    # Path to the JSON file on your local machine
    local_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "audio_names.json")

    # Destination path on Dropbox where the file will be uploaded
    destination_path = '/audio_names.json' 

    # Create a Dropbox client
    dbx = dropbox.Dropbox(access_token)

    # Upload the file to Dropbox
    with open(local_file_path, 'rb') as file:
        dbx.files_upload(file.read(), destination_path, mode=dropbox.files.WriteMode.overwrite)

def update_json_list_for_account_info(access_token, SOUNDBOARD_DATABASE):

    # Path to the JSON file on your local machine
    local_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_profile_data.json")

    # Destination path on Dropbox where the file will be uploaded
    destination_path = '/soundboard_account_profile_data.json'

    # Create a Dropbox client
    dbx = dropbox.Dropbox(access_token)

    # Upload the file to Dropbox
    with open(local_file_path, 'rb') as file:
        dbx.files_upload(file.read(), destination_path, mode=dropbox.files.WriteMode.overwrite)

def upload_encrypted_account_info(access_token, SOUNDBOARD_DATABASE):
    from encrypt_account_info import save_encrypt_account_data
    save_encrypt_account_data()

    # Path to the JSON file on your local machine
    local_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data_encrypt.bin")

    # Destination path on Dropbox where the file will be uploaded
    destination_path = '/soundboard_account_data_encrypt.bin'

    # Create a Dropbox client
    dbx = dropbox.Dropbox(access_token)

    # Upload the file to Dropbox
    with open(local_file_path, 'rb') as file:
        dbx.files_upload(file.read(), destination_path, mode=dropbox.files.WriteMode.overwrite)

def download_encrypted_account_info(access_token, SOUNDBOARD_DATABASE):
    from encrypt_account_info import load_encrypt_account_data

    save_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data_decrypt.bin")

    # Destination path on Dropbox to download the file
    source_path = '/soundboard_account_data_encrypt.bin'

    # Create a Dropbox client
    dbx = dropbox.Dropbox(access_token)

    # Download the file from Dropbox
    dbx.files_download_to_file(save_file_path, source_path)
    load_encrypt_account_data()



# with open('server_api_keys.json', 'r') as file:
#     server_api_data = json.load(file)

# upload_encrypted_account_info(server_api_data["dropbox_access_token"], SOUNDBOARD_DATABASE)

# download_encrypted_account_info(server_api_data["dropbox_access_token"], SOUNDBOARD_DATABASE)
