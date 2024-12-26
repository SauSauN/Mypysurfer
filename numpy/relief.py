import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
from PIL import Image, ImageTk  # Pillow for extended image support
import os

# Create the database table
def create_table():
    conn = sqlite3.connect("images.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image BLOB
        )
    """)
    conn.commit()
    conn.close()

# Insert an image into the database
def insert_image():
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.gif")])
    if not filepath:
        return

    # Read the image as binary data
    with open(filepath, "rb") as file:
        image_data = file.read()

    # Insert the image into the database
    conn = sqlite3.connect("images.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO photos (name, image) VALUES (?, ?)", (os.path.basename(filepath), image_data))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Image added to the database!")

# Display images from the database
def display_images():
    conn = sqlite3.connect("images.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, image FROM photos")
    records = cursor.fetchall()
    conn.close()

    # Display each image
    for idx, (name, image_data) in enumerate(records):
        temp_file = f"temp_image_{idx}.jpg"  # Use a temporary file to store the image

        # Save binary data as an image file
        with open(temp_file, "wb") as file:
            file.write(image_data)

        # Open the image with Pillow
        try:
            pil_image = Image.open(temp_file)
            img = ImageTk.PhotoImage(pil_image)

            # Create a label to display the image
            label = tk.Label(root, text=name, image=img, compound="top")
            label.image = img  # Keep a reference to avoid garbage collection
            label.pack()
        except Exception as e:
            print(f"Failed to load image {name}: {e}")
        
        # Clean up the temporary file after displaying
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Create the main Tkinter window
root = tk.Tk()
root.title("Image Database Viewer")

# Create the database table
create_table()

# Buttons for adding and displaying images
add_button = tk.Button(root, text="Add Image", command=insert_image)
add_button.pack()

display_button = tk.Button(root, text="Display Images", command=display_images)
display_button.pack()

# Run the Tkinter main loop
root.mainloop()
