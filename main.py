import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
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

        #show image
        image_label.pack(pady=20)
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
            textToShow="Ambiguity among following numbers: " + " , ".join(numberplateSet)
        
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
window.geometry("550x500")

# Create a frame to hold the buttons
button_frame = ttk.Frame(window)
button_frame.pack(pady=20)


# Create a button for image upload
upload_button = ttk.Button(button_frame, text="Upload Image", command=upload_image)
upload_button.pack(side="left", padx=10)

# Create a button to display dummy text (initially hidden)
show_text_button = ttk.Button(button_frame, text="Show Text", command=display_text)
show_text_button.pack(side="left", padx=10)
show_text_button.pack_forget()

# Create a label to display the uploaded image
image_label = ttk.Label(window)
image_label.pack(pady=20)
image_label.pack_forget()

# Create a label to display the text
text_label = ttk.Label(window, text="", style='Result.TLabel')
text_label.pack(pady=20)
text_label.pack_forget()


# add some styling
theme=ttk.Style()
theme.theme_use('clam')
theme.configure("TButton",
                      padding=8,
                      relief="flat",
                      background="#55f",
                      foreground="#fff")
theme.configure("Result.TLabel",
                padding=6,
                background="#f50",
                foreground="#fff",
                font=('Helvetica', 13))
theme.map("TButton",
    foreground=[('pressed', '#fff'), ('active', '#55f')],
    background=[('pressed', '!disabled', '#ccc'), ('active', 'white')]
    )

# Start the main event loop
window.mainloop()
