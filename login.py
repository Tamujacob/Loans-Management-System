from tkinter import *
from tkinter import messagebox
import database
import subprocess
import bcrypt # Essential for password hashing/verification

# --- Navigation Function ---
def open_create_account(current_window):
    """Closes the current window and opens the create account script."""
    # Note: Assumes 'create account.py' exists and is in the same directory.
    current_window.destroy()
    try:
        subprocess.Popen(["python", "create account.py"])
    except FileNotFoundError:
        messagebox.showerror("Error", "Could not find 'create account.py'.")

# --- Main Login Logic ---
def verify_login(username, password, window):
    """
    Checks credentials against the MongoDB 'users' collection using bcrypt 
    for secure password verification.
    """
    if database.db is None:
        messagebox.showerror("Connection Error", "Database not connected. Cannot log in.")
        return False

    try:
        # 1. Find the user by username
        # database.db['users'] is the MongoDB collection object
        user_doc = database.db['users'].find_one({"username": username})

        if user_doc:
            # 2. User found: Verify the hashed password
            # Passwords are stored as bytes, so we encode the stored hash and the input password
            stored_hash = user_doc.get('password_hash', '').encode('utf-8')
            input_password_bytes = password.encode('utf-8')

            # bcrypt.checkpw compares the raw password to the stored hash
            if bcrypt.checkpw(input_password_bytes, stored_hash):
                return True # Login successful
            else:
                return False # Password mismatch
        else:
            # 3. User not found
            return False
            
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred during login verification: {e}")
        return False

def login():
    """Handles button press, attempts to log in, and navigates on success."""
    user = user_entry.get()
    passw = pass_entry.get()

    if verify_login(user, passw, window):
        messagebox.showinfo("Login Successful", f"Welcome, {user}!")
        window.destroy()  # Close login window
        try:
            # Note: Assumes 'dashboard.py' exists and is in the same directory.
            subprocess.Popen(["python", "dashboard.py"])  # Open dashboard
        except FileNotFoundError:
            messagebox.showerror("Error", "Login successful, but could not find 'dashboard.py'.")
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password!")

# ----------------------------------------------------
# --- GUI SETUP ---

# Create main window
window = Tk()
window.title("Loan Management System - Login")
window.geometry("500x400") 
window.configure(bg="#2c3e50") # Dark background for modern look

# Check DB connection status on launch
if database.db is None:
    messagebox.showwarning("DB Warning", "Could not connect to MongoDB. Login function will rely on DB connection. Please check database.py.")

# Center Frame (Enhanced Styling)
frame = Frame(window, bg="white", padx=40, pady=40, relief="raised", bd=5)
frame.place(relx=0.5, rely=0.5, anchor=CENTER)

# Title Label (Enhanced)
Label(
    frame, 
    text="👤 System Login", 
    font=("Arial", 20, "bold"), 
    bg="white", 
    fg="#34495e"
).grid(row=0, column=0, columnspan=2, pady=(0, 20))

# Username Label & Entry
Label(
    frame, 
    text="Username:", 
    font=("Arial", 12), 
    bg="white"
).grid(row=1, column=0, sticky="w", padx=5, pady=10)
user_entry = Entry(frame, font=("Arial", 12), width=25, bd=1, relief=SUNKEN)
user_entry.grid(row=1, column=1, padx=5, pady=10, ipady=3)

# Password Label & Entry
Label(
    frame, 
    text="Password:", 
    font=("Arial", 12), 
    bg="white"
).grid(row=2, column=0, sticky="w", padx=5, pady=10)
pass_entry = Entry(frame, font=("Arial", 12), width=25, show="*", bd=1, relief=SUNKEN)
pass_entry.grid(row=2, column=1, padx=5, pady=10, ipady=3)

# Login Button
log_button = Button(
    frame, 
    text="LOGIN", 
    font=("Arial", 12, "bold"), 
    bg="#2980b9", # Blue color
    fg="white", 
    activebackground="#3498db",
    width=20, 
    command=login
)
log_button.grid(row=3, column=0, columnspan=2, pady=15)

# Create Account Button/Link
create_account_btn = Button(
    frame, 
    text="Create New Account", 
    font=("Arial", 10), 
    bg="white", 
    fg="#2c3e50",
    bd=0, # Makes it look like a link
    cursor="hand2",
    command=lambda: open_create_account(window)
)
create_account_btn.grid(row=4, column=0, columnspan=2)

# Allow pressing "Enter" to log in
window.bind('<Return>', lambda event: login())

window.mainloop()