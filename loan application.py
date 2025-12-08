from tkinter import *
from tkinter import ttk, messagebox
import database
import datetime
import uuid
import subprocess   # <-- REQUIRED for opening dashboard.py


# -------------------------------------------------------
# GLOBAL VARIABLES (Initialized after window creation)
# -------------------------------------------------------
repayment_method_var = None
terms_var = None


# -------------------------------------------------------
# HELPER FUNCTION: Calculate Return Amount
# -------------------------------------------------------
def calculate_return_amount():
    """
    Calculates the loan repayment amount using simple interest.
    Annual interest rate = 12%
    """
    try:
        loan_amount = float(amount_entry.get())
        duration_text = duration_combo.get()

        # Extract years from duration text
        if "year" in duration_text:
            years = int(duration_text.split()[0])
        elif "month" in duration_text:
            months = int(duration_text.split()[0])
            years = months / 12.0
        else:
            return 0

        ANNUAL_INTEREST = 0.12  # 12%

        interest = loan_amount * ANNUAL_INTEREST * years
        total_amount = loan_amount + interest

        return round(total_amount, 2)

    except Exception:
        return 0


# -------------------------------------------------------
# NAVIGATION: Return to Dashboard
# -------------------------------------------------------
def return_to_dashboard():
    """Closes loan application page and opens dashboard.py"""
    window.destroy()
    subprocess.Popen(["python", "dashboard.py"])


# -------------------------------------------------------
# CORE: Submit Loan Application
# -------------------------------------------------------
def submit_application():
    try:
        # Fetch form values
        customer_name = name_entry.get()
        loan_amount_str = amount_entry.get()
        loan_type = type_combo.get()
        repayment_duration = duration_combo.get()
        repayment_method = repayment_method_var.get()
        loan_purpose = loan_purpose_text.get("1.0", END).strip()
        collateral_security = collateral_entry.get()
        terms_accepted = terms_var.get()

        # Required fields check
        if not all([customer_name, loan_amount_str, loan_type, repayment_duration]):
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        if terms_accepted != 1:
            messagebox.showerror("Error", "You must accept the terms and conditions.")
            return

        try:
            loan_amount = float(loan_amount_str)
            if loan_amount <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Loan amount must be a valid positive number.")
            return

        total_return_amount = calculate_return_amount()

        # Build MongoDB document
        loan_data = {
            "loan_id": str(uuid.uuid4()),
            "customer_name": customer_name,
            "loan_amount": loan_amount,
            "loan_type": loan_type,
            "duration": repayment_duration,
            "repayment_method": repayment_method,
            "purpose": loan_purpose,
            "collateral": collateral_security if collateral_security else "None",
            "return_amount": total_return_amount,
            "interest_rate": 0.12,
            "application_date": datetime.datetime.now(),
            "status": "Pending",
            "next_payment": "To be set"
        }

        if database.db is None:
            messagebox.showerror("DB Error", "Database not connected.")
            return

        result = database.db['loans'].insert_one(loan_data)

        if result.inserted_id:
            messagebox.showinfo("Success", f"Loan Application Submitted!\nLoan ID: {loan_data['loan_id']}")
            clear_form()
        else:
            messagebox.showerror("Error", "Failed to save application.")

    except Exception as e:
        messagebox.showerror("System Error", f"Unexpected error: {e}")


# -------------------------------------------------------
# CLEAR FORM
# -------------------------------------------------------
def clear_form():
    name_entry.delete(0, END)
    amount_entry.delete(0, END)
    type_combo.set('')
    duration_combo.set('')
    repayment_method_var.set("Monthly")
    terms_var.set(0)
    loan_purpose_text.delete("1.0", END)
    collateral_entry.delete(0, END)
    update_return_amount()


# -------------------------------------------------------
# UPDATE RETURN AMOUNT LIVE
# -------------------------------------------------------
def update_return_amount(event=None):
    total = calculate_return_amount()
    return_amount_entry.config(state="normal")
    return_amount_entry.delete(0, END)
    return_amount_entry.insert(0, f"{total:,.2f}")
    return_amount_entry.config(state="readonly")


# =======================================================
# GUI START
# =======================================================
window = Tk()
window.title("Apply For A Loan")
window.geometry("800x600")
window.configure(bg="#e1ffc9")

# Initialize variables AFTER creating window
repayment_method_var = StringVar(value="Monthly")
terms_var = IntVar()

# Title
title_label = Label(window, text="APPLY FOR A LOAN", font=("Arial", 25, "bold"), bg="#e1ffc9")
title_label.pack(pady=20)

# Form container frame
widget_frame = Frame(window, bg="white", padx=20, pady=20, relief="raised", bd=3)
widget_frame.pack()

# ------------------ FORM FIELDS -------------------

# Name
Label(widget_frame, text="Full Name:", bg="white", font=("Arial")).grid(row=0, column=0, pady=5, sticky=W)
name_entry = Entry(widget_frame, font=("Arial"), width=30)
name_entry.grid(row=0, column=1, pady=5)

# Loan Amount
Label(widget_frame, text="Loan Amount:", bg="white", font=("Arial")).grid(row=1, column=0, pady=5, sticky=W)
amount_entry = Entry(widget_frame, font=("Arial"), width=30)
amount_entry.grid(row=1, column=1, pady=5)
amount_entry.bind("<KeyRelease>", update_return_amount)

# Loan Type
Label(widget_frame, text="Loan Type:", bg="white", font=("Arial")).grid(row=2, column=0, pady=5, sticky=W)
type_combo = ttk.Combobox(widget_frame, values=["Personal Loan", "Business Loan", "Car Loan", "Home Loan", "School Fees Loan"],
                          font=("Arial", 12), width=28, state="readonly")
type_combo.grid(row=2, column=1, pady=5)

# Duration
Label(widget_frame, text="Repayment Duration:", bg="white", font=("Arial")).grid(row=3, column=0, pady=5, sticky=W)
duration_combo = ttk.Combobox(widget_frame,
                              values=["6 months", "1 year", "2 years", "3 years", "5 years"],
                              font=("Arial", 12), width=28, state="readonly")
duration_combo.grid(row=3, column=1, pady=5)
duration_combo.bind("<<ComboboxSelected>>", update_return_amount)

# Repayment Method
Label(widget_frame, text="Repayment Method:", bg="white", font=("Arial")).grid(row=4, column=0, pady=5, sticky=W)
Radiobutton(widget_frame, text="Monthly", variable=repayment_method_var, value="Monthly",
            bg="white", font=("Arial")).grid(row=4, column=1, sticky="w")
Radiobutton(widget_frame, text="Weekly", variable=repayment_method_var, value="Weekly",
            bg="white", font=("Arial")).grid(row=4, column=2, sticky="w")

# Loan Purpose
Label(widget_frame, text="Loan Purpose:", bg="white", font=("Arial")).grid(row=5, column=0, pady=5, sticky=W)
loan_purpose_text = Text(widget_frame, height=3, width=30, font=("Arial"))
loan_purpose_text.grid(row=5, column=1, pady=5)

# Collateral
Label(widget_frame, text="Collateral Security:", bg="white", font=("Arial")).grid(row=6, column=0, pady=5, sticky=W)
collateral_entry = Entry(widget_frame, font=("Arial"), width=30)
collateral_entry.grid(row=6, column=1, pady=5)

# Return Amount (read-only)
Label(widget_frame, text="Estimated Return Amount:", bg="white", font=("Arial")).grid(row=7, column=0, pady=5, sticky=W)
return_amount_entry = Entry(widget_frame, font=("Arial", 12), width=30, state="readonly")
return_amount_entry.grid(row=7, column=1, pady=5)

# Terms
terms_check = Checkbutton(widget_frame, text="I accept the terms and conditions",
                          variable=terms_var, bg="white", font=("Arial"))
terms_check.grid(row=8, column=0, columnspan=2, pady=10)

# ------------------ BUTTONS -------------------
btn_frame = Frame(window, bg="#e1ffc9")
btn_frame.pack(pady=10)

submit_btn = Button(btn_frame, text="Submit Application", bg="#28a745", fg="white",
                    font=("Arial", 12, "bold"), width=18, command=submit_application)
submit_btn.grid(row=0, column=0, padx=10)

clear_btn = Button(btn_frame, text="Clear", bg="#dc3545", fg="white",
                   font=("Arial", 12, "bold"), width=10, command=clear_form)
clear_btn.grid(row=0, column=1, padx=10)

dashboard_btn = Button(btn_frame, text="Return to Dashboard",
                       bg="#007bff", fg="white", font=("Arial", 12, "bold"),
                       width=20, command=return_to_dashboard)
dashboard_btn.grid(row=0, column=2, padx=10)

# =======================================================
window.mainloop()
