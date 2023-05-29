import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from numberplate_identifier import identify

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

def display_text():
    global file_path
    if file_path:
        numberplateSet=identify(file_path)
        
        if len(numberplateSet)==0 :
            textToShow="Could not detect number"
        elif len(numberplateSet)==1:
            textToShow="Number plate detected: " + str(numberplateSet.pop())
        else:
            textToShow="Ambiguity among following numbers: " + ",".join(numberplateSet)
        
        # set value and ;show text label
        text_label.configure(text= textToShow )
        text_label.pack()
        # reset file path and hide show text button so that its shown only if another image selected
        file_path=None
        show_text_button.pack_forget()
        
# global variable for access across 
file_path=None
        
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
show_text_button = tk.Button(button_frame, text="Show Text", command=display_text)
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
