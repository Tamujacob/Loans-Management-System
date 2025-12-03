from tkinter import *
from tkinter import ttk

# Create main window
window = Tk()
window.title("Apply For A Loan")
window.geometry("800x600")
window.configure(bg="#dff6dd")

# Title label
title_label = Label(window, text="APPLY FOR A LOAN", font=("Arial", 25, "bold"), bg="#dff6dd", fg="#2c264a")
title_label.pack(pady=20)

# Widget frame
widget_frame = Frame(window, bg="white", padx=30, pady=20, relief="raised", bd=5)
widget_frame.pack()

# Function to create labels and entries aligned properly
def create_row(label_text, row):
    label = Label(widget_frame, text=label_text, font=("Arial", 12, "bold"), bg="white", anchor="w")
    label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
    entry = Entry(widget_frame, font=("Arial", 12), width=30)
    entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
    return entry

# Create form fields
name_entry = create_row("Full Name:", 0)
amount_entry = create_row("Loan Amount:", 1)
collateral_entry = create_row("Collateral Security:", 2)
return_amount_entry = create_row("Return Amount:", 3)
return_amount_entry.config(state="readonly")

# Loan type dropdown
type_label = Label(widget_frame, text="Loan Type:", font=("Arial", 12, "bold"), bg="white")
type_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
type_combo = ttk.Combobox(widget_frame, values=["Personal Loan", "Business Loan", "Car Loan", "Home Loan", "School Fees Loan"], font=("Arial", 12), width=28)
type_combo.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Duration dropdown
duration_label = Label(widget_frame, text="Repayment Duration:", font=("Arial", 12, "bold"), bg="white")
duration_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
duration_combo = ttk.Combobox(widget_frame, values=["6 months", "1 year", "2 years", "3 years", "5 years"], font=("Arial", 12), width=28)
duration_combo.grid(row=5, column=1, padx=10, pady=5, sticky="w")

# Repayment method
method_label = Label(widget_frame, text="Repayment Method:", font=("Arial", 12, "bold"), bg="white")
method_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
monthly_radio = Radiobutton(widget_frame, text="Monthly", value="Monthly", font=("Arial", 12), bg="white")
monthly_radio.grid(row=6, column=1, sticky="w", padx=5)
weekly_radio = Radiobutton(widget_frame, text="Weekly", value="Weekly", font=("Arial", 12), bg="white")
weekly_radio.grid(row=6, column=1, sticky="e", padx=5)

# Loan purpose
purpose_label = Label(widget_frame, text="Loan Purpose:", font=("Arial", 12, "bold"), bg="white")
purpose_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
loan_purpose_text = Text(widget_frame, height=3, width=30, font=("Arial", 12))
loan_purpose_text.grid(row=7, column=1, padx=10, pady=5, sticky="w")

# Terms and conditions checkbox
terms_var = IntVar()
terms_check = Checkbutton(widget_frame, text="I accept the terms and conditions", variable=terms_var, font=("Arial", 12), bg="white")
terms_check.grid(row=8, columnspan=2, pady=10)

# Button frame
btn_frame = Frame(window, bg="#dff6dd")
btn_frame.pack(pady=10)

# Submit button
submit_btn = Button(btn_frame, text="Submit Application", bg="#28a745", fg="white", font=("Arial", 12, "bold"), width=18)
submit_btn.grid(row=0, column=0, padx=10)

# Clear button
clear_btn = Button(btn_frame, text="Clear", bg="#dc3545", fg="white", font=("Arial", 12, "bold"), width=10)
clear_btn.grid(row=0, column=1, padx=10)

window.mainloop()

