import json
import os
import dropbox

def update_json_list_for_app(access_token):
    directory = "audio_data_test_store"
    json_file = os.path.join(os.getcwd(), "soundboard_database", "audio_names.json")

    # Retrieve the names of MP3 files in the directory
    audio_names = [filename[:-4] for filename in os.listdir(directory) if filename.endswith(".mp3")]

    # Save the audio names as a JSON file
    with open(json_file, "w") as file:
        json.dump(audio_names, file)
        
    # Path to the JSON file on your local machine
    local_file_path = os.path.join(os.getcwd(), "soundboard_database", "audio_names.json")

    # Destination path on Dropbox where the file will be uploaded
    destination_path = '/audio_names.json' 

    # Create a Dropbox client
    dbx = dropbox.Dropbox(access_token)

    # Upload the file to Dropbox
    with open(local_file_path, 'rb') as file:
        dbx.files_upload(file.read(), destination_path, mode=dropbox.files.WriteMode.overwrite)

def update_json_list_for_account_info(access_token):

    # Path to the JSON file on your local machine
    local_file_path = os.path.join(os.getcwd(), "soundboard_database", "soundboard_account_profile_data.json")

    # Destination path on Dropbox where the file will be uploaded
    destination_path = '/soundboard_account_profile_data.json'

    # Create a Dropbox client
    dbx = dropbox.Dropbox(access_token)

    # Upload the file to Dropbox
    with open(local_file_path, 'rb') as file:
        dbx.files_upload(file.read(), destination_path, mode=dropbox.files.WriteMode.overwrite)