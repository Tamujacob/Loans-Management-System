from tkinter import *

# Create main window
window = Tk()
window.title("Loans Management System")
window.geometry("1000x650")
window.configure(bg="#f0f0f0")

# Title Label (Styled)
title_label = Label(window, text="LOANS MANAGEMENT SYSTEM", font=("Algerian", 30, "bold"), fg="white", bg="#2c264a", padx=20, pady=10)
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
loan_application = Button(frame, text="Loan Application", bg="#007BFF", fg="white", **btn_style)
loan_application.grid(row=0, column=0, pady=10)

# Loan Management Button
loan_management = Button(frame, text="Loan Management", bg="#28a745", fg="white", **btn_style)
loan_management.grid(row=1, column=0, pady=10)

# Loan Repayment Button
loan_repayment = Button(frame, text="Loan Repayment", bg="#ffc107", fg="black", **btn_style)
loan_repayment.grid(row=2, column=0, pady=10)

# User Management Button
user_management = Button(frame, text="User Management", bg="#dc3545", fg="white", **btn_style)
user_management.grid(row=3, column=0, pady=10)

# Reports & Analytics Button
reports_analysis = Button(frame, text="Reports and Analytics", bg="#6f42c1", fg="white", **btn_style)
reports_analysis.grid(row=4, column=0, pady=10)

window.mainloop()
