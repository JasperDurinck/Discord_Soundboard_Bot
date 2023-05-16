import tkinter as tk
import requests
from tkinter import ttk
from tkinter import simpledialog, messagebox


webhook_url = "DISCORD_Web_Hook_Key"
        

def update_json_list():
    url = "https://dl.dropboxusercontent.com/s/(your link)/audio_names.json" #!!!!change

    # Send a GET request to retrieve the file content
    response = requests.get(url)

    if response.status_code == 200:
        # Content of the JSON file
        file_content = response.json()
        # Process the JSON file content as needed
        print(file_content)
        file_content.append("update")
        file_content.append("settings")
        file_content.append("Bot manager")
        return file_content
    else:
        print(f"Failed to retrieve file. Status code: {response.status_code}")


def send_message_to_discord_webhook(webhook_url, message_content):
        payload = {
            "content": message_content
        }
        response = requests.post(webhook_url, json=payload)


def play_sound(sound_name):
    # Implement the logic to play the sound based on the sound_name
    if sound_name == "update":
        refresh_buttons()
    elif sound_name == "settings":
        open_settings()
    elif sound_name == "Bot manager":
        open_bot_manager()
    else:
        print(f"Playing sound: {sound_name}")
        message_content = f"!play {sound_name}"
        send_message_to_discord_webhook(webhook_url, message_content)

def drag_window(event):
    window.geometry(f"+{event.x_root - x_click_pos}+{event.y_root - y_click_pos}")

def save_click_pos(event):
    global x_click_pos, y_click_pos
    x_click_pos = event.x
    y_click_pos = event.y

def on_mousewheel(event):
    canvas.yview_scroll(-1 * int(event.delta/120), "units")

def open_bot_manager():
    bot_manager_window = tk.Toplevel(window)
    bot_manager_window.title("Bot Manager")
    bot_manager_window.config(bg="black")

    # Retrieve the list of audio files
    list_audio_files = update_json_list()

    # Create Tab Control
    tab_control = ttk.Notebook(bot_manager_window)

    # Create Change Audio Level Tab
    change_audio_level_tab = tk.Frame(tab_control, bg="black")
    tab_control.add(change_audio_level_tab, text="Change Audio Level")
    def select_button_for_change_audio(sound_name):
        number_change_audio = simpledialog.askinteger("Change Audio Level", f"Enter the audio level for {sound_name}:", minvalue=-100)
        if number_change_audio is not None:
            message_content = f"*change_audio_level {sound_name} {number_change_audio}"
            send_message_to_discord_webhook(webhook_url, message_content)
    # Create selection buttons for each audio file in the "Change Audio Level" tab
    for sound_name in list_audio_files[:-3]:
        selection_button = tk.Button(change_audio_level_tab, text=sound_name, command=lambda name=sound_name: select_button_for_change_audio(name))
        selection_button.pack()

    # Create Remove Tab
    remove_tab = tk.Frame(tab_control, bg="black")
    tab_control.add(remove_tab, text="Remove")
    def select_button_for_remove(sound_name):
        confirmed = messagebox.askyesno("Confirmation", f"Are you sure you want to remove {sound_name}?")
        if confirmed:
            message_content = f"*remove {sound_name}.mp3"
            send_message_to_discord_webhook(webhook_url, message_content)
    # Create selection buttons for each audio file in the "Remove" tab
    for sound_name in list_audio_files[:-3]:
        selection_button = tk.Button(remove_tab, text=sound_name, command=lambda name=sound_name: select_button_for_remove(name))
        selection_button.pack()

    # Create Rename Tab
    rename_tab = tk.Frame(tab_control, bg="black")
    tab_control.add(rename_tab, text="Rename")
    def select_button_for_rename(sound_name):
        change_name = simpledialog.askstring("Rename", f"Enter new name for {sound_name}:")
        if change_name is not None:
            message_content = f"*rename {sound_name} {change_name}"
            send_message_to_discord_webhook(webhook_url, message_content)
    # Create selection buttons for each audio file in the "Remove" tab
    for sound_name in list_audio_files[:-3]:
        selection_button = tk.Button(rename_tab, text=sound_name, command=lambda name=sound_name: select_button_for_rename(name))
        selection_button.pack()

    # Create Update App List Tab
    update_app_list_tab = tk.Frame(tab_control, bg="black")
    tab_control.add(update_app_list_tab, text="Update App List")
    def update_APP_list():
            message_content = f"*update_APP_list"
            send_message_to_discord_webhook(webhook_url, message_content)
    # Create a button for updating the app list
    update_button = tk.Button(update_app_list_tab, text="Update App List", command=update_APP_list)
    update_button.pack()

    # Create YouTube Download Tab
    youtube_download_tab = tk.Frame(tab_control, bg="black")
    tab_control.add(youtube_download_tab, text="YouTube Download")
    def youtube_download():
        url = simpledialog.askstring("YouTube Download", "Enter the YouTube URL:")
        if url is not None:
            new_sound_name = simpledialog.askstring("YouTube Download", "Enter the new sound name:")
            if new_sound_name is not None:
                time_range = simpledialog.askstring("YouTube Download", "Enter the time range (e.g., 00:00:00.000-00:00:10.000):", initialvalue="00:00:00.000-00:00:10.000")
                if time_range is None:
                    time_range = ""
                message_content = f"*youtube_download_sound_bit -n {new_sound_name} -url {url} -cut {time_range}"
                send_message_to_discord_webhook(webhook_url, message_content)

    # Create a button for YouTube download
    download_button = tk.Button(youtube_download_tab, text="YouTube Download", command=youtube_download)
    download_button.pack()

    # Pack the Tab Control
    tab_control.pack(expand=1, fill="both")

    # Set window transparency
    bot_manager_window.wm_attributes('-alpha', 0.7)

# Function to set the button color and text color
def open_settings():
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.config(bg="black")
    settings_window.wm_attributes('-alpha', 0.7)

    # Function to set the window size
    def set_window_size():
        width = int(width_slider.get())
        height = int(height_slider.get())
        window.geometry(f"{width}x{height}")

        # Resize the canvas to match the new window size
        canvas.config(width=width, height=height)
        canvas.update_idletasks()

    # Function to set the button color and text color
    def set_button_color():
        color = button_color_variable.get()

        # Update button colors and text colors based on the selected color
        if color == "Black":
            for button in buttons:
                button.config(bg="black", fg="white")  # Set background color to black and text color to white
        elif color == "Grey":
            for button in buttons:
                button.config(bg="grey", fg="black")  # Set background color to grey and text color to white

    # Function to set the transparency level
    def set_transparency_level():
        transparency = transparency_slider.get()
        window.wm_attributes('-alpha', transparency)

    # Create settings labels
    width_label = tk.Label(settings_window, text="Width:", bg="black", fg="white")
    width_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

    height_label = tk.Label(settings_window, text="Height:", bg="black", fg="white")
    height_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

    button_color_label = tk.Label(settings_window, text="Button Color:", bg="black", fg="white")
    button_color_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

    transparency_label = tk.Label(settings_window, text="Transparency Level:", bg="black", fg="white")
    transparency_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

    # Create settings sliders
    width_slider = tk.Scale(settings_window, from_=200, to=800, orient=tk.HORIZONTAL, bg="black", fg="white")
    width_slider.grid(row=0, column=1, padx=10, pady=10)

    height_slider = tk.Scale(settings_window, from_=200, to=600, orient=tk.HORIZONTAL, bg="black", fg="white")
    height_slider.grid(row=1, column=1, padx=10, pady=10)

    # Create button color dropdown
    button_color_variable = tk.StringVar(settings_window)
    button_color_variable.set("Black")  # Default color selection
    button_color_dropdown = tk.OptionMenu(settings_window, button_color_variable, "Black", "Grey", "White")
    button_color_dropdown.config(bg="black", fg="white")
    button_color_dropdown.grid(row=2, column=1, padx=10, pady=10)

    # Create transparency slider
    transparency_slider = tk.Scale(settings_window, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, bg="black", fg="white")
    transparency_slider.grid(row=3, column=1, padx=10, pady=10)

    # Create buttons to save settings
    save_button = tk.Button(settings_window, text="Save Size", command=set_window_size, bg="black", fg="white")
    save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    set_color_button = tk.Button(settings_window, text="Set Button Color", command=set_button_color, bg="black", fg="white")
    set_color_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    set_transparency_button = tk.Button(settings_window, text="Set Transparency", command=set_transparency_level, bg="black", fg="white")
    set_transparency_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Update buttons list with dynamically created buttons
    buttons = []

    def create_button(sound_name):
        button = tk.Button(frame, text=sound_name, command=lambda name=sound_name: play_sound(name))
        button.pack()
        buttons.append(button)  # Add the button to the list

    # Clear existing buttons
    for button in frame.winfo_children():
        button.destroy()

    # Create buttons dynamically
    for sound_name in audio_names:
        create_button(sound_name)

def refresh_buttons():
    # Update the list of audio names
    audio_names = update_json_list()

    # Clear existing buttons
    for button in frame.winfo_children():
        button.destroy()

    # Create buttons dynamically
    for sound_name in audio_names:
        button = tk.Button(frame, text=sound_name, command=lambda name=sound_name: play_sound(name))
        button.pack()

#check for updata json list
audio_names = update_json_list()

# Create the tkinter window
window = tk.Tk()
window.title("Soundboard")

# Remove title bar and buttons
window.overrideredirect(True)

# Set window attributes for transparency
window.attributes('-transparentcolor', 'white')
window.config(bg='white')


# Create a canvas to hold buttons
canvas = tk.Canvas(window, bg='white', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Create a frame to hold the buttons
frame = tk.Frame(canvas, bg='white')
canvas.create_window((0, 0), window=frame, anchor='nw')

# Create buttons dynamically
for sound_name in audio_names:
    button = tk.Button(frame, text=sound_name, command=lambda name=sound_name: play_sound(name))
    button.pack()

# Set window background transparency
window.wm_attributes('-alpha', 0.5)

# Make window draggable
x_click_pos = 0
y_click_pos = 0
window.bind("<ButtonPress-1>", save_click_pos)
window.bind("<B1-Motion>", drag_window)

# Bind the mousewheel event to the canvas
canvas.bind_all("<MouseWheel>", on_mousewheel)

# Make window stay in the foreground
window.wm_attributes('-topmost', 1)

# Start the tkinter event loop
window.mainloop()