# Discord_Soundboard_Bot
Discord Soundboard bot. Features: upload (moste commen video and audio formats), download from youtube, both in discord and external (overlay) interface, cut time frame and change audio levels. Separate from the discord soundboard, thus unlimited free soundboard slots.

Only tested on python 3.10, on windows.

How to setup and run it:

1. Go to Discord https://discord.com/developers/applications, make the bot that will be used for the soundboard.
2. Download the required packages (see below) in a new enviorment preferably (python version 3.10 tested)
3. Fill in the required Channel/Server IDs,(optinal:) dropbox API key and add a Discord Web Hook (the web hook can also be added in a separate discord server, 
   but make sure that the soundboard bot can also access that discord server (if you want to use the external app)
4. (optinal:) provide the dropbox link where the external app can access the names of (by the soundboard bot) uploaded sound names.
5. (optinal:) Use for example the package pyinstaller to create an .exe file of the GUI.py (should be around 11mB .exe file), 
    which is the only thing other users will need to use the soundboard though interface separate from discord.
6. (info:) Use *help or *docs to see more info on the commands and documentation (feel free to change the prefix in the code)
