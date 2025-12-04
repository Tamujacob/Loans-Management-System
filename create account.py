import tkinter as tk
from tkinter import messagebox


window = tk.Tk()
window.title("Secure Account Creation")
# Set the window size, though the content will scale slightly
window.geometry("1000x650")
window.configure(bg="#e0f7fa") # Light blue-green background


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
        # In a real application, you would save this data to a database.
        messagebox.showinfo("Success", f"Account created for: {username}!")
        
        # Clear fields after successful submission
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        confirm_entry.delete(0, tk.END)


# --- Main Content Frame (Centered) ---
# Use a frame to group all the widgets and give it a white background
main_frame = tk.Frame(window, bg="white", padx=40, pady=40, relief=tk.RAISED, bd=2)
# Center the frame in the window
main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# --- Title ---
title_label = tk.Label(
    main_frame,
    text="👤 Create Your Account",
    font=("Arial", 24, "bold"),
    bg="white",
    fg="#00796b" # Dark teal color
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
# The show="*" option hides the password characters
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
    command=create_account,
    font=("Arial", 14, "bold"),
    bg="#4CAF50", # Green background
    fg="white", # White text
    activebackground="#66BB6A", # Lighter green when clicked
    width=20
)
create_button.grid(row=7, column=0, columnspan=2, pady=(30, 10), ipady=8)

# "Already have an account?" link/button
login_link = tk.Button(
    main_frame,
    text="Already have an account? Login here",
    # You would typically add a command here to switch to a login window
    command=lambda: print("Switching to Login..."),
    font=("Arial", 10),
    bg="white",
    fg="#00796b", # Dark teal text
    bd=0, # No border to make it look like a link
    cursor="hand2" # Change mouse cursor on hover
)
login_link.grid(row=8, column=0, columnspan=2)


window.mainloop()