from tkinter import *
import subprocess  # Switched from os to subprocess for better path handling
import sys

# --- NAVIGATION FUNCTIONS ---
def open_loan_application():
    """Destroys dashboard and runs the loan application script."""
    window.destroy()
    # subprocess handles the space in 'ARJENZ JACOB' automatically
    subprocess.Popen([sys.executable, "loan application.py"])

def open_loan_management():
    """Destroys dashboard and runs the loan management script."""
    window.destroy()
    subprocess.Popen([sys.executable, "loan management.py"])

def open_login():
    """Returns to the login screen."""
    window.destroy()
    subprocess.Popen([sys.executable, "login.py"])

def open_loan_repayment():
    print("Navigating to Loan Repayment module...")
    # subprocess.Popen([sys.executable, "loan_repayment.py"])

def open_user_management():
    print("Navigating to User Management module...")
    # subprocess.Popen([sys.executable, "user_management.py"])
    
def open_reports_analysis():
    print("Navigating to Reports and Analytics module...")
    # subprocess.Popen([sys.executable, "reports_analysis.py"])

# --- THEME COLORS ---
PRIMARY_GREEN = "#2ecc71"  # Your Company Green
BG_LIGHT = "#f4f7f6"       
DARK_TEXT = "#2c3e50"
WHITE = "#ffffff"

# --- MAIN WINDOW SETUP ---
window = Tk()
window.title("Loans Management System - Dashboard")
window.geometry("1100x700") 
window.configure(bg=BG_LIGHT)

# --- SET WINDOW TITLE BAR ICON ---
try:
    # Replaces the default leaf icon with your company logo
    title_icon = PhotoImage(file="bu logo.png")
    window.iconphoto(True, title_icon)
except Exception as e:
    print(f"Title bar icon could not be loaded: {e}")

# --- HEADER SECTION ---
header = Frame(window, bg=PRIMARY_GREEN, height=120)
header.pack(fill="x", side="top")
header.pack_propagate(False)

Label(header, text="BIG ON GOLD LOANS", font=("Segoe UI", 28, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack(pady=(20, 0))
Label(header, text="MANAGEMENT DASHBOARD", font=("Segoe UI", 12, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack()

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
# Loan Application
loan_app_btn = Button(frame, text="New Loan Application", bg=PRIMARY_GREEN, fg=WHITE, 
                      activebackground="#27ae60", activeforeground=WHITE,
                      **btn_style, command=open_loan_application)
loan_app_btn.grid(row=0, column=0, pady=12)

# Management Buttons
loan_man_btn = Button(frame, text="Loan Management", bg=DARK_TEXT, fg=WHITE, 
                      activebackground="#34495e", activeforeground=WHITE,
                      **btn_style, command=open_loan_management)
loan_man_btn.grid(row=1, column=0, pady=12)

loan_rep_btn = Button(frame, text="Loan Repayment", bg=DARK_TEXT, fg=WHITE, 
                      activebackground="#34495e", activeforeground=WHITE,
                      **btn_style, command=open_loan_repayment)
loan_rep_btn.grid(row=2, column=0, pady=12)

user_man_btn = Button(frame, text="User Management", bg=DARK_TEXT, fg=WHITE, 
                      activebackground="#34495e", activeforeground=WHITE,
                      **btn_style, command=open_user_management)
user_man_btn.grid(row=3, column=0, pady=12)

reports_btn = Button(frame, text="Reports and Analytics", bg=DARK_TEXT, fg=WHITE, 
                     activebackground="#34495e", activeforeground=WHITE,
                     **btn_style, command=open_reports_analysis)
reports_btn.grid(row=4, column=0, pady=12)

# --- FOOTER ---
exit_btn = Button(window, text="Sign Out", font=("Segoe UI", 10, "underline"), 
                  bg=BG_LIGHT, fg=DARK_TEXT, bd=0, cursor="hand2", command=open_login)
exit_btn.pack(side="bottom", pady=20)

window.mainloop()