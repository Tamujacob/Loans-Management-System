import tkinter as tk
from tkinter import messagebox, ttk
import database 
import bcrypt 
import sys

# --- THEME COLORS ---
PRIMARY_GREEN = "#2ecc71"
DARK_GREEN = "#27ae60"
BG_COLOR = "#f4f7f6"
WHITE = "#ffffff"
TEXT_COLOR = "#2c3e50"
SOFT_GREY = "#dcdde1"
DANGER_RED = "#e74c3c"

def close_window():
    window.destroy()

def create_account():
    username = username_entry.get().strip()
    password = password_entry.get()
    confirm_password = confirm_entry.get()
    role = role_combobox.get()
    
    if not username or not password or not confirm_password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
        
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    try:
        # Check for existing user
        if database.db['users'].find_one({"username": username}):
            messagebox.showerror("Error", f"Username '{username}' is already taken.")
            return

        # Hashing
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        user_data = {
            "username": username,
            "password_hash": hashed_password.decode('utf-8'),
            "role": role
        }
        
        result = database.db['users'].insert_one(user_data)
        
        if result.inserted_id:
            messagebox.showinfo("Success", f"User {username} successfully registered as {role}.")
            close_window()
    except Exception as e:
        messagebox.showerror("Database Error", f"Connection lost: {e}")

# --- GUI Setup ---
window = tk.Tk()
window.title("System User Registration")
window.geometry("800x750")
window.configure(bg=BG_COLOR)

# Custom Style for Combobox
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground=WHITE, bordercolor=SOFT_GREY, padding=5)

# --- MAIN CARD ---
card = tk.Frame(window, bg=WHITE, padx=0, pady=0, highlightthickness=1, highlightbackground=SOFT_GREY)
card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=450, height=620)

# --- CARD HEADER ---
header_frame = tk.Frame(card, bg=PRIMARY_GREEN, height=80)
header_frame.pack(fill="x", side="top")
header_frame.pack_propagate(False)

tk.Label(header_frame, text="ADD NEW USER", font=("Segoe UI", 18, "bold"), 
         bg=PRIMARY_GREEN, fg=WHITE).pack(pady=20)

# --- FORM CONTENT ---
form_container = tk.Frame(card, bg=WHITE, padx=40, pady=30)
form_container.pack(fill="both", expand=True)

def create_label(text):
    return tk.Label(form_container, text=text, font=("Segoe UI", 10, "bold"), 
                    bg=WHITE, fg=TEXT_COLOR)

def create_entry(show=None):
    return tk.Entry(form_container, font=("Segoe UI", 11), bg=BG_COLOR, 
                    fg=TEXT_COLOR, bd=0, highlightthickness=1, 
                    highlightbackground=SOFT_GREY, highlightcolor=PRIMARY_GREEN, show=show)

# Username
create_label("USERNAME").pack(anchor="w", pady=(10, 2))
username_entry = create_entry()
username_entry.pack(fill="x", ipady=8, pady=(0, 15))

# Role
create_label("ACCESS ROLE").pack(anchor="w", pady=(10, 2))
role_combobox = ttk.Combobox(form_container, font=("Segoe UI", 11), state="readonly")
role_combobox['values'] = ("Staff", "Admin")
role_combobox.set("Staff")
role_combobox.pack(fill="x", ipady=5, pady=(0, 15))

# Password
create_label("PASSWORD").pack(anchor="w", pady=(10, 2))
password_entry = create_entry(show="*")
password_entry.pack(fill="x", ipady=8, pady=(0, 15))

# Confirm Password
create_label("CONFIRM PASSWORD").pack(anchor="w", pady=(10, 2))
confirm_entry = create_entry(show="*")
confirm_entry.pack(fill="x", ipady=8, pady=(0, 30))

# --- BUTTONS ---
register_btn = tk.Button(
    form_container, text="REGISTER ACCOUNT", command=create_account,
    font=("Segoe UI", 12, "bold"), bg=PRIMARY_GREEN, fg=WHITE,
    activebackground=DARK_GREEN, activeforeground=WHITE,
    bd=0, cursor="hand2"
)
register_btn.pack(fill="x", ipady=12)

cancel_btn = tk.Button(
    form_container, text="Cancel", command=close_window,
    font=("Segoe UI", 10, "underline"), bg=WHITE, fg=DANGER_RED,
    activebackground=WHITE, activeforeground=TEXT_COLOR,
    bd=0, cursor="hand2"
)
cancel_btn.pack(pady=15)

window.mainloop()