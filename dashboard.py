from tkinter import *
import os 

# --- NAVIGATION FUNCTIONS ---
def open_loan_application():
    """Destroys dashboard and runs the loan application script."""
    window.destroy()
    # Execute the file: loanapplication.py
    os.system('python "loan application.py"') 

def open_loan_management():
    """Destroys dashboard and runs the loan management script."""
    window.destroy()
    # Execute the file: loan management.py
    os.system('python "loan management.py"')

def open_login():
    """Placeholder: Typically, the dashboard is accessed after login. 
    This is for demonstration or returning to a login screen.
    """
    window.destroy()
    os.system('python login.py')

# You will need to create separate files for these:
def open_loan_repayment():
    print("Navigating to Loan Repayment module...")
    # window.destroy()
    # os.system('python loan_repayment.py')

def open_user_management():
    print("Navigating to User Management module...")
    # window.destroy()
    # os.system('python user_management.py')
    
def open_reports_analysis():
    print("Navigating to Reports and Analytics module...")
    # window.destroy()
    # os.system('python reports_analysis.py')

# ----------------------------

# Create main window
window = Tk()
window.title("Loans Management System")
window.geometry("1000x650")
window.configure(bg="#f0f0f0")

# Title Label (Styled)
title_label = Label(window, text="BIG ON GOLD LOANS MANAGEMENT SYSTEM", font=("Algerian", 30, "bold"), fg="white", bg="#2c264a", padx=20, pady=10)
title_label.pack(fill="x")

# Main Frame (Holds Buttons)
frame = Frame(window, bg="#c5eda6", relief="ridge", bd=5, padx=50, pady=20)
frame.pack(pady=50)

# Define button styling
btn_style = {
    "font": ("Arial", 14, "bold"),
    "width": 25,
    "height": 2,
    "relief": "raised",
    "bd": 3
}


# Loan Application Button
loan_application = Button(frame, text="Loan Application", bg="#007BFF", fg="white", **btn_style, command=open_loan_application)
loan_application.grid(row=0, column=0, pady=10)

# Loan Management Button
# NOTE: The file name has a space, so it must be enclosed in quotes in os.system
loan_management = Button(frame, text="Loan Management", bg="#28a745", fg="white", **btn_style, command=open_loan_management)
loan_management.grid(row=1, column=0, pady=10)

# Loan Repayment Button (Functionality needs to be added to open_loan_repayment)
loan_repayment = Button(frame, text="Loan Repayment", bg="#ffc107", fg="black", **btn_style, command=open_loan_repayment)
loan_repayment.grid(row=2, column=0, pady=10)

# User Management Button (Functionality needs to be added to open_user_management)
user_management = Button(frame, text="User Management", bg="#dc3545", fg="white", **btn_style, command=open_user_management)
user_management.grid(row=3, column=0, pady=10)

# Reports & Analytics Button (Functionality needs to be added to open_reports_analysis)
reports_analysis = Button(frame, text="Reports and Analytics", bg="#6f42c1", fg="white", **btn_style, command=open_reports_analysis)
reports_analysis.grid(row=4, column=0, pady=10)

window.mainloop()