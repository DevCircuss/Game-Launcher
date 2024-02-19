from tkinter import *
from tkinter.font import Font
from PIL import Image, ImageTk, ImageEnhance
import math
from pyexcel_ods3 import get_data, save_data
import os
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import date, datetime
from tkinter import ttk
import random
from PIL import ImageDraw
from PIL import ImageFont

import requests
from bs4 import BeautifulSoup
import re
from PIL import Image

from selenium import webdriver
import io

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

from steamgrid import SteamGridDB

from inputs import get_gamepad

stored_grid = None

library_view = []

# This is the index of the currently-selected game. Start at the top.
selected_game_index = 0

# This is your scrollbar position. You'll need to adjust how this works based
# on your GUI library and specific use case.
scroll_position = 0

# Class definition for game objects
class Game:
    def __init__(self, title, sort_title, series, release_date, console, genres, developers, publishers, completion_status, collections, version_name, box_art, launch_path, isCollection, visible_version):
        self.title = title
        self.sort_title = sort_title
        self.series = series
        self.release_date = release_date
        self.console = console
        self.genres = genres
        self.developers = developers
        self.publishers = publishers
        self.completion_status = completion_status
        self.collections = collections
        self.version_name = version_name
        self.box_art = box_art
        self.launch_path = launch_path
        self.isCollection = isCollection
        self.visible_version = visible_version

class Collection:
    def __init__(self, title, sort_title, series, release_date, console, genres, developers, publishers, completion_status, collections, version_name, box_art, launch_path, isCollection, visible_version):
        self.title = title
        self.sort_title = sort_title
        self.series = series
        self.release_date = release_date
        self.console = console
        self.genres = genres
        self.developers = developers
        self.publishers = publishers
        self.completion_status = completion_status
        self.collections = collections
        self.version_name = version_name
        self.box_art = box_art
        self.launch_path = launch_path
        self.isCollection = isCollection
        self.visible_version = visible_version

import json

def load_image(image_path):
    try:
        image = Image.open(image_path).convert("RGBA")
    except:
        image = Image.open(r"DefaultImages\NoImage.png").convert("RGBA")

    image = image.resize((grid_dim_x, grid_dim_y), Image.LANCZOS)
    background = Image.new("RGBA", image.size, (0, 0, 0, 0))
    background.paste(image, (0, 0), image)
    photo = ImageTk.PhotoImage(background)
    image_queue.put(photo)


# Retrieve the game library from the ods file
data = get_data(r"LibraryData\IgnitionLibrary.ods")
sheet_name = "Sheet1"
sheet_data = data[sheet_name]
library_list = [list(row) for row in sheet_data]
library_array = []

for game in library_list:
    # Check if the row is empty or doesn't have enough elements
    if not game or len(game) < 1:
        continue

    # Unpack the game list and pass the elements as arguments
    try:
        title, sort_title, series, release_date, console, genres, developers, publishers, completion_status, collections, version_name, box_art, launch_path, isCollection, visible_version = game
    except ValueError:
        # Handle the case when there are not enough values to unpack
        # Fill the missing values with empty values of the expected type
        title = ""
        sort_title = ""
        series = ""
        release_date = ""
        console = ""
        genres = ""
        developers = ""
        publishers = ""
        completion_status = ""
        collections = ""
        version_name = ""
        box_art = ""
        launch_path = ""
        isCollection = False
        visible_version = True

    # Parse the JSON-encoded strings back into lists
    try:
        genres = json.loads(genres)
    except ValueError:
        genres = "none"
    try:
        developers = json.loads(developers)
    except ValueError:
        developers =  "none"
    try:
        publishers = json.loads(publishers)
    except ValueError:
        publishers = "none"
        
    collections = collections.split(";")

    library_array.append(Game(
        title,
        sort_title,
        series,
        release_date,
        console,
        genres,
        developers,
        publishers,
        completion_status,
        collections,
        version_name,
        box_art,
        launch_path,
        isCollection,
        visible_version
    ))

def save_library_data(library_array):
    data = []
    for game in library_array:
        collections_string = "".join(game.collections)
        data.append([
            game.title,
            game.sort_title,
            game.series,
            game.release_date,
            game.console,
            json.dumps(game.genres),
            json.dumps(game.developers),
            json.dumps(game.publishers),
            game.completion_status,
            collections_string,
            game.version_name,
            game.box_art,
            game.launch_path,
            game.isCollection,
            game.visible_version
            ])

    sheet_data = {'Sheet1': data}
    save_data(r"LibraryData\IgnitionLibrary.ods", sheet_data)

collections = []
versions = []

collection_focus = ""

def on_enter(event):
    event.widget.configure(borderwidth=0, relief="solid", highlightbackground="light blue", highlightthickness=4)
    global selected_game_index
    selected_game_index = 0

def on_leave(event):
    event.widget.configure(borderwidth=0, relief="flat", highlightbackground="dark blue", highlightthickness=4)

def open_launch_path(game):
    if game.launch_path and os.path.exists(game.launch_path):
        os.startfile(game.launch_path)

def update_grid_with_versions(frame, canvas, sort_title):
    if sort_title != "":
        current_date = date.today()  # Define current_date variable here

        # Destroy the existing grid
        for widget in frame.winfo_children():
            widget.destroy()

        match_sort_title = sort_title

        # Create list to store game versions
        all_versions = []

        # Filter out unpreferred games from library array
        for i, thisgame in enumerate(library_array):
            if thisgame.sort_title == match_sort_title:
                if not thisgame.isCollection:
                    all_versions.append(thisgame)

        # Sort the library_array based on the sort_title attribute
        #sorted_library = sorted(all_versions, key=lambda game: game.sort_title.lower())

        # Sort the library_array based on the sort_title attribute
        sorted_library = sorted(all_versions, key=lambda game: game.sort_title.lower() if game.sort_title else game.title.lower())

        def assign_banner(console):
            try:
                if version.console == console:
                    console_banner_path = r"DefaultImages\Banners\\" + console + ".png"
                    banner = Image.open(console_banner_path).convert("RGBA")
                    banner = banner.resize((600, 120), Image.LANCZOS)
                    image.paste(banner, (0, 0), banner)
            except:
                print(version.title + ": No Banner determined.")

        # Add games and collection entries to grid
        for i, version in enumerate(sorted_library):
            try:
                box_art_path = version.box_art
                image = Image.open(box_art_path).convert("RGBA")
            except:
                image = Image.open(r"DefaultImages\NoImage.png").convert("RGBA")

            consoles = ["PSX", "PS2", "PS3", "PS4", "PS5", "PSP", "PSV", "NES", "SNES", "N64", "NGC", "Wii", "WiiU", "Switch", "GB", "GBC", "GBA", "NDS", "3DS", "XBX", "X360", "PC"]
            
            for con in consoles:
                assign_banner(con)

            # Apply image darkening if release date is after the current date
            try:
                if version.release_date and datetime.strptime(version.release_date, "%Y-%m-%d").date() > current_date:
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(0.3)  # Adjust the brightness factor as needed
            except:
                print(version.title + " Release Date not formatted correctly.")

            image = image.resize((grid_dim_x, grid_dim_y), Image.LANCZOS)
            background = Image.new("RGBA", image.size, (0, 0, 0, 0))
            background.paste(image, (0, 0), image)
            photo = ImageTk.PhotoImage(background)
            label = Label(frame, image=photo, bg=frame.master.cget("bg"), relief="flat",
                          highlightbackground="dark blue", highlightthickness=4, borderwidth=0)  # Set the background to match root window's background color
            label.image = photo  # Store a reference to avoid garbage collection
            label.game = version
            label.bind("<Button-3>", on_right_click)
            label.bind("<Button-1>", on_left_click)
            # Bind the hover events to the label
            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)
            row = i // grid_size
            column = i % grid_size
            label.grid(row=row, column=column, padx=3, pady=3, sticky="nsew")

        # Update the Scrollable Region
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Set the canvas view to the top-left corner
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
    
def update_grid_with_collection(frame, canvas, collection):
    current_date = date.today()  # Define current_date variable here

    collection_focus = collection
    
    # Destroy the existing grid
    for widget in frame.winfo_children():
        widget.destroy()

    collection_array = []

    for i, game in enumerate(library_array):
        if collection in game.collections:
            collection_array.append(game)

    library_prefered = []
        
    #Filter out unprefered games from library array
    for i, game in enumerate(collection_array):
        if game.visible_version != "0":
            library_prefered.append(game)

    #sorted_library = sorted(library_prefered, key=lambda game: game.sort_title.lower())

    # Sort the library_array based on the sort_title attribute
    sorted_library = sorted(library_prefered, key=lambda game: game.sort_title.lower() if game.sort_title else game.title.lower())
        
    #Add games and collection entries to grid
    for i, game in enumerate(sorted_library):
        try:
            box_art_path = game.box_art
            image = Image.open(box_art_path).convert("RGBA")
        except:
            image = Image.open(r"DefaultImages\NoImage.png").convert("RGBA")

        # Apply image darkening if release date is after the current date
        try:
            if game.release_date and datetime.strptime(game.release_date, "%Y-%m-%d").date() > current_date:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(0.3)  # Adjust the brightness factor as needed
        except:
            print(game.title + " Release Date not formatted correctly.")
                    
        image = image.resize((grid_dim_x, grid_dim_y), Image.LANCZOS)
        background = Image.new("RGBA", image.size, (0, 0, 0, 0))
        background.paste(image, (0, 0), image)
        photo = ImageTk.PhotoImage(background)
        label = Label(frame, image=photo, bg=frame.master.cget("bg"), relief="flat", highlightbackground="dark blue", highlightthickness=4, borderwidth=0)  # Set the background to match root window's background color
        label.image = photo  # Store a reference to avoid garbage collection
        label.game = game
        label.bind("<Button-3>", on_right_click)
        label.bind("<Button-1>", on_left_click)
        label.bind("<Button-2>", on_middle_click)
        # Bind the hover events to the label
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        row = i // grid_size
        column = i % grid_size
        label.grid(row=row, column=column, padx=3, pady=3)

    # Update the Scrollable Region
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

collection_map = {}

def update_grid(frame, canvas):
    current_date = date.today()  # Define current_date variable here
    

    global collection_focus
    collection_focus = ""

    # Destroy the existing grid
    for widget in frame.winfo_children():
        widget.destroy()

    # Display loading message while items are still popuplating on the grid
    #loading_label.lift()
    
    root.update()

    if collection_nesting == True:

        #Clear individual games array
        games_in_collections = []

        collections = []

        collection_names = []

        #Create collections from library array
        for i, game in enumerate(library_array):
            if game.isCollection == 1:
                collections.append(game)

        library_prefered = []
        
        #Filter out unprefered games from library array
        for i, game in enumerate(library_array):
            if game.visible_version != "0":
                library_prefered.append(game)

        #Create list of collection names
        for i, game in enumerate(collections):
            collection_names.append(game.title)

        #Parse out what games are in collections
        for i, game in enumerate(library_prefered):
            for col in game.collections:
                if col in collection_names:
                    games_in_collections.append(game)

        individual_games_only = list(set(library_prefered).difference(games_in_collections))
        
        combined_array = individual_games_only #+ collections

        # Sort the library_array based on the sort_title attribute
        sorted_library = sorted(combined_array, key=lambda game: game.sort_title.lower() if game.sort_title else game.title.lower())

        global library_view
        library_view = sorted_library
                
        #Add games and collection entries to grid
        for i, game in enumerate(sorted_library):
            try:
                box_art_path = game.box_art
                image = Image.open(box_art_path).convert("RGBA")
                root.update()
            except:
                # Use a default image instead
                image = Image.open(r"DefaultImages\NoImage.png").convert("RGBA")

                font_size = 54  # Set the desired font size
                title_font = ImageFont.truetype("arial", font_size)

                # Create a new image with the game title overlayed on the default image
                title_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(title_image)
                title_font = ImageFont.truetype("arial", font_size)
                x = 20
                y = 20
                draw.text((x, y), game.title, font=title_font, fill=(255, 255, 255, 255))  # Customize the text color and position as needed
                
                # Composite the title image and the default image
                image = Image.alpha_composite(image, title_image)
                
            # Apply image darkening if release date is after the current date
            try:
                if game.release_date and datetime.strptime(game.release_date, "%Y-%m-%d").date() > current_date:
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(0.3)  # Adjust the brightness factor as needed
            except:
                print(game.title + " Release Date not formatted correctly.")

            image = image.resize((grid_dim_x, grid_dim_y), Image.LANCZOS)
            background = Image.new("RGBA", image.size, (0, 0, 0, 0))
            background.paste(image, (0, 0), image)
            photo = ImageTk.PhotoImage(background)
            label = Label(frame, image=photo, bg=frame.master.cget("bg"), relief="flat", highlightbackground="dark blue", highlightthickness=4, borderwidth=0)  # Set the background to match root window's background color
            label.image = photo  # Store a reference to avoid garbage collection
            label.game = game
            label.bind("<Button-3>", on_right_click)
            label.bind("<Button-1>", on_left_click)
            label.bind("<Button-2>", on_middle_click)
            # Bind the hover events to the label
            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)
            row = i // grid_size
            column = i % grid_size
            label.grid(row=row, column=column, padx=3, pady=3)
            
    if collection_nesting == False:
        # Create a grid layout
        for i, game in enumerate(library_array):
            # Get the box art path from the game object
            box_art_path = game.box_art

            # Open the image with alpha channel
            image = Image.open(box_art_path).convert("RGBA")
            image = image.resize((grid_dim_x, grid_dim_y), Image.LANCZOS)

            # Create a transparent background
            background = Image.new("RGBA", image.size, (0, 0, 0, 0))
            background.paste(image, (0, 0), image)

            # Convert the image to Tkinter PhotoImage with transparency
            photo = ImageTk.PhotoImage(background)

            # Create a Label widget to display the image
            label = Label(frame, image=photo, bg=frame.master.cget("bg"))  # Set the background to match root window's background color
            label.image = photo  # Store a reference to avoid garbage collection

            # Calculate the row and column positions in the grid
            row = i // grid_size
            column = i % grid_size

            # Position the label in the grid
            label.grid(row=row, column=column, padx=5, pady=5)

    # Update the Scrollable Region
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    loading_label.lower()
    root.update()

    global stored_grid
    stored_grid = frame

global canvas

def load_stored_grid():
    global stored_grid
    if stored_grid:
        # Remove the existing grid from the main grid frame
        for widget in grid_frame.grid_slaves():
            widget.grid_remove()

        # Add the stored grid back to the main grid frame
        stored_grid.grid(row=0, column=0, sticky="nsew")

        # Verify the contents of the grid
        for widget in stored_grid.grid_slaves():
            print(widget.game.title)

def AddGameWizard():
    print("Adding New Game")
    if collection_focus == "":
        # Create a new game object and append it to the library_array
        new_game = Game("New Game", "", "", "", "", [""], [""], [""], "", [""], "", "", "", False, True)
        library_array.append(new_game)
        #update_grid(inner_frame, canvas)
        open_editor(new_game, inner_frame, canvas)
    else:
        # Create a new game object and append it to the library_array
        new_game = Game("New Game", "", "", "", "", [""], [""], [""], "", [collection_focus], "", "", "", False, True)
        library_array.append(new_game)
        #update_grid_with_collection(inner_frame, canvas, collection_focus)
        open_editor(new_game, inner_frame, canvas)

def AddCollectionWizard():
    print("Adding New Collection")
    # Create a new game object and append it to the library_array
    new_game = Game("New Collection", "", "", "", "", [""], [""], [""], "", [""], "", "", "", True, True)
    library_array.append(new_game)
    update_grid(inner_frame, canvas)

def open_editor(game, grid_frame, canvas):
    # Create a new window for editing
    global editor_window
    editor_window = Toplevel(root)
    if game.isCollection != True:
        editor_window.title("Edit Game")
    else:
        editor_window.title("Edit Collection")
    editor_window.configure(background="dark blue")

    # Create a frame to hold the labels and entry fields
    editor_frame = Frame(editor_window)
    editor_frame.configure(background="dark blue")
    editor_frame.pack(padx=10, pady=10)

    # Create lists to hold the labels and entry fields
    labels = []
    entry_fields = []

    if game.isCollection != True:
        # Create labels and entry fields for each game attribute
        attribute_names = [
            "Title", "Sort Title", "Series", "Release Date", "Console",
            "Genres", "Developers", "Publishers", "Completion Status",
            "Collections", "Version Name", "Box Art", "Launch Path", "Preffered Version"
        ]
    else:
        # Create labels and entry fields for each game attribute
        attribute_names = [
            "Title", "Sort Title", "Box Art"
        ]


    for i, attribute_name in enumerate(attribute_names):
        # Create a label
        label = Label(editor_frame, text=attribute_name + ":")
        label.configure(background="dark blue", fg="white")
        label.grid(row=i, column=0, sticky="e")
        labels.append(label)

        # Create an entry field
        entry_field = Entry(editor_frame, width=30)
        entry_field.grid(row=i, column=1, padx=5, pady=5)
        entry_field.configure(background="dark blue", fg="white")
        entry_fields.append(entry_field)

    if game.isCollection != True:
        # Populate the entry fields with the game data
        collections_str = ";".join(game.collections)
        entry_fields[0].insert(0, game.title)
        entry_fields[1].insert(0, game.sort_title)
        entry_fields[2].insert(0, game.series)
        entry_fields[3].insert(0, game.release_date)
        entry_fields[4].insert(0, game.console)
        entry_fields[5].insert(0, game.genres)
        entry_fields[6].insert(0, game.developers)
        entry_fields[7].insert(0, game.publishers)
        entry_fields[8].insert(0, game.completion_status)
        entry_fields[9].insert(0, collections_str)
        entry_fields[10].insert(0, game.version_name)
        entry_fields[11].insert(0, game.box_art)
        entry_fields[12].insert(0, game.launch_path)
        entry_fields[13].insert(0, game.visible_version)
    else:
        entry_fields[0].insert(0, game.title)
        entry_fields[1].insert(0, game.sort_title)
        entry_fields[2].insert(0, game.box_art)
            

    # Function to handle drop event
    def handle_drop(event):
        file_path = event.data.strip("{}")

        if game.isCollection!= True:
            # Update the "Box Art" field with the dropped image file path
            entry_fields[11].delete(0, "end")
            entry_fields[11].insert(0, file_path)
        else:
            entry_fields[2].delete(0, "end")
            entry_fields[2].insert(0, file_path)

    # Configure drop event handling for the editor window
    editor_window.drop_target_register(DND_FILES)
    editor_window.dnd_bind("<<Drop>>", handle_drop)

    # Create a save button
    save_button = Button(
        editor_window,
        text="Save Changes",
        fg="dark blue",
        command=lambda: save_changes(game, entry_fields, editor_window, grid_frame, canvas)
    )
    save_button.configure(background="light blue")
    save_button.pack(pady=10)

##########

    if game.isCollection!= True:
        title_entry = entry_fields[0]  # Assuming it's the first entry field (index 0)
        box_art_textbox = entry_fields[11]  # Assuming it's the 12th entry field (index 11)
    else:
        title_entry = entry_fields[0]  # Assuming it's the first entry field (index 0)
        box_art_textbox = entry_fields[2]  # Assuming it's the 12th entry field (index 11)
        
    box_art_button = Button(
        editor_window,
        text="Find Box Art",
        fg="dark blue",
        command=lambda: download_new_box_art(game, box_art_textbox, title_entry)
    )


##########
    # Create a download box art button
    box_art_button.configure(background="light blue")
    box_art_button.pack(pady=10)

    #Create Delete Button
    delete_button = Button(
        editor_window,
        text="Delete Game",
        fg="white",
        command=lambda: delete_item(game, entry_fields, editor_window, grid_frame, canvas)
    )
    delete_button.configure(background="red")
    delete_button.pack(padx=10)

    # Disable resizing of the editor window
    editor_window.resizable(False, False)

def get_box_art(game_title):
    from steamgrid import StyleType, PlatformType, MimeType, ImageType
    
    sgdb = SteamGridDB('d8bce3b83a25d534a467cad96450a20b')

    result = sgdb.search_game(game_title)

    gameid = result[0].id

    grids = sgdb.get_grids_by_gameid([gameid])

    foundpics = []

    for grid in grids:
        if grid.height == 900 and grid.width == 600:
            url = grid
            foundpics.append(url)

    chosen_url = random.choice(foundpics)
    image = requests.get(chosen_url, stream=True).raw
    print(chosen_url)
    img = Image.open(image)
    imagepath = os.path.join(r"BoxArt_Scraped", game_title + '.png')
    img.save(imagepath)
    return imagepath

def delete_item(g, entry_fields, editor_window, grid_frame, canvas):
    global library_array
    global collection_focus
    data = []
    for game in library_array:
        if game != g:
            collections_string = "".join(game.collections)
            data.append([
                game.title,
                game.sort_title,
                game.series,
                game.release_date,
                game.console,
                json.dumps(game.genres),
                json.dumps(game.developers),
                json.dumps(game.publishers),
                game.completion_status,
                collections_string,
                game.version_name,
                game.box_art,
                game.launch_path,
                game.isCollection,
                game.visible_version
                ])

    sheet_data = {'Sheet1': data}
    save_data(r"LibraryData\IgnitionLibrary.ods", sheet_data)

    # Retrieve the game library from the ods file
    data = get_data(r"LibraryData\IgnitionLibrary.ods")
    sheet_name = "Sheet1"
    sheet_data = data[sheet_name]
    library_list = [list(row) for row in sheet_data]
    library_array = []

    for game in library_list:
        # Check if the row is empty or doesn't have enough elements
        if not game or len(game) < 1:
            continue

        # Unpack the game list and pass the elements as arguments
        try:
            title, sort_title, series, release_date, console, genres, developers, publishers, completion_status, collections, version_name, box_art, launch_path, isCollection, visible_version = game
        except ValueError:
            # Handle the case when there are not enough values to unpack
            # Fill the missing values with empty values of the expected type
            title = ""
            sort_title = ""
            series = ""
            release_date = ""
            console = ""
            genres = ""
            developers = ""
            publishers = ""
            completion_status = ""
            collections = ""
            version_name = ""
            box_art = ""
            launch_path = ""
            isCollection = False
            visible_version = True

        # Parse the JSON-encoded strings back into lists
        try:
            genres = json.loads(genres)
        except ValueError:
            genres = "none"
        try:
            developers = json.loads(developers)
        except ValueError:
            developers =  "none"
        try:
            publishers = json.loads(publishers)
        except ValueError:
            publishers = "none"
            
        collections = collections.split(";")

        library_array.append(Game(
            title,
            sort_title,
            series,
            release_date,
            console,
            genres,
            developers,
            publishers,
            completion_status,
            collections,
            version_name,
            box_art,
            launch_path,
            isCollection,
            visible_version
        ))

    if collection_focus == "":
        update_grid(inner_frame, canvas)
    else:
        update_grid_with_collection(inner_frame, canvas, collection_focus)
    # Refresh the home grid
    #update_grid(inner_frame, canvas)

    # Close the editor window
    editor_window.destroy()
    
def save_changes(game, entry_fields, editor_window, grid_frame, canvas):
    #Retrieve the updated values from the entry fields
    updated_values = [entry_field.get() for entry_field in entry_fields]

    if game.isCollection != True:
        # Update the game object with the new values
        game.title = updated_values[0]
        game.sort_title = updated_values[1]
        game.series = updated_values[2]
        game.release_date = updated_values[3]
        game.console = updated_values[4]
        game.genres = updated_values[5]
        game.developers = updated_values[6]
        game.publishers = updated_values[7]
        game.completion_status = updated_values[8]
        game.collections = [";".join(updated_values[9].split(";"))]
        #game.collections = updated_values[9]
        game.version_name = updated_values[10]
        game.box_art = updated_values[11]
        game.launch_path = updated_values[12]
        game.visible_version = updated_values[13]
    else:
        # Update the collection object with new values
        game.title = updated_values[0]
        game.sort_title = updated_values[1]
        game.box_art = updated_values[2]

    save_library_data(library_array)

    if game.collections == "":
        # Refresh the home grid
        update_grid(inner_frame, canvas)
    else:
        # Refresh the collection grid
        update_grid_with_collection(inner_frame, canvas, game.collections[0])

    # Close the editor window
    editor_window.destroy()

def download_new_box_art(game, box_art_textbox, title_entry):
    # Retrieve the current game title from the entry field
    game_title = title_entry.get()

    # Use the function to get new box art
    new_box_art_path = get_box_art(game_title)

    # Update the game object
    if new_box_art_path is not None:
        game.box_art = new_box_art_path

        # Update the text box in the editor window
        box_art_textbox.delete(0, "end")  # Clear the existing content
        box_art_textbox.insert(0, game.box_art)  # Insert the new box art path

        if game.collections == "":
            update_grid(inner_frame, canvas)
        else:
            update_grid_with_collection(inner_frame, canvas, game.collections[0])
        editor_window.update()



def on_right_click(event):
    # Find the clicked label widget
    clicked_label = event.widget

    # Get the game object stored as an attribute of the label widget
    game = clicked_label.game

    # Open the editing window for the selected game
    open_editor(game, grid_frame, canvas)

    # This stops further propagation of the event.
    return "break"

def on_right_click_elsewhere(event):
    # Refresh the grid
    #load_stored_grid()
    #root.update()
    update_grid(inner_frame, canvas)
    collection_focus = ""

def on_left_click(event):
    # Find the clicked label widget
    clicked_label = event.widget

    # Get the game object stored as an attribute of the label widget
    game = clicked_label.game

    if game.isCollection:
        update_grid_with_collection(inner_frame, canvas, game.title)
        global collection_focus
        collection_focus = game.title
    else:
        # Launch the game
        open_launch_path(game)

def on_middle_click(event):
    # Find the clicked label widget
    clicked_label = event.widget

    # Get the game object stored as an attribute of the label widget
    game = clicked_label.game

    update_grid_with_versions(inner_frame, canvas, game.sort_title)
        
root = TkinterDnD.Tk()
root.title("Ignition")

root.drop_target_register(DND_FILES)

root.configure(background="dark blue")

#root.minsize(1920, 1010)
#root.maxsize(1920, 1010)

root.state("zoomed")

root.update()

loading_image = PhotoImage(file=r"DefaultImages\loadicon.png")
loading_label = Label(root, image=loading_image)
loading_label.place(relx=0.5, rely=0.5, anchor="center")

# You can bind the new function to the root object
root.bind("<Button-3>", on_right_click_elsewhere)

# Get the window width for the Grid
window_width = root.winfo_width()

# Grid Item Dimensions
grid_dim_x = 176
grid_dim_y = 264

# Number of columns in the grid
grid_size = math.floor(window_width/(grid_dim_x + 5))

# Padding or empty rows before the grid
padding_rows = 2

# Set Collection Nesting
collection_nesting = True

###############################################################################################################
def process_xinput():
    global selected_game_index
    global scroll_position
    global library_view
    # Get events from the gamepad.
    for event in get_gamepad():
        if event.code == 'ABS_HAT0X':
            if event.state < 0:
                # D-pad moved left
                selected_game_index -= 1 #max(0, selected_game_index - 1)
                print("left")
            elif event.state > 0:
                # D-pad moved right
                selected_game_index += 1 #min(len(library_view) - 1, selected_game_index + 1)
                print("right")
        if event.code == 'ABS_HAT0Y':
            if event.state < 0:
                # D-pad moved up
                selected_game_index -= grid_size
                print("up")
            elif event.state > 0:
                # D-pad moved down
                selected_game_index += grid_size
                print("down")

            # Update the scroll position if necessary.
            if selected_game_index - scroll_position >= 5:
                scroll_position += 1
            elif selected_game_index - scroll_position <= -5:
                scroll_position -= 1

            # Update the GUI with the new selected game and scroll position.
            update_gui()


def update_gui():
    # Here is where you need to update the visual aspect of your application.
    # Highlight the new selected game, unhighlight the old selected game,
    # scroll the window, etc.
    global selected_game_index
    print(selected_game_index)
    pass

###############################################################################################################

# Define the initial state of the top bar
top_bar_visible = True

# Set View Top Bar
view_top_bar = True

# Create the top bar
if view_top_bar:
    # Create a game button above the grid
    add_game_button = Button(root, text="Add Game", width=10, command=AddGameWizard)
    add_game_button.grid(row=padding_rows, column=0, columnspan=grid_size, padx=5, pady=5, sticky="nw")
    # Create a collection button above the grid
    add_collection_button = Button(root, text="Add Collection", width=15, command=AddCollectionWizard)
    add_collection_button.grid(row=padding_rows, column=1, columnspan=grid_size, padx=5, pady=5, sticky="nw")

def toggle_top_bar():
    global top_bar_visible
    if top_bar_visible:
        add_game_button.grid_forget()
        add_collection_button.grid_forget()
        top_bar_visible = False
    else:
        add_game_button.grid(row=padding_rows, column=0, columnspan=grid_size, padx=5, pady=5, sticky="nw")
        add_collection_button.grid(row=padding_rows, column=1, columnspan=grid_size, padx=5, pady=5, sticky="nw")
        top_bar_visible = True

def handle_insert_key(event):
    if event.keysym == "Insert":
        toggle_top_bar()

# Bind the Insert key to toggle the top bar
root.bind("<Key>", handle_insert_key)

is_fullscreen = False

def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        root.minsize(1, 1)  # remove size constraints for fullscreen
        root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())  # remove size constraints for fullscreen
        root.attributes('-fullscreen', True)
    else:
        root.attributes('-fullscreen', False)
        root.geometry("1920x1080")  # set size when in window mode
        root.minsize(640, 480)  # set minsize when in window mode
        root.maxsize(1920, 1080)  # set maxsize when in window mode

root.bind("<F11>", toggle_fullscreen)

# Set View Top Bar
view_top_bar = True
# Configure root to expand grid_frame
root.grid_rowconfigure(padding_rows + 1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create a frame to hold the grid
grid_frame = Frame(root)
grid_frame.configure(background='dark blue')  # Set the background to match root window's background color
grid_frame.grid(row=padding_rows + 1, column=0, columnspan=grid_size)

# Configure grid_frame to expand with the window
grid_frame.grid_rowconfigure(0, weight=1)
grid_frame.grid_columnconfigure(0, weight=1)

# Create a canvas widget for the grid frame
canvas = Canvas(grid_frame, width=root.winfo_width() - 20, height=root.winfo_height() - 2, background=root.cget("bg"), name="canvas")
canvas.grid(row=0, column=0, sticky="nsew")  # Use grid manager instead of pack

# Now the canvas should expand and shrink with the window

# Create a scrollbar widget and associate it with the canvas
scrollbar = Scrollbar(grid_frame, orient="vertical", command=canvas.yview)  # style="CustomScrollbar.TScrollbar"
scrollbar.grid(row=0, column=1, sticky="ns")  # Use grid manager instead of pack
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas to hold the grid
inner_frame = Frame(canvas)
inner_frame.configure(background='dark blue')

# Use grid manager for inner_frame and make sure it stretches with the grid
inner_frame.grid(row=0, column=0, sticky="nsew")
for i in range(grid_size):
    inner_frame.grid_columnconfigure(i, weight=1)
    inner_frame.grid_rowconfigure(i, weight=1)

canvas.create_window((0, 0), window=inner_frame, anchor="nw")

# Update the canvas's scrollregion whenever the size of the inner_frame changes
inner_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Update root so that grid can be navigated while images are loading
root.update()

# Call the function to display the initial images
update_grid(inner_frame, canvas)

def smooth_scroll(event):
    units_to_move = 1  # Total scroll distance for a single mouse wheel event
    if event.delta > 0:
        direction = -1
    else:
        direction = 1

    def scroll_step(remaining_steps):
        if remaining_steps > 0:
            canvas.yview_scroll(direction, "units")
            root.after(500, scroll_step, remaining_steps - 1)

    scroll_step(units_to_move)

canvas.bind_all("<MouseWheel>", smooth_scroll)

def start_xinput():
    process_xinput()
    root.after(100, start_xinput)  # Call the function again after 100 ms.

# Call the function for the first time to start the loop.
#start_xinput()
    
root.mainloop()