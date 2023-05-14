import discord
from discord.ext import commands
import asyncio
import os
import subprocess
import functools
from pydub import AudioSegment
import shutil
import pytube
from pytube import YouTube

from discord.ui import View, Button, Item

# Check if the directories exist, and create them if they don't
if not os.path.exists(os.path.join(os.getcwd(), "audio_data_test_store")):
    os.mkdir(os.path.join(os.getcwd(), "audio_data_test_store"))
if not os.path.exists(os.path.join(os.getcwd(), "audio_data_test_store_original")):
    os.mkdir(os.path.join(os.getcwd(), "audio_data_test_store_original"))


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("*"),
    description='Relatively simple music bot example',
    intents=intents,)

#channel connect ID:
channel_connect_ID = "Channel_ID"

# Set up event listeners for when the bot connects to the Discord server
#run
@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')
    channel = bot.get_channel(channel_connect_ID)
    vc = await channel.connect()

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
                attachment_path = os.path.join(os.getcwd(), "audio_data_test_store", attachment.filename)
                await attachment.save(attachment_path)

                # Convert the audio file to MP3 format using ffmpeg and cut the specified time frame
                if time_frame_cut_arg:
                    # Parse the time frame argument
                    start_time, end_time = time_frame_cut_arg.split('-')

                    # Generate the output file path with the specified name
                    output_path = os.path.join(os.getcwd(), "audio_data_test_store", name_arg + ".mp3")

                    # Use ffmpeg to cut the audio file and save it to the output path
                    subprocess.run(["ffmpeg", "-i", attachment_path, "-ss", start_time, "-to", end_time, "-c:a", "libmp3lame", "-q:a", "2", output_path])

                else:
                    # Generate the output file path with the specified name
                    output_path = os.path.join(os.getcwd(), "audio_data_test_store", name_arg + ".mp3")

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
    mp3_path = os.path.join(os.getcwd(), "audio_data_test_store", f"{sound_file_name}.mp3")

    if not os.path.exists(mp3_path):
        await ctx.send("No MP3 file found.")
        return

    # Play the MP3 file in the voice channel
    ctx.voice_client.play(discord.FFmpegPCMAudio(mp3_path))

    # Wait for the MP3 file to finish playing
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)


SOUND_DIRECTORY = "audio_data_test_store"
SOUND_FILES = {}

for filename in os.listdir(SOUND_DIRECTORY):
    if filename.endswith(".mp3"):
        name = os.path.splitext(filename)[0]
        SOUND_FILES[name] = name


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

@bot.command()
async def list_files(ctx):
    dir_path = os.path.join(os.getcwd(), "audio_data_test_store")
    files = os.listdir(dir_path)
    files_str = "\n".join(files)
    await ctx.send(f"{files_str}")

@bot.command()
async def remove(ctx, filename):
    path = os.path.join(os.getcwd(), "audio_data_test_store", filename)
    try:
        os.remove(path)
        await ctx.send(f"The file {filename} has been successfully removed.")
    except FileNotFoundError:
        await ctx.send(f"The file {filename} could not be found.")

@bot.command()
async def rename(ctx, old_filename, new_filename):
    old_path = os.path.join(os.getcwd(), "audio_data_test_store", old_filename)
    new_path = os.path.join(os.getcwd(), "audio_data_test_store", new_filename)
    try:
        os.rename(old_path, new_path)
        await ctx.send(f"The file {old_filename} has been successfully renamed to {new_filename}.")
    except FileNotFoundError:
        await ctx.send(f"The file {old_filename} could not be found.")
    except FileExistsError:
        await ctx.send(f"The file {new_filename} already exists.")

@bot.command()
async def docs(ctx):
    """Displays documentation for the bot's commands. See github:  """
    # Create an embed with a title and description
    embed = discord.Embed(title="Bot Documentation", description="Here are the available commands:")

    # Loop through all the bot's commands and add them to the embed
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help, inline=False)

    # Send the embed as a message
    await ctx.send(embed=embed)

@bot.command()
async def download(ctx, name):
    # Check if the requested file exists in the sound directory
    file_path = os.path.join(SOUND_DIRECTORY, f"{name}.mp3")
    if not os.path.isfile(file_path):
        await ctx.send(f"File '{name}.mp3' not found.")
        return

    # Send the file to the user
    with open(file_path, "rb") as f:
        await ctx.send(file=discord.File(f, f"{name}.mp3"))


@bot.command()
async def change_audio_level(ctx, name: str, decibel: int):
    """Changes the audio level of an MP3 file. (decibel change from original)"""

    using_store__dir = os.path.join(os.getcwd(), "audio_data_test_store")
    original_store_dir = os.path.join(os.getcwd(), "audio_data_test_store_original")

    if os.path.exists(os.path.join(os.getcwd(), "audio_data_test_store_original", name + ".mp3")):
        # Replace the file in the destination directory if it already exists
        os.remove(os.path.join(using_store__dir,  name + ".mp3"))
        # Copy the file from source to destination directory
        shutil.copy(os.path.join(original_store_dir, name + ".mp3"), using_store__dir)
    else:
        shutil.copy(os.path.join(using_store__dir, name + ".mp3"), original_store_dir)

    # Construct the file path
    file_path = os.path.join(os.getcwd(), "audio_data_test_store", name + ".mp3")

    # Check if the file exists
    if not os.path.exists(file_path):
        await ctx.send(f"File {name}.mp3 does not exist.")
        return

    # Load the audio file
    audio = AudioSegment.from_file(file_path, format="mp3")

    # Calculate the maximum loudness in dBFS
    loudness = audio.max_dBFS
    print(abs(loudness))

    # Change the audio level
    audio = audio.apply_gain(decibel)

    # Export the audio file
    audio.export(file_path, format="mp3")

    # Send a confirmation message
    await ctx.send(f"The audio file {name}.mp3 has been processed and the decibel has been changed by {decibel} decibel from original upload.")

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
    time_frame_cut_arg = None
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
    try:
        yt = YouTube(url_arg)
        stream = yt.streams.filter(only_audio=True).first()
        if stream:


            stream.download(output_path= os.path.join(os.getcwd(), "audio_data_test_store"),filename=f"{name_arg}_temp.mp3")

            attachment_path = os.path.join(os.getcwd(), f"audio_data_test_store/{name_arg}_temp.mp3")

            # Convert the audio file to MP3 format using ffmpeg and cut the specified time frame
            if time_frame_cut_arg:
                # Parse the time frame argument
                start_time, end_time = time_frame_cut_arg.split('-')

                # Generate the output file path with the specified name
                output_path = os.path.join(os.getcwd(), "audio_data_test_store", name_arg + ".mp3")

                # Use ffmpeg to cut the audio file and save it to the output path
                subprocess.run(["ffmpeg", "-i", attachment_path, "-ss", start_time, "-to", end_time, "-c:a", "libmp3lame", "-q:a", "2", output_path])

            else:
                # Generate the output file path with the specified name
                output_path = os.path.join(os.getcwd(), "audio_data_test_store", name_arg + ".mp3")

                # Use ffmpeg to convert the audio file to MP3 format and save it to the output path
                subprocess.run(["ffmpeg", "-i", attachment_path, "-c:a", "libmp3lame", "-q:a", "2", output_path])

            # Remove the original audio file
            os.remove(attachment_path)

        else:
            await ctx.send('Cannot find audio stream in the video.')
            return
    except Exception as e:
        await ctx.send(f'Error occurred while downloading audio: {e}')
        return

    # Send a confirmation message
    await ctx.send(f"The sound bit has been downloaded and saved as `{name_arg}.mp3`.")




# Run the bot
bot.run("BOT_TOKEN")