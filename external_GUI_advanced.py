import tkinter as tk
from tkinter import *
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
            "content": message_content,
        }
        response = requests.post(webhook_url, json=payload)

def play_sound(sound_name):
    # Implement the logic to play the sound based on the sound_name
    if sound_name == "update":
        app.refresh_buttons()
    elif sound_name == "settings":
        open_settings()
    elif sound_name == "Bot manager":
        open_bot_manager()
    else:
        print(f"Playing sound: {sound_name}")
        message_content = f"!play {sound_name}"
        send_message_to_discord_webhook(webhook_url, message_content)


def open_bot_manager():
    bot_manager_window = tk.Toplevel(app)
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
            message_content = f"*remove {sound_name}"
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
    settings_window = tk.Toplevel(app)
    settings_window.title("Settings")
    settings_window.config(bg="black")
    settings_window.wm_attributes('-alpha', 0.7)

    # Function to set the window size
    def set_window_size():
        width = int(width_slider.get())
        height = int(height_slider.get())
        app.geometry(f"{width}x{height}")

        # Resize the canvas to match the new window size
        app.config(width=width, height=height)
        app.update_idletasks()

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
        app.wm_attributes('-alpha', transparency)

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
    width_slider = tk.Scale(settings_window, from_=100, to=800, orient=tk.HORIZONTAL, bg="black", fg="white")
    width_slider.set(200)
    width_slider.grid(row=0, column=1, padx=10, pady=10)

    height_slider = tk.Scale(settings_window, from_=100, to=600, orient=tk.HORIZONTAL, bg="black", fg="white")
    height_slider.set(200)
    height_slider.grid(row=1, column=1, padx=10, pady=10)

    # Create button color dropdown
    button_color_variable = tk.StringVar(settings_window)
    button_color_variable.set("Black")  # Default color selection
    button_color_dropdown = tk.OptionMenu(settings_window, button_color_variable, "Black", "Grey", "White")
    button_color_dropdown.config(bg="black", fg="white")
    button_color_dropdown.grid(row=2, column=1, padx=10, pady=10)

    # Create transparency slider
    transparency_slider = tk.Scale(settings_window, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, bg="black", fg="white")
    transparency_slider.set(0.3)  # Set the initial value to 0.3
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

class VerticalScrolledFrame(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object for scrolling
        canvas = Canvas(self, bd=0, highlightthickness=0)
        canvas.configure(bg='white', highlightbackground='white')  # Make the canvas transparent
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)

    
        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)
        interior.configure(bg='white', highlightbackground='white')

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-4 * (event.delta / 120)), "units")
        self.interior.bind_all("<MouseWheel>", _on_mousewheel)

        # track changes to the canvas and frame width and sync them
        def _configure_interior(event):
            # update the scrollable region
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class App_interface(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.overrideredirect(True)  # Remove window border
        self.attributes('-alpha', 0.5)  # Set window transparency
        # Set window attributes for transparency
        self.attributes('-transparentcolor', 'white')
        self.config(bg='white')

        self.wm_attributes('-topmost', 1)  # Stay on the foreground
        self.geometry("300x100")  # Set the window size here

        self.button_frame = Frame(self)
        self.button_frame.pack()

        self.frame = VerticalScrolledFrame(self)
        self.frame.pack()

        self.buttons_visible = True  # Track visibility of buttons

    def refresh_buttons(self):

        #check for updata json list
        audio_names = update_json_list()

        self.buttons = []

        # Clear existing buttons
        for button in self.button_frame.winfo_children():
            button.destroy()

        self.toggle_button = Button(self.button_frame, text="Toggle Buttons", command=self.toggle_buttons)
        self.toggle_button.pack()

        # Clear existing buttons
        for button in self.frame.interior.winfo_children():
            button.destroy()

        # Create buttons dynamically
        for sound_name in audio_names:
            button = Button(self.frame.interior, text=sound_name, command=lambda name=sound_name: play_sound(name))
            button.pack()
            self.buttons.append(button)  # Add the button to the hidden_buttons list
            

        # Make the window draggable
        self.draggable = True
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)
        self.bind("<B1-Motion>", self.drag)

    def toggle_buttons(self):
        self.buttons_visible = not self.buttons_visible
        if self.buttons_visible:
            for button in self.buttons:
                button.pack()
        else:
            for button in self.buttons:
                button.pack_forget()

    def start_drag(self, event):
        if self.draggable:
            self.x = event.x
            self.y = event.y

    def stop_drag(self, event):
        if self.draggable:
            self.x = None
            self.y = None

    def drag(self, event):
                if self.draggable and self.x is not None and self.y is not None:
                    deltax = event.x - self.x
                    deltay = event.y - self.y
                    x = self.winfo_x() + deltax
                    y = self.winfo_y() + deltay
                    self.geometry(f"+{x}+{y}")

app = App_interface()
app.refresh_buttons()
app.mainloop()