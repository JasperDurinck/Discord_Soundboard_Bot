import tkinter as tk
import requests

def update_json_list():
    url = "dropbox_link_file_with_json_list_sound_names"

    # Send a GET request to retrieve the file content
    response = requests.get(url)

    if response.status_code == 200:
        # Content of the JSON file
        file_content = response.json()
        # Process the JSON file content as needed
        print(file_content)
        file_content.append("update")
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
    else:
        print(f"Playing sound: {sound_name}")
        import requests
        webhook_url = "#Discord_channel_Web_Hook_bot_key"
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

# # Read the JSON file
# with open('audio_names.json', 'r') as file:
#     audio_names = json.load(file)

# Create the tkinter window
window = tk.Tk()
window.title("Soundboard")

# Remove title bar and buttons
window.overrideredirect(True)

# Set window attributes for transparency
window.attributes('-transparentcolor', 'white')
window.config(bg='white')

# Set maximum window size
max_width = 300
max_height = 100
window.minsize(200, 200)
window.maxsize(max_width, max_height)

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