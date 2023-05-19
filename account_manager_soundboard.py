import json
import os

def create_account_settings(SOUNDBOARD_DATABASE, change_account=False):
    # Load the existing data from the account profile JSON file
    profile_data_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_profile_data.json")
    if os.path.exists(profile_data_file_path):
        with open(profile_data_file_path, 'r') as profile_file:
            database = json.load(profile_file)
    else:
        database = {}

    # Load the new account data from the account data JSON file
    account_data_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json")
    with open(account_data_file_path, 'r') as account_file:
        account_data = json.load(account_file)

    # Iterate through each Discord ID in the new account data
    for discord_id, account_info in account_data.items():
        # Check if the Discord ID already exists in the database
        if discord_id in database:
            if change_account:
                database[discord_id]["name"] = account_info.get('name')
            else:
                continue

        # Get the name from the new account data
        name = account_info.get('name')

        # Create account settings for the Discord ID
        account_settings = {
            'name': name,
            'permission_status': 'standard',
            'favorites': []
        }

        # Add the account settings to the database
        database[discord_id] = account_settings

    # Save the updated database to the JSON file
    with open(profile_data_file_path, 'w') as profile_file:
        json.dump(database, profile_file, indent=4)

def change_permission_status(name, permission_status, SOUNDBOARD_DATABASE):
    # Load the existing data from the JSON file
    profile_data_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_profile_data.json")
    with open(profile_data_file_path, 'r') as profile_file:
        database = json.load(profile_file)

    # Iterate through each Discord ID in the database
    for discord_id, account_settings in database.items():
        # Check if the name matches the account settings name
        if account_settings.get('name') == name:
            # Change the permission status
            account_settings['permission_status'] = permission_status

    # Save the updated database to the JSON file
    with open(profile_data_file_path, 'w') as profile_file:
        json.dump(database, profile_file, indent=4)

def get_permission_status(discord_id, SOUNDBOARD_DATABASE):
    # Load the data from the JSON file
    profile_data_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_profile_data.json")
    with open(profile_data_file_path, 'r') as profile_file:
        database = json.load(profile_file)

    # Check if the Discord ID exists in the database
    if str(discord_id) in database:
        # Retrieve the permission status
        account_settings = database[str(discord_id)]
        permission_status = account_settings.get('permission_status')
        return permission_status
    else:
        return None


