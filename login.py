from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk  
import database
import subprocess
import bcrypt
import os
import sys

# --- LOGIN LOGIC ---
def handle_login(window, user_entry, pass_entry):
    """Handles the login button click, verifies role, and launches dashboard."""
    username = user_entry.get().strip()
    password = pass_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    if database.db is None:
        messagebox.showerror("Connection Error", "Database not connected. Please check your MongoDB service.")
        return

    try:
        # 1. Look up the user by username
        user_doc = database.db['users'].find_one({"username": username})
        
        if user_doc:
            # 2. Extract hashed password from DB
            stored_hash = user_doc.get('password_hash', '').encode('utf-8')
            
            # 3. Verify password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                # 4. Password Correct! Fetch Role and Name
                user_role = user_doc.get('role', 'Staff')
                full_name = user_doc.get('full_name', username)
                
                # LOGGING THE ACTIVITY
                database.log_activity(full_name, "Login", "User successfully logged into the system")
                
                messagebox.showinfo("Login Successful", f"Welcome back, {full_name}!")
                
                # 5. Launch Dashboard
                window.destroy()
                try:
                    subprocess.Popen([sys.executable, "dashboard.py", user_role, full_name])
                except Exception as e:
                    messagebox.showerror("Error", f"Could not launch dashboard: {e}")
            else:
                messagebox.showerror("Login Failed", "Invalid Username or Password!")
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password!")

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

# --- GUI SETUP ---
window = Tk()
window.title("Loan Management System - Secure Login")
window.geometry("900x550")
window.resizable(False, False)
window.configure(bg="white")

# Center window on screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width/2) - (900/2)
y = (screen_height/2) - (550/2)
window.geometry('%dx%d+%d+%d' % (900, 550, x, y))

# SET WINDOW TITLE BAR ICON 
try:
    title_icon = PhotoImage(file="bu logo.png")
    window.iconphoto(True, title_icon)
except Exception:
    pass

# Theme Colors
PRIMARY_GREEN = "#2ecc71"
DARK_TEXT = "#2c3e50"
GRAY_TEXT = "#7f8c8d"

window.grid_columnconfigure(0, weight=1) 
window.grid_columnconfigure(1, weight=1) 
window.grid_rowconfigure(0, weight=1)

# LEFT SIDE: LOGO PANEL 
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
          bg=PRIMARY_GREEN, font=("Segoe UI", 28, "bold")).place(relx=0.5, rely=0.5, anchor=CENTER)

# RIGHT SIDE: LOGIN FORM 
right_panel = Frame(window, bg="white")
right_panel.grid(row=0, column=1, sticky="nsew")

form_box = Frame(right_panel, bg="white")
form_box.place(relx=0.5, rely=0.5, anchor=CENTER)

Label(form_box, text="System Login", font=("Segoe UI", 24, "bold"), 
      bg="white", fg=DARK_TEXT).pack(pady=(0, 5))
Label(form_box, text="Enter your credentials to continue", font=("Segoe UI", 10), 
      bg="white", fg=GRAY_TEXT).pack(pady=(0, 30))

# Username Field
Label(form_box, text="Username", bg="white", font=("Segoe UI", 10, "bold"), fg=DARK_TEXT).pack(anchor="w")
user_entry = Entry(form_box, font=("Segoe UI", 12), width=35, bd=0, highlightthickness=1)
user_entry.config(highlightbackground="#dcdde1", highlightcolor=PRIMARY_GREEN)
user_entry.pack(pady=(5, 20), ipady=8)

# Password Field
Label(form_box, text="Password", bg="white", font=("Segoe UI", 10, "bold"), fg=DARK_TEXT).pack(anchor="w")
pass_entry = Entry(form_box, font=("Segoe UI", 12), width=35, show="*", bd=0, highlightthickness=1)
pass_entry.config(highlightbackground="#dcdde1", highlightcolor=PRIMARY_GREEN)
pass_entry.pack(pady=(5, 30), ipady=8)

# Login Button
login_btn = Button(form_box, text="LOG IN", bg=PRIMARY_GREEN, fg="white", 
                    font=("Segoe UI", 12, "bold"), width=32, height=2, bd=0,
                    cursor="hand2", command=lambda: handle_login(window, user_entry, pass_entry))
login_btn.pack(pady=10)

# --- FINAL INITIALIZATION ---

# Binding Enter Key for better UX
window.bind('<Return>', lambda event: handle_login(window, user_entry, pass_entry))

# Final check for DB connection before allowing interactions
if database.db is None:
    messagebox.showwarning("Database Warning", "MongoDB connection failed. Ensure your database is running.")



# Start the application loop
window.mainloop()