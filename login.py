from tkinter import *
from tkinter import messagebox
import subprocess  # Import subprocess to run dashboard.py

# Dummy credentials
USERNAME = "admin"
PASSWORD = "password123"

def login():
    user = user_entry.get()
    passw = pass_entry.get()

    if user == USERNAME and passw == PASSWORD:
        messagebox.showinfo("Login Successful", "Welcome to Loan Management System!")
        window.destroy()  # Close login window
        subprocess.Popen(["python", "dashboard.py"])  # Open dashboard
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password!")

# Create main window
window = Tk()
window.title("Login Page")
window.geometry("350x250")
window.configure(bg="#f0f0f0")

# Center Frame
frame = Frame(window, bg="white", padx=20, pady=20, relief="ridge", bd=5)
frame.place(relx=0.5, rely=0.5, anchor=CENTER)

# Title Label
Label(frame, text="User Login", font=("Arial", 14, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=10)

# Username Label & Entry
Label(frame, text="Username:", font=("Arial", 10), bg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
user_entry = Entry(frame, font=("Arial", 10))
user_entry.grid(row=1, column=1, padx=5, pady=5)

# Password Label & Entry
Label(frame, text="Password:", font=("Arial", 10), bg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
pass_entry = Entry(frame, font=("Arial", 10), show="*")
pass_entry.grid(row=2, column=1, padx=5, pady=5)

# Login Button
log_button = Button(frame, text="Login", font=("Arial", 10, "bold"), bg="#007BFF", fg="white", width=15, command=login)
log_button.grid(row=3, column=0, columnspan=2, pady=10)

# Allow pressing "Enter" to log in
window.bind('<Return>', lambda event: login())

window.mainloop()
