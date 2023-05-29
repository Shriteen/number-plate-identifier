import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

def upload_image():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[
        ("image", ".jpeg"), ("image", ".png"), ("image", ".jpg"),
        ("image", ".jp2"), ("image", ".bmp"), ("image", ".webp"),
        ("image", ".tiff")
    ])
    
    if file_path:
        # Display the uploaded image
        uploaded_image = Image.open(file_path)
        uploaded_image.thumbnail((400, 400))  # fitting image
        image_label.configure(image=None)
        image_label.image = ImageTk.PhotoImage(uploaded_image)
        image_label.configure(image=image_label.image)

        #hide text label
        text_label.pack_forget()
        # Show the "Show Text" button
        show_text_button.pack()

def display_dummy_text():
    dummy_text = input("Enter text.")
    text_label.configure(text=dummy_text)

# Create the main window
window = tk.Tk()
window.title("Automatic Number Plate Detection")
window.geometry("550x400")

# Create a frame to hold the buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=20)

# Create a button for image upload
upload_button = tk.Button(button_frame, text="Upload Image", command=upload_image)
upload_button.pack(side="left", padx=10)

# Create a button to display dummy text (initially hidden)
show_text_button = tk.Button(button_frame, text="Show Text", command=display_dummy_text)
show_text_button.pack(side="left", padx=10)
show_text_button.pack_forget()

# Create a label to display the uploaded image
image_label = tk.Label(window)
image_label.pack()

# Create a label to display the text
text_label = tk.Label(window, text="")
text_label.pack(pady=20)

# Start the main event loop
window.mainloop()
