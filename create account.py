import tkinter as tk
from tkinter import messagebox, ttk
import database 
import bcrypt 
import sys
import subprocess

# --- Global Functions for Navigation ---
def close_window():
    """Closes this window to return to the calling management screen."""
    window.destroy()

def create_account():
    # Get values from the entry fields
    username = username_entry.get()
    password = password_entry.get()
    confirm_password = confirm_entry.get()
    role = role_combobox.get() # Get selected role
    
    if not username or not password or not confirm_password or not role:
        messagebox.showerror("Error", "All fields are required.")
    elif password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
    else:
        # Hash the password
        try:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            
            user_data = {
                "username": username,
                "password_hash": hashed_password.decode('utf-8'),
                "role": role # Use the selected role from dropdown
            }
            
            # Check for existing user
            if database.db['users'].find_one({"username": username}):
                messagebox.showerror("Error", "Username already exists.")
                return

            # Save to MongoDB
            result = database.db['users'].insert_one(user_data)
            
            if result.inserted_id:
                messagebox.showinfo("Success", f"Account created for: {username} with role: {role}!")
                
                # Clear fields
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                confirm_entry.delete(0, tk.END)
                
                # Close window so the Admin sees the updated list in User Management
                close_window()
                
            else:
                messagebox.showerror("Error", "Failed to save account.")

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        
# --- GUI Setup ---
window = tk.Tk()
window.title("Add New System User")
window.geometry("1000x700")
window.configure(bg="#e0f7fa")

# --- Main Content Frame ---
main_frame = tk.Frame(window, bg="white", padx=40, pady=40, relief=tk.RAISED, bd=2)
main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# --- Title ---
tk.Label(
    main_frame,
    text="👤 Register New User",
    font=("Arial", 24, "bold"),
    bg="white",
    fg="#00796b"
).grid(row=0, column=0, columnspan=2, pady=(0, 30))

# --- Input Fields ---

# 1. Username
tk.Label(main_frame, text="Username:", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="w", pady=(10, 5))
username_entry = tk.Entry(main_frame, width=40, font=("Arial", 12), bd=1, relief=tk.SOLID)
username_entry.grid(row=2, column=0, columnspan=2, ipady=5)

# 2. Access Level (Role Selection)
tk.Label(main_frame, text="Access Level:", font=("Arial", 12), bg="white").grid(row=3, column=0, sticky="w", pady=(10, 5))
role_combobox = ttk.Combobox(main_frame, width=38, font=("Arial", 12), state="readonly")
role_combobox['values'] = ("Staff", "Admin") # Defining the roles
role_combobox.set("Staff") # Set default
role_combobox.grid(row=4, column=0, columnspan=2, ipady=5)

# 3. Password
tk.Label(main_frame, text="Password:", font=("Arial", 12), bg="white").grid(row=5, column=0, sticky="w", pady=(10, 5))
password_entry = tk.Entry(main_frame, width=40, font=("Arial", 12), show="*", bd=1, relief=tk.SOLID)
password_entry.grid(row=6, column=0, columnspan=2, ipady=5)

# 4. Confirm Password
tk.Label(main_frame, text="Confirm Password:", font=("Arial", 12), bg="white").grid(row=7, column=0, sticky="w", pady=(10, 5))
confirm_entry = tk.Entry(main_frame, width=40, font=("Arial", 12), show="*", bd=1, relief=tk.SOLID)
confirm_entry.grid(row=8, column=0, columnspan=2, ipady=5)

# --- Action Buttons ---
create_button = tk.Button(
    main_frame,
    text="Register User",
    command=create_account,
    font=("Arial", 14, "bold"),
    bg="#4CAF50",
    fg="white",
    activebackground="#66BB6A",
    width=20,
    cursor="hand2"
)
create_button.grid(row=9, column=0, columnspan=2, pady=(30, 10), ipady=8)

# Cancel/Back Button
cancel_button = tk.Button(
    main_frame,
    text="Cancel and Exit",
    command=close_window,
    font=("Arial", 10),
    bg="white",
    fg="#d32f2f",
    bd=0,
    cursor="hand2"
)
cancel_button.grid(row=10, column=0, columnspan=2)

# Check DB connection
if database.db is None:
    messagebox.showwarning("Database Error", "Not connected to MongoDB!")

window.mainloop()