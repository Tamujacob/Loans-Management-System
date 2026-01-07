from tkinter import *
import subprocess
import sys
from tkinter import messagebox

# --- 1. CATCH LOGIN ARGUMENTS ---
try:
    CURRENT_USER_ROLE = sys.argv[1]
    CURRENT_USER_NAME = sys.argv[2]
except IndexError:
    CURRENT_USER_ROLE = "Staff"
    CURRENT_USER_NAME = "Guest"

# --- NAVIGATION FUNCTIONS (With Session Persistence) ---
def open_loan_application():
    window.destroy()
    try:
        # Pass session data forward
        subprocess.Popen([sys.executable, "loan application.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'loan application.py'.")

def open_loan_management():
    window.destroy()
    try:
        # Pass session data forward
        subprocess.Popen([sys.executable, "loan management.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'loan management.py'.")

def open_login():
    """Sign out and return to login."""
    if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
        window.destroy()
        try:
            subprocess.Popen([sys.executable, "login.py"])
        except Exception:
            messagebox.showerror("Error", "Could not find 'login.py'.")

def open_user_management():
    window.destroy()
    try:
        # Pass session data forward
        subprocess.Popen([sys.executable, "user_management.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'user_management.py'.")

# --- THEME COLORS ---
PRIMARY_GREEN = "#2ecc71"  
BG_LIGHT = "#f4f7f6"       
DARK_TEXT = "#2c3e50"
WHITE = "#ffffff"

# --- MAIN WINDOW SETUP ---
window = Tk()
window.title(f"Dashboard - {CURRENT_USER_NAME} ({CURRENT_USER_ROLE})")
window.geometry("1100x750") 
window.configure(bg=BG_LIGHT)

# --- HEADER SECTION ---
header = Frame(window, bg=PRIMARY_GREEN, height=140)
header.pack(fill="x", side="top")
header.pack_propagate(False)

Label(header, text="BIG ON GOLD LOANS", font=("Segoe UI", 28, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack(pady=(20, 0))
Label(header, text="MANAGEMENT DASHBOARD", font=("Segoe UI", 12, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack()

# User Status Bar in Header
status_frame = Frame(header, bg="#27ae60", padx=20)
status_frame.pack(side="bottom", fill="x")
Label(status_frame, text=f"👤 User: {CURRENT_USER_NAME}  |  🔑 Role: {CURRENT_USER_ROLE}", 
      font=("Segoe UI", 10), fg=WHITE, bg="#27ae60").pack(pady=5)

# --- MAIN CONTENT FRAME ---
frame = Frame(window, bg=WHITE, relief="flat", bd=0, padx=50, pady=30, 
              highlightthickness=1, highlightbackground="#dcdde1")
frame.pack(pady=40)

# Define modern button styling
btn_style = {
    "font": ("Segoe UI", 13, "bold"),
    "width": 30,
    "height": 2,
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0
}

# --- BUTTONS ---
current_row = 0

# 1. Loan Application
loan_app_btn = Button(frame, text="New Loan Application", bg=PRIMARY_GREEN, fg=WHITE, 
                      activebackground="#27ae60", activeforeground=WHITE,
                      **btn_style, command=open_loan_application)
loan_app_btn.grid(row=current_row, column=0, pady=12)
current_row += 1

# 2. Loan Management
loan_man_btn = Button(frame, text="Loan Management", bg=DARK_TEXT, fg=WHITE, 
                      activebackground="#34495e", activeforeground=WHITE,
                      **btn_style, command=open_loan_management)
loan_man_btn.grid(row=current_row, column=0, pady=12)
current_row += 1

# 3. Loan Repayment
loan_rep_btn = Button(frame, text="Loan Repayment", bg=DARK_TEXT, fg=WHITE, 
                      activebackground="#34495e", activeforeground=WHITE,
                      **btn_style)
loan_rep_btn.grid(row=current_row, column=0, pady=12)
current_row += 1

# --- CONDITIONAL ADMIN BUTTON ---
if CURRENT_USER_ROLE == "Admin":
    user_man_btn = Button(frame, text="User Management", bg="#3498db", fg=WHITE, 
                          activebackground="#2980b9", activeforeground=WHITE,
                          **btn_style, command=open_user_management)
    user_man_btn.grid(row=current_row, column=0, pady=12)
    current_row += 1

# 4. Reports and Analytics
reports_btn = Button(frame, text="Reports and Analytics", bg=DARK_TEXT, fg=WHITE, 
                      activebackground="#34495e", activeforeground=WHITE,
                      **btn_style)
reports_btn.grid(row=current_row, column=0, pady=12)

# --- FOOTER ---
exit_btn = Button(window, text="🚪 Sign Out", font=("Segoe UI", 11, "bold", "underline"), 
                  bg=BG_LIGHT, fg="#e74c3c", bd=0, cursor="hand2", command=open_login)
exit_btn.pack(side="bottom", pady=30)

window.mainloop()