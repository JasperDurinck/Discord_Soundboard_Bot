import discord
from discord.ext import commands
import asyncio
import os
import subprocess
import functools
from pydub import AudioSegment
import shutil
from pytube import YouTube
import json
from Sound_Commands_json_upload import update_json_list_for_app, update_json_list_for_account_info
from account_manager_soundboard import create_account_settings, get_permission_status
from discord.ui import View, Button, Item
from datetime import datetime

# Read the JSON file
with open('server_config.json') as file:
    server_api_data = json.load(file)

#settings
max_length_seconds = int(server_api_data['max_length_seconds']) #max length sounds

# Access the values
channel_connect_ID = int(server_api_data['channel_connect_ID'])
webhookbot_id = server_api_data['webhookbot_id']
server_id = server_api_data['server_id']
discord_bot_token = server_api_data['discord_bot_token']
dropbox_access_token = server_api_data['dropbox_access_token']
dropbox_sounds_list_link_key = server_api_data['dropbox_sounds_list_link_key']

# Access the directories
CURRENT_CLIENT_DIRECTORY = server_api_data['CURRENT_CLIENT_DIRECTORY']
SOUND_DIRECTORY = server_api_data['SOUND_DIRECTORY']
SOUND_ORIGINAL_DIRECTORY = server_api_data['SOUND_ORIGINAL_DIRECTORY']
SOUNDBOARD_DATABASE = server_api_data['SOUNDBOARD_DATABASE']

DIRECOTRY_LIST = [CURRENT_CLIENT_DIRECTORY, SOUND_DIRECTORY, SOUND_ORIGINAL_DIRECTORY, SOUNDBOARD_DATABASE]

for DIRECOTRY in DIRECOTRY_LIST:
    # Check if the directories exist, and create them if they don't
    if not os.path.exists(os.path.join(os.getcwd(), DIRECOTRY)):
        os.mkdir(os.path.join(os.getcwd(), DIRECOTRY))

SOUND_FILES = {}

for filename in os.listdir(SOUND_DIRECTORY):
    if filename.endswith(".mp3"):
        name = os.path.splitext(filename)[0]
        SOUND_FILES[name] = name

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("*"),
    description='Relatively simple music bot example',
    intents=intents,)

# Load the data from the JSON file
with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json"), 'r') as file: 
    data = json.load(file)

# Set up event listeners for when the bot connects to the Discord server
#run
class MyView(discord.ui.View):
    def __init__(self, ctx, bot):
        super().__init__()
        self.ctx = ctx
        self.bot = bot

        for sound_file, label in SOUND_FILES.items():
            button = discord.ui.Button(label=label, emoji="🔊", custom_id=sound_file)
            button.callback = functools.partial(self.button_callback, button)  # remove the call here
            self.add_item(button)

        stop_button = discord.ui.Button(emoji="🔴", custom_id="stop")
        stop_button.callback = self.stop_button_callback
        self.add_item(stop_button)

    async def interaction_check(self, interaction: discord.Interaction):
        # Check if the user who clicked the button is in the same voice channel as the bot
        if self.ctx.author.voice and self.ctx.author.voice.channel == self.ctx.voice_client.channel:
            return True
        else:
            await interaction.response.send_message("You must be in the same voice channel as the bot to use this button.", ephemeral=True)
            return False

    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        sound_file = button.custom_id
        print(sound_file)
        voice_client = self.ctx.voice_client

        if voice_client is None:
            await self.ctx.invoke(self.bot.get_command('join'))

        message = interaction.message
        self.ctx: commands.Context = await self.bot.get_context(message)
        await self.ctx.invoke(self.bot.get_command('play'), sound_file)
        

    async def stop_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        voice_client = self.ctx.voice_client
        if voice_client:
            voice_client.stop()

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')
    channel = bot.get_channel(channel_connect_ID)
    vc = await channel.connect()

def parse_client_input(input_str):
    # Split the input string by the "-client_name" separator
    parts = input_str.split("-client_name", 1)

    # Extract the command and command arguments
    command_str = parts[0].strip()

    # Extract the login information (if present)
    if len(parts) > 1:
        client_info = parts[1].strip()
    else:
        client_info = None

    return command_str, client_info

def check_login(login_info, data):
    # Extract the client name and password from the login information
    client_name = None
    client_password = None

    # Split the login information by whitespace
    login_parts = login_info.split()

    # Iterate through the login parts and extract the client name and password
    client_name = login_parts[0]
    print(client_name)
    client_password = login_parts[-1]
    print(client_password)

    # If client name and password are not provided, return None
    if client_name is None or client_password is None:
        return None

    # Iterate through the data to check if login information matches
    for discord_id, user_data in data.items():
        if user_data.get('name') == client_name and user_data.get('pin') == client_password:
            return discord_id

    # If no match is found, return None
    return None

@bot.event
async def on_message(message):
    if webhookbot_id in str(message.author): #server_api_keys webhookbot_id
        print("WebHook authorized")
        print(message.author)
        print(message.content)
        
        command_str, client_info = parse_client_input(message.content)
        discord_id = check_login(client_info, data)

        if discord_id is not None:

            if get_permission_status(str(discord_id), SOUNDBOARD_DATABASE) != "ban":

                if command_str.startswith('!play'):
                    print('gets the command!')
                    sound_file_name = command_str.split('!play ')[1]
                    guild = bot.get_guild(int(server_id)) # #server_api_keys server_id
                    voice_client = discord.utils.get(bot.voice_clients, guild=guild)
                    if voice_client:
                        mp3_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, f"{sound_file_name}.mp3")  # Replace with the path to your audio file
                        voice_client.play(discord.FFmpegPCMAudio(mp3_path))
                        while voice_client.is_playing():
                            await asyncio.sleep(1)

                if command_str.startswith('*'):
                    command, *args = command_str.split()
                    if command == "*rename" and len(args) >= 2:
                        try:
                            rename_process(args[0], args[1])
                        except Exception as e:
                            print("An error occurred while executing rename_process:")
                    if command == "*remove" and len(args) >= 1:
                        try:
                            remove_process(args[0])
                        except Exception as e:
                            print("An error occurred while executing remove_process:")
                    if command == "*change_audio_level" and len(args) >= 2:
                        try:
                            change_audio_level_process(args[0], args[1])
                        except Exception as e:
                            print(e)
                            print("An error occurred while executing change_audio_level_process:")
                    if command == "*youtube_download_sound_bit" and len(args) >= 3:
                        try:
                            name_arg = args[args.index("-n") + 1]
                            url_arg = args[args.index("-url") + 1]
                            time_frame_cut_arg = args[args.index("-cut") + 1] if "-cut" in args else None
                            youtube_download_sound_bit_process(name_arg, url_arg, time_frame_cut_arg)
                        except Exception as e:
                            print("An error occurred while executing youtube_download_sound_bit_process:")
                            print(e)
                    if command == "*update_APP_list":
                        try:
                            update_APP_list_process()
                        except Exception as e:
                            print("An error occurred while executing youtube_download_sound_bit_process:")
                            print(e)
                      
    await bot.process_commands(message)

@bot.command()
async def upload(ctx, arg, *args):
    """Upload (almoste) any audio or video format. *upload -n NAME -cut (Optional: "00:00:10-00:00:15")"""
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            if attachment.filename.lower().endswith('.mp3') or attachment.filename.lower().endswith('.mp4'):

                if arg == "-n":
                    # Get the name argument
                    name_arg = args[0]
                    await ctx.send(f'You provided the name argument: {name_arg}')
                else:
                    await ctx.send('Please provide the name argument (-n) for this command.')

                # Check if cut argument is provided
                cut_index = -1
                time_frame_cut_arg = None
                if "-cut" in args:
                    cut_index = args.index("-cut")
                    if len(args) > cut_index + 1:
                        time_frame_cut_arg = args[cut_index + 1]

                # Download the attachment to a local file
                attachment_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, attachment.filename)
                await attachment.save(attachment_path)

                # Convert the audio file to MP3 format using ffmpeg and cut the specified time frame
                if time_frame_cut_arg:
                    # Parse the time frame argument
                    start_time, end_time = time_frame_cut_arg.split('-')

                    start_time = datetime.strptime(start_time, '%H:%M:%S.%f')
                    end_time = datetime.strptime(end_time, '%H:%M:%S.%f')

                    time_difference = end_time - start_time
                    seconds_length = time_difference.seconds % 60

                    if int(seconds_length) > max_length_seconds:
                        await ctx.send(f'The audio file {attachment.filename} is to long: {seconds_length} seconds, while max length is: {max_length_seconds}.')
                        return
                        
                    # Generate the output file path with the specified name
                    output_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, name_arg + ".mp3")

                    # Use ffmpeg to cut the audio file and save it to the output path
                    subprocess.run(["ffmpeg", "-i", attachment_path, "-ss", start_time, "-to", end_time, "-c:a", "libmp3lame", "-q:a", "2", output_path])

                else:
                    # Generate the output file path with the specified name
                    output_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, name_arg + ".mp3")

                    # Use ffmpeg to convert the audio file to MP3 format and save it to the output path
                    subprocess.run(["ffmpeg", "-i", attachment_path, "-c:a", "libmp3lame", "-q:a", "2", output_path])

                # Remove the original audio file
                os.remove(attachment_path)

                # Send a confirmation message
                await ctx.send(f'The audio file {attachment.filename} has been uploaded and processed.')
            else:
                await ctx.send('Please attach an MP3 or MP4 file to your message.')

@bot.command()
async def play(ctx, sound_file_name):
    """Not for manual use. For playing command use /button  to get the soundboard"""
    if not ctx.voice_client:
        # Join the voice channel of the user who issued the command
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            return

    # Get the path of the previously uploaded MP3 file
    mp3_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, f"{sound_file_name}.mp3")

    if not os.path.exists(mp3_path):
        await ctx.send("No MP3 file found.")
        return

    # Play the MP3 file in the voice channel
    ctx.voice_client.play(discord.FFmpegPCMAudio(mp3_path))

    # Wait for the MP3 file to finish playing
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)

@bot.command()
async def refresh_sound_files(ctx):
    """Refreshes the list of shown sounds"""
    global SOUND_FILES
    SOUND_FILES = {}

    for filename in os.listdir(SOUND_DIRECTORY):
        if filename.endswith(".mp3"):
            name = os.path.splitext(filename)[0]
            SOUND_FILES[name] = name

    await ctx.send("Sound files refreshed!")

@bot.slash_command()
async def button(ctx):
    await ctx.respond("Soundboard", view=MyView(ctx, bot), ephemeral=True)

@bot.slash_command()
async def recover_account(ctx, new_name: str, new_password: str):
    discord_id = str(ctx.author.id)

    # Load the existing data from the JSON file
    with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json"), 'r') as file:
        data = json.load(file)

    # Check if the discord ID is in the dictionary
    if discord_id in data:

        # Check if the name is already taken
        for user_data in data.values():
            if user_data['name'] == new_name:
                if user_data != discord_id:
                    await ctx.respond("The new name is already taken, and was not your old name.", ephemeral=True)
                    return

        # Update the name and password for the user
        data[discord_id]['name'] = new_name
        data[discord_id]['pin'] = new_password

        # Save the updated data back to the JSON file
        with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json"), 'w') as file:
            json.dump(data, file, indent=4)
        create_account_settings(SOUNDBOARD_DATABASE, change_account=True)
        update_json_list_for_account_info(dropbox_access_token, SOUNDBOARD_DATABASE)

        await ctx.respond("Account recovered successfully. Name and password updated.", ephemeral=True)
    else:
        await ctx.respond("Unable to recover account. Discord ID not found.", ephemeral=True)

@bot.slash_command()
async def change_permission(ctx, name: str, permission_status: str):
    discord_id = str(ctx.author.id)

    # Load the existing data from the JSON file
    profile_data_file_path = os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_profile_data.json")
    with open(profile_data_file_path, 'r') as profile_file:
        database = json.load(profile_file)

    # Check if the executor has admin permission
    executor_settings = database.get(discord_id)
    if executor_settings and executor_settings['permission_status'] == 'admin':
        # Iterate through each account settings in the database
        for account_settings in database.values():
            if account_settings.get('name') == name:
                # Change the permission status
                account_settings['permission_status'] = permission_status

        # Save the updated database to the JSON file
        with open(profile_data_file_path, 'w') as profile_file:
            json.dump(database, profile_file, indent=4)

        await ctx.respond(f"Permission status for {name} changed to {permission_status}.", ephemeral=True)
        update_json_list_for_account_info(dropbox_access_token, SOUNDBOARD_DATABASE)

    else:
        await ctx.respond("You do not have permission to change permission status.", ephemeral=True)

@bot.slash_command()
async def sign_up(ctx, name: str, pin: str):
    discord_id = str(ctx.author.id)

    # Check if the JSON file exists
    if not os.path.exists(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json")):
        data = {}
    else:
        # Load the existing data from the JSON file
        with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json"), 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
        
    # Check if the discord ID is already in the dictionary
    if discord_id in data:
        await ctx.respond("You have already signed up.", ephemeral=True)
        return

    # Check if the name is already taken
    for user_data in data.values():
        if user_data['name'] == name:
            await ctx.respond("The name is already taken.", ephemeral=True)
            return

    # Save the new user information in the dictionary
    data[discord_id] = {'name': name, 'pin': pin}

    # Save the updated data back to the JSON file
    with open(os.path.join(os.getcwd(), SOUNDBOARD_DATABASE, "soundboard_account_data.json"), 'w') as file:
        json.dump(data, file, indent=4)

    #create account settings to the account profile JSON file
    create_account_settings(SOUNDBOARD_DATABASE)
    update_json_list_for_account_info(dropbox_access_token, SOUNDBOARD_DATABASE)

    await ctx.respond(f"Sign up successful!, here is the connect key: {dropbox_sounds_list_link_key}", ephemeral=True)

@bot.slash_command()
async def get_connect_key(ctx):
     await ctx.respond(f"Connect key: {dropbox_sounds_list_link_key}", ephemeral=True)

@bot.slash_command()
async def download_client(ctx):
    """Download up to date client"""

    # List all files in the CURRENT_CLIENT_DIRECTORY
    files = os.listdir(CURRENT_CLIENT_DIRECTORY)
    file_name_found = None

    # Find the first file that starts with "FF_" and has a .exe extension
    for file_name in files:
        if file_name.startswith("FF_") and file_name.endswith(".exe"):
            file_path = os.path.join(CURRENT_CLIENT_DIRECTORY, file_name)
            file_name_found = file_name
            break


    if file_name_found is None:
        ctx.respond(f"File  not found.", ephemeral=True)
        return

    # Send the file to the user
    with open(file_path, "rb") as f:
        await ctx.respond(file=discord.File(f, file_name_found), ephemeral=True)#ctx.send(file=discord.File(f, file_name_found))

@bot.command()
async def list_files(ctx):
    """Shows all sound names"""
    dir_path = os.path.join(os.getcwd(), SOUND_DIRECTORY)
    files = os.listdir(dir_path)
    files_str = "\n".join(files)
    await ctx.send(f"{files_str}")

def remove_process(filename):
    path = os.path.join(os.getcwd(), SOUND_DIRECTORY, f"{filename}.mp3")
    try:
        os.remove(path)
        print(f"The file {filename}.mp3 has been successfully removed.")
    except FileNotFoundError:
        print(f"The file {filename}.mp3 could not be found.")

@bot.command()
async def remove(ctx, filename):
    """Remove sound"""
    try:
        remove_process(filename)
        await ctx.send(f"The file {filename} has been successfully removed.")
    except FileNotFoundError:
        await ctx.send(f"The file {filename} could not be found.")

def rename_process(old_filename, new_filename):
    """Rename sound"""
    old_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, f'{old_filename}.mp3')
    new_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, f'{new_filename}.mp3')
    try:
        os.rename(old_path, new_path)
    except FileNotFoundError:
        print(f"The file {old_filename} could not be found.")
    except FileExistsError:
        print(f"The file {new_filename} already exists.")

@bot.command()
async def rename(ctx, old_filename, new_filename):
    """Rename sound"""
    try:
        rename_process(old_filename, new_filename)
        await ctx.send(f"The file {old_filename} has been successfully renamed to {new_filename}.")
    except FileNotFoundError:
        await ctx.send(f"The file {old_filename} could not be found.")
    except FileExistsError:
        await ctx.send(f"The file {new_filename} already exists.")

@bot.command()
async def docs(ctx):
    """Displays documentation for the bot's commands"""
    # Create an embed with a title and description
    embed = discord.Embed(title="Bot Documentation", description="Here are the available commands:")

    # Loop through all the bot's commands and add them to the embed
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help, inline=False)

    # Send the embed as a message
    await ctx.send(embed=embed)

@bot.command()
async def download(ctx, name):
    """Download mp3 file from the bot"""
    # Check if the requested file exists in the sound directory
    file_path = os.path.join(SOUND_DIRECTORY, f"{name}.mp3")
    if not os.path.isfile(file_path):
        await ctx.send(f"File '{name}.mp3' not found.")
        return

    # Send the file to the user
    with open(file_path, "rb") as f:
        await ctx.send(file=discord.File(f, f"{name}.mp3"))

def change_audio_level_process(name: str, decibel: int) -> str:
    using_store_dir = os.path.join(os.getcwd(), SOUND_DIRECTORY)
    original_store_dir = os.path.join(os.getcwd(), SOUND_ORIGINAL_DIRECTORY)

    original_file_path = os.path.join(original_store_dir, name + ".mp3")
    destination_file_path = os.path.join(using_store_dir, name + ".mp3")

    if os.path.exists(original_file_path):
        # Replace the file in the destination directory if it already exists
        os.remove(destination_file_path)
        # Copy the file from the original store to the destination directory
        shutil.copy(original_file_path, using_store_dir)
    else:
        shutil.copy(os.path.join(using_store_dir, name + ".mp3"), original_store_dir)

    # Check if the file exists in the destination directory
    if not os.path.exists(destination_file_path):
        print(f"File {name}.mp3 does not exist.")
        return f"File {name}.mp3 does not exist."

    # Load the audio file
    audio = AudioSegment.from_file(destination_file_path, format="mp3")

    # Calculate the current loudness in dBFS
    current_loudness = audio.dBFS
    print("Current loudness:", current_loudness)

    # Calculate the target loudness
    target_loudness = current_loudness + int(decibel)
    if target_loudness > 20:
        return f'Audio change request is to high'
    print("Target loudness:", target_loudness)

    # Adjust the audio level
    adjusted_audio = audio + target_loudness - current_loudness

    # Export the adjusted audio file
    adjusted_audio.export(destination_file_path, format="mp3")

    print(f"The audio file {name}.mp3 has been processed and the decibel has been changed by {decibel} decibel from the original upload.")
    return f"The audio file {name}.mp3 has been processed and the decibel has been changed by {decibel} decibel from the original upload."

@bot.command()
async def change_audio_level(ctx, name: str, decibel: int):
    """Changes the audio level of an MP3 file. (decibel change from original)"""
    result = change_audio_level_process(name, decibel)
    await ctx.send(result)

def youtube_download_sound_bit_process(name_arg, url_arg, time_frame_cut_arg):

    if time_frame_cut_arg:
        # Parse the time frame argument
        start_time, end_time = time_frame_cut_arg.split('-')

        start_time = datetime.strptime(start_time, '%H:%M:%S.%f')
        end_time = datetime.strptime(end_time, '%H:%M:%S.%f')

        time_difference = end_time - start_time
        seconds_length = time_difference.seconds % 60

    if int(seconds_length) > max_length_seconds:
        print(f'The audio file is to long: {seconds_length} seconds, while max length is: {max_length_seconds}.')
        return f'The audio file is to long: {seconds_length} seconds, while max length is: {max_length_seconds}.'

    try:
        yt = YouTube(url_arg)
        stream = yt.streams.filter(only_audio=True).first()
        if stream:
            stream.download(output_path=os.path.join(os.getcwd(), SOUND_DIRECTORY), filename=f"{name_arg}_temp.mp3")
            attachment_path = os.path.join(os.getcwd(), f"audio_data_test_store/{name_arg}_temp.mp3")

            # Convert the audio file to MP3 format using ffmpeg and cut the specified time frame
            if time_frame_cut_arg:
                # Generate the output file path with the specified name
                output_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, f"{name_arg}.mp3")

                # Use ffmpeg to cut the audio file and save it to the output path
                subprocess.run(["ffmpeg", "-i", attachment_path, "-ss", start_time, "-to", end_time, "-c:a", "libmp3lame", "-q:a", "2", output_path])
            else:
                # Generate the output file path with the specified name
                output_path = os.path.join(os.getcwd(), SOUND_DIRECTORY, f"{name_arg}.mp3")

                # Use ffmpeg to convert the audio file to MP3 format and save it to the output path
                subprocess.run(["ffmpeg", "-i", attachment_path, "-c:a", "libmp3lame", "-q:a", "2", output_path])

            # Remove the original audio file
            os.remove(attachment_path)
        else:
            return 'Cannot find audio stream in the video.'
    except Exception as e:
        return f'Error occurred while downloading audio: {e}'

    return f"The sound bit has been downloaded and saved as `{name_arg}.mp3`."

@bot.command()
async def youtube_download_sound_bit(ctx, arg, *args):
    """Download a portion of a YouTube video based on start and end time: *youtube_download_sound_bit -n NAME -url YT_URL -cut (Optional: "00:00:10-00:00:15")     Note that for milisecond this is the notation required:  00:00:05.500-00:00:08.500"""

    if arg == "-n":
        # Get the name argument
        name_arg = args[0]
        await ctx.send(f'You provided the name argument: {name_arg}')
    else:
        await ctx.send('Please provide the name argument (-n) for this command.')

    # Check if URL argument is provided
    url_index = -1
    url_arg = None
    if "-url" in args:
        url_index = args.index("-url")
        if len(args) > url_index + 1:
            url_arg = args[url_index + 1]

    # Check if cut argument is provided
    cut_index = -1
    time_frame_cut_arg = None
    if "-cut" in args:
        cut_index = args.index("-cut")
        if len(args) > cut_index + 1:
            time_frame_cut_arg = args[cut_index + 1]

    # Download the audio file
    result = youtube_download_sound_bit_process(name_arg, url_arg, time_frame_cut_arg)
    await ctx.send(result)
    if "Error" in result:
        return

    # Send a confirmation message
    await ctx

def update_APP_list_process():
    update_json_list_for_app(dropbox_access_token, SOUND_DIRECTORY, SOUNDBOARD_DATABASE)
    print('APP list updated successfully.')

@bot.command()
async def update_APP_list(ctx):
    """Update the list of commands in the external app"""
    update_json_list_for_app(dropbox_access_token, SOUND_DIRECTORY, SOUNDBOARD_DATABASE)
    await ctx.send('APP list updated successfully.')

# Run the bot
bot.run(discord_bot_token)