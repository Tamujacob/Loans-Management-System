import tkinter as tk
from tkinter import messagebox
import database 
import bcrypt # 1. Import bcrypt for password hashing
import os     # 2. Import os to switch back to the login screen

# --- Global Functions for Navigation ---
def switch_to_login(current_window):
    """Destroys the current window and opens the login screen."""
    current_window.destroy()
    # Execute the login.py script
    os.system('python login.py')


def create_account():
    # Get values from the entry fields
    username = username_entry.get()
    password = password_entry.get()
    confirm_password = confirm_entry.get()
    
    
    if not username or not password or not confirm_password:
        messagebox.showerror("Error", "All fields are required.")
    elif password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
    else:
        # --- MISSING CODE: MongoDB Integration and Hashing ---
        
        # 1. Hash the password
        try:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            
            user_data = {
                "username": username,
                # Store the hashed password as a string
                "password_hash": hashed_password.decode('utf-8'),
                "role": "user" # Default role
            }
            
            # 2. Check for existing user before insertion
            if database.db['users'].find_one({"username": username}):
                messagebox.showerror("Error", "Username already exists. Please choose a different one.")
                return

            # 3. Save to MongoDB
            result = database.db['users'].insert_one(user_data)
            
            if result.inserted_id:
                messagebox.showinfo("Success", f"Account created successfully for: {username}! You can now log in.")
                
                # Clear fields after successful submission
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                confirm_entry.delete(0, tk.END)
                
                # Optional: Automatically switch to login screen after successful account creation
                switch_to_login(window) 
                
            else:
                messagebox.showerror("Error", "Failed to save account to database.")

        except Exception as e:
             # This handles MongoDB connection errors or bcrypt errors
            messagebox.showerror("Database Error", f"An error occurred while saving: {e}")
        
        # --- END OF MISSING CODE ---


# --- GUI Setup (Your Existing Code) ---
window = tk.Tk()
window.title("Secure Account Creation")
window.geometry("1000x650")
window.configure(bg="#e0f7fa")

# --- Main Content Frame (Centered) ---
main_frame = tk.Frame(window, bg="white", padx=40, pady=40, relief=tk.RAISED, bd=2)
main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# --- Title ---
title_label = tk.Label(
    main_frame,
    text="👤 Create Your Account",
    font=("Arial", 24, "bold"),
    bg="white",
    fg="#00796b"
)
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))


# --- Input Fields ---

# 1. Username/Email Field
username_label = tk.Label(main_frame, text="Username (or Email):", font=("Arial", 12), bg="white")
username_label.grid(row=1, column=0, sticky="w", pady=(10, 5))
username_entry = tk.Entry(main_frame, width=40, font=("Arial", 12), bd=1, relief=tk.SOLID)
username_entry.grid(row=2, column=0, columnspan=2, ipady=5)

# 2. Password Field
password_label = tk.Label(main_frame, text="Password:", font=("Arial", 12), bg="white")
password_label.grid(row=3, column=0, sticky="w", pady=(10, 5))
password_entry = tk.Entry(main_frame, width=40, font=("Arial", 12), show="*", bd=1, relief=tk.SOLID)
password_entry.grid(row=4, column=0, columnspan=2, ipady=5)

# 3. Confirm Password Field
confirm_label = tk.Label(main_frame, text="Confirm Password:", font=("Arial", 12), bg="white")
confirm_label.grid(row=5, column=0, sticky="w", pady=(10, 5))
confirm_entry = tk.Entry(main_frame, width=40, font=("Arial", 12), show="*", bd=1, relief=tk.SOLID)
confirm_entry.grid(row=6, column=0, columnspan=2, ipady=5)


# --- Action Buttons ---
create_button = tk.Button(
    main_frame,
    text="Create Account",
    command=create_account, # Linked to the updated function
    font=("Arial", 14, "bold"),
    bg="#4CAF50",
    fg="white",
    activebackground="#66BB6A",
    width=20
)
create_button.grid(row=7, column=0, columnspan=2, pady=(30, 10), ipady=8)

# "Already have an account?" link/button
login_link = tk.Button(
    main_frame,
    text="Already have an account? Login here",
    command=lambda: switch_to_login(window), # Linked to the switch function
    font=("Arial", 10),
    bg="white",
    fg="#00796b",
    bd=0,
    cursor="hand2"
)
login_link.grid(row=8, column=0, columnspan=2)


# --- Check DB Connection on Launch ---
if database.db is None:
    messagebox.showwarning("Connection Status", "Could not connect to MongoDB. Login/Account functions may not work.")


window.mainloop()