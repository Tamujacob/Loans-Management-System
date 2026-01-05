from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk  
import database
import subprocess
import bcrypt
import os
import sys

# --- Main Login Logic ---
def verify_login(username, password):
    """Checks credentials against MongoDB users collection using bcrypt."""
    if database.db is None:
        messagebox.showerror("Connection Error", "Database not connected.")
        return False
    
    try:
        user_doc = database.db['users'].find_one({"username": username})
        if user_doc:
            stored_hash = user_doc.get('password_hash', '').encode('utf-8')
            input_password_bytes = password.encode('utf-8')
            if bcrypt.checkpw(input_password_bytes, stored_hash):
                return True
        return False
    except Exception as e:
        messagebox.showerror("Database Error", f"Verification error: {e}")
        return False

def handle_login(window, user_entry, pass_entry):
    """Handles the login button click."""
    user = user_entry.get()
    passw = pass_entry.get()

    if verify_login(user, passw):
        messagebox.showinfo("Login Successful", f"Welcome, {user}!")
        window.destroy()
        try:
            subprocess.Popen([sys.executable, "dashboard.py"])
        except Exception:
            messagebox.showerror("Error", "Could not find 'dashboard.py'.")
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password!")

# --- GUI SETUP ---
window = Tk()
window.title("Loan Management System - Secure Login")
window.geometry("900x550")
window.resizable(False, False)
window.configure(bg="white")

# --- SET WINDOW TITLE BAR ICON ---
try:
    title_icon = PhotoImage(file="bu logo.png")
    window.iconphoto(True, title_icon)
except Exception as e:
    print(f"Title bar icon could not be loaded: {e}")

# Theme Colors
PRIMARY_GREEN = "#2ecc71"
DARK_TEXT = "#2c3e50"
GRAY_TEXT = "#7f8c8d"

window.grid_columnconfigure(0, weight=1) 
window.grid_columnconfigure(1, weight=1) 
window.grid_rowconfigure(0, weight=1)

# --- LEFT SIDE: LOGO PANEL ---
left_panel = Frame(window, bg=PRIMARY_GREEN)
left_panel.grid(row=0, column=0, sticky="nsew")

try:
    img = Image.open("bu logo.png")
    img = img.resize((320, 320), Image.Resampling.LANCZOS)
    logo_img = ImageTk.PhotoImage(img)
    logo_label = Label(left_panel, image=logo_img, bg=PRIMARY_GREEN)
    logo_label.place(relx=0.5, rely=0.5, anchor=CENTER)
except Exception:
    Label(left_panel, text="BUSINESS\nLOGO", fg="white", 
          bg=PRIMARY_GREEN, font=("Arial", 28, "bold")).place(relx=0.5, rely=0.5, anchor=CENTER)

# --- RIGHT SIDE: LOGIN FORM ---
right_panel = Frame(window, bg="white")
right_panel.grid(row=0, column=1, sticky="nsew")

form_box = Frame(right_panel, bg="white")
form_box.place(relx=0.5, rely=0.5, anchor=CENTER)

Label(form_box, text="System Login", font=("Arial", 24, "bold"), 
      bg="white", fg=DARK_TEXT).pack(pady=(0, 5))
Label(form_box, text="Authorized Personnel Only", font=("Arial", 10), 
      bg="white", fg=GRAY_TEXT).pack(pady=(0, 30))

# Username Field
Label(form_box, text="Username", bg="white", font=("Arial", 10, "bold"), fg=DARK_TEXT).pack(anchor="w")
user_entry = Entry(form_box, font=("Arial", 12), width=35, bd=0, highlightthickness=1)
user_entry.config(highlightbackground="#dcdde1", highlightcolor=PRIMARY_GREEN)
user_entry.pack(pady=(5, 20), ipady=8)

# Password Field
Label(form_box, text="Password", bg="white", font=("Arial", 10, "bold"), fg=DARK_TEXT).pack(anchor="w")
pass_entry = Entry(form_box, font=("Arial", 12), width=35, show="*", bd=0, highlightthickness=1)
pass_entry.config(highlightbackground="#dcdde1", highlightcolor=PRIMARY_GREEN)
pass_entry.pack(pady=(5, 30), ipady=8)

# Login Button
login_btn = Button(form_box, text="LOG IN", bg=PRIMARY_GREEN, fg="white", 
                   font=("Arial", 12, "bold"), width=32, height=2, bd=0,
                   cursor="hand2", command=lambda: handle_login(window, user_entry, pass_entry))
login_btn.pack(pady=10)

# Binding Enter Key
window.bind('<Return>', lambda event: handle_login(window, user_entry, pass_entry))

if database.db is None:
    messagebox.showwarning("Database Warning", "MongoDB connection failed.")

window.mainloop()