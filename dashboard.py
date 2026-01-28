from tkinter import *
import subprocess
import sys
from tkinter import messagebox
import database  # Imported for activity logging
import os

# CATCH LOGIN ARGUMENTS
try:
    # If launched from login.py, these will be populated
    CURRENT_USER_ROLE = sys.argv[1]
    CURRENT_USER_NAME = sys.argv[2]
except IndexError:
    # If run separately/manually, it defaults to Guest
    CURRENT_USER_ROLE = "Staff"
    CURRENT_USER_NAME = "Guest"

# NAVIGATION FUNCTIONS 
def open_loan_application():
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "loan application.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'loan application.py'.")

def open_loan_management():
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "loan management.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'loan management.py'.")

def open_reports():
    """Navigates to reports.py and closes the dashboard"""
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "reports.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'reports.py'.")

def handle_logout():
    confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out?")
    if confirm:
        # LOG THE ACTIVITY
        try:
            database.log_activity(CURRENT_USER_NAME, "Logout", "User logged out from Dashboard")
        except Exception:
            pass # Ensure logout proceeds even if logging fails
            
        window.destroy()
        try:
            subprocess.Popen([sys.executable, "login.py"])
        except Exception:
            messagebox.showerror("Error", "Could not return to login screen.")

def open_user_management():
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "user_management.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'user_management.py'.")

#  THEME COLORS 
PRIMARY_GREEN = "#2ecc71"  
BG_LIGHT = "#f4f7f6"       
DARK_TEXT = "#2c3e50"
WHITE = "#ffffff"
DANGER_RED = "#c0392b"  
HOVER_RED = "#e74c3c"   

# MAIN WINDOW SETUP 
window = Tk()
window.title(f"Dashboard - {CURRENT_USER_NAME}")
window.geometry("1100x850") 
window.configure(bg=BG_LIGHT)

# --- ICON UPDATE (Replacing the leaf) ---
try:
    icon_path = "bu logo.png"
    if os.path.exists(icon_path):
        img = PhotoImage(file=icon_path)
        window.iconphoto(False, img)
except Exception as e:
    print(f"Icon could not be loaded: {e}")

# HEADER SECTION 
header = Frame(window, bg=PRIMARY_GREEN, height=140)
header.pack(fill="x", side="top")
header.pack_propagate(False)

Label(header, text="BIG ON GOLD LOANS", font=("Segoe UI", 28, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack(pady=(20, 0))
Label(header, text="MANAGEMENT DASHBOARD", font=("Segoe UI", 12, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack()

status_frame = Frame(header, bg="#27ae60", padx=20)
status_frame.pack(side="bottom", fill="x")
Label(status_frame, text=f"👤 User: {CURRENT_USER_NAME}  |  🔑 Role: {CURRENT_USER_ROLE}", 
      font=("Segoe UI", 10, "bold"), fg=WHITE, bg="#27ae60").pack(pady=5)

#  MAIN CONTENT
frame = Frame(window, bg=WHITE, relief="flat", padx=50, pady=30, 
              highlightthickness=1, highlightbackground="#dcdde1")
frame.pack(pady=20)

btn_style = {
    "font": ("Segoe UI", 13, "bold"),
    "width": 35,
    "height": 2,
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0
}

#  MENU BUTTONS
current_row = 0
modules = [
    ("New Loan Application", PRIMARY_GREEN, open_loan_application),
    ("Loan Management", DARK_TEXT, open_loan_management),
]

for text, color, cmd in modules:
    Button(frame, text=text, bg=color, fg=WHITE, **btn_style, command=cmd).grid(row=current_row, column=0, pady=8)
    current_row += 1

if CURRENT_USER_ROLE == "Admin":
    Button(frame, text="User Management", bg="#3498db", fg=WHITE, 
           **btn_style, command=open_user_management).grid(row=current_row, column=0, pady=8)
    current_row += 1

# Reports button linked to open_reports
Button(frame, text="Reports and Analytics", bg=DARK_TEXT, fg=WHITE, **btn_style, command=open_reports).grid(row=current_row, column=0, pady=8)

# LOGOUT BUTTON 
footer = Frame(window, bg=BG_LIGHT)
footer.pack(fill="x", pady=(20, 40)) 

def on_enter(e):
    logout_btn['background'] = HOVER_RED

def on_leave(e):
    logout_btn['background'] = DANGER_RED

logout_btn = Button(
    footer, 
    text="🛑  SIGN OUT OF SYSTEM", 
    font=("Segoe UI", 14, "bold"),
    bg=DANGER_RED, 
    fg=WHITE,
    activebackground=HOVER_RED,
    activeforeground=WHITE,
    width=35,
    height=2,
    bd=0,
    cursor="hand2",
    command=handle_logout
)
logout_btn.pack()

# Bind hover effects
logout_btn.bind("<Enter>", on_enter)
logout_btn.bind("<Leave>", on_leave)

window.mainloop()