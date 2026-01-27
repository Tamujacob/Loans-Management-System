import tkinter as tk
from tkinter import messagebox, ttk
import database 
import bcrypt 
import sys

# --- SESSION PERSISTENCE ---
try:
    # Capturing the admin who is creating the account
    CURRENT_USER_NAME = sys.argv[2] if len(sys.argv) > 2 else "Administrator"
except IndexError:
    CURRENT_USER_NAME = "Administrator"

# --- THEME COLORS ---
PRIMARY_GREEN = "#2ecc71"
DARK_GREEN = "#27ae60"
BG_COLOR = "#f4f7f6"
WHITE = "#ffffff"
TEXT_COLOR = "#2c3e50"
SOFT_GREY = "#dcdde1"
DANGER_RED = "#e74c3c"

def close_window():
    """Returns to the user management screen."""
    window.destroy()

def create_account():
    # Retrieve all inputs
    full_name = fullname_entry.get().strip()
    email = email_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get()
    confirm_password = confirm_entry.get()
    role = role_combobox.get()
    
    # Validation
    if not all([full_name, email, username, password, confirm_password]):
        messagebox.showerror("Error", "Please fill in all fields.")
        return
        
    if "@" not in email or "." not in email:
        messagebox.showerror("Error", "Please enter a valid email address.")
        return

    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    try:
        # Check for existing username OR email
        if database.db['users'].find_one({"username": username}):
            messagebox.showerror("Error", f"Username '{username}' is already taken.")
            return
        
        if database.db['users'].find_one({"email": email}):
            messagebox.showerror("Error", f"Email '{email}' is already registered.")
            return

        # Password Hashing
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Data dictionary matching user_management.py expectations
        user_data = {
            "full_name": full_name,
            "email": email,
            "username": username,
            "password_hash": hashed_password.decode('utf-8'),
            "role": role
        }
        
        result = database.db['users'].insert_one(user_data)
        
        if result.inserted_id:
            # LOG THE ACTIVITY
            database.log_activity(
                CURRENT_USER_NAME, 
                "Account Creation", 
                f"Created new {role} account for {full_name} ({username})"
            )
            
            messagebox.showinfo("Success", f"User {full_name} registered successfully!")
            close_window()
            
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

# --- GUI Setup ---
window = tk.Tk()
window.title("Register New System User")
window.geometry("600x850") 
window.configure(bg=BG_COLOR)

# Custom Style for Combobox
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground=WHITE, bordercolor=SOFT_GREY, padding=5)

# --- MAIN CARD ---

card = tk.Frame(window, bg=WHITE, highlightthickness=1, highlightbackground=SOFT_GREY)
card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=480, height=750)

# --- CARD HEADER ---
header_frame = tk.Frame(card, bg=PRIMARY_GREEN, height=80)
header_frame.pack(fill="x", side="top")
header_frame.pack_propagate(False)

tk.Label(header_frame, text="CREATE NEW ACCOUNT", font=("Segoe UI", 16, "bold"), 
          bg=PRIMARY_GREEN, fg=WHITE).pack(pady=25)

# --- FORM CONTENT ---
form_container = tk.Frame(card, bg=WHITE, padx=40, pady=20)
form_container.pack(fill="both", expand=True)

def create_label(text):
    return tk.Label(form_container, text=text, font=("Segoe UI", 9, "bold"), 
                    bg=WHITE, fg=TEXT_COLOR)

def create_entry(show=None):
    return tk.Entry(form_container, font=("Segoe UI", 11), bg=BG_COLOR, 
                    fg=TEXT_COLOR, bd=0, highlightthickness=1, 
                    highlightbackground=SOFT_GREY, highlightcolor=PRIMARY_GREEN, show=show)

# 1. Full Name
create_label("FULL NAME").pack(anchor="w", pady=(10, 2))
fullname_entry = create_entry()
fullname_entry.pack(fill="x", ipady=7, pady=(0, 12))

# 2. Email
create_label("EMAIL ADDRESS").pack(anchor="w", pady=(5, 2))
email_entry = create_entry()
email_entry.pack(fill="x", ipady=7, pady=(0, 12))

# 3. Username
create_label("USERNAME").pack(anchor="w", pady=(5, 2))
username_entry = create_entry()
username_entry.pack(fill="x", ipady=7, pady=(0, 12))

# 4. Access Role
create_label("ACCESS LEVEL").pack(anchor="w", pady=(5, 2))
role_combobox = ttk.Combobox(form_container, font=("Segoe UI", 11), state="readonly")
role_combobox['values'] = ("Staff", "Admin")
role_combobox.set("Staff")
role_combobox.pack(fill="x", ipady=4, pady=(0, 12))

# 5. Password
create_label("PASSWORD").pack(anchor="w", pady=(5, 2))
password_entry = create_entry(show="*")
password_entry.pack(fill="x", ipady=7, pady=(0, 12))

# 6. Confirm Password
create_label("CONFIRM PASSWORD").pack(anchor="w", pady=(5, 2))
confirm_entry = create_entry(show="*")
confirm_entry.pack(fill="x", ipady=7, pady=(0, 25))

# --- BUTTONS ---
register_btn = tk.Button(
    form_container, text="REGISTER USER", command=create_account,
    font=("Segoe UI", 12, "bold"), bg=PRIMARY_GREEN, fg=WHITE,
    activebackground=DARK_GREEN, activeforeground=WHITE,
    bd=0, cursor="hand2"
)
register_btn.pack(fill="x", ipady=12)

cancel_btn = tk.Button(
    form_container, text="Back to Management", command=close_window,
    font=("Segoe UI", 10, "underline"), bg=WHITE, fg=DANGER_RED,
    activebackground=WHITE, activeforeground=TEXT_COLOR,
    bd=0, cursor="hand2"
)
cancel_btn.pack(pady=10)

window.mainloop()