from tkinter import *
from tkinter import ttk, messagebox
import database # Import your MongoDB connection file
import datetime # Used for stamping the application date


# --- GLOBAL VARIABLE FOR REPAYMENT METHOD ---
# We need a StringVar to correctly handle the Radiobuttons
repayment_method_var = StringVar(value="Monthly") # Set a default value


# --- HELPER FUNCTION: Calculate Estimated Return Amount (Simple Interest Example) ---
def calculate_return_amount():
    """
    Calculates the total repayment amount (Principal + Interest).
    Interest Rate is simplified to 12% annual rate for demonstration.
    """
    try:
        loan_amount = float(amount_entry.get())
        duration_text = duration_combo.get()
        
        # 1. Extract duration in years
        if "year" in duration_text:
            years = int(duration_text.split()[0])
        elif "month" in duration_text:
            months = int(duration_text.split()[0])
            years = months / 12.0
        else:
            return 0 # Default if combo box is empty
            
        # 2. Define a simple annual interest rate (e.g., 12% or 0.12)
        ANNUAL_INTEREST_RATE = 0.12 
        
        # 3. Simple Interest Calculation: I = P * R * T
        interest_amount = loan_amount * ANNUAL_INTEREST_RATE * years
        total_return_amount = loan_amount + interest_amount
        
        return round(total_return_amount, 2)
        
    except ValueError:
        return 0
    except Exception:
        return 0


# --- CORE LOGIC: Save Data to MongoDB ---
def submit_application():
    """
    Gathers form data, calculates return amount, validates, and saves to MongoDB.
    """
    try:
        # 1. Collect all data from the form
        customer_name = name_entry.get()
        loan_amount_str = amount_entry.get()
        loan_type = type_combo.get()
        repayment_duration = duration_combo.get()
        repayment_method = repayment_method_var.get()
        loan_purpose = loan_purpose_text.get("1.0", END).strip()
        collateral_security = collateral_entry.get()
        terms_accepted = terms_var.get()
        
        # 2. Initial Validation
        if not all([customer_name, loan_amount_str, loan_type, repayment_duration]):
            messagebox.showerror("Validation Error", "Please fill in all required fields (Name, Amount, Type, Duration).")
            return
        
        if terms_accepted != 1:
            messagebox.showerror("Validation Error", "You must accept the terms and conditions.")
            return

        try:
            loan_amount = float(loan_amount_str)
            if loan_amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Loan Amount must be a valid number greater than zero.")
            return
            
        # 3. Calculate Final Amounts
        total_return_amount = calculate_return_amount()

        # 4. Construct the MongoDB Document
        loan_data = {
            "customer_name": customer_name,
            "loan_amount": loan_amount,
            "loan_type": loan_type,
            "duration": repayment_duration,
            "repayment_method": repayment_method,
            "purpose": loan_purpose,
            "collateral": collateral_security if collateral_security else "None Provided",
            "return_amount": total_return_amount,
            "interest_rate": 0.12, # Stored for record
            "application_date": datetime.datetime.now(),
            "status": "Pending"
        }
        
        # 5. Save to MongoDB
        if database.db is None:
            messagebox.showerror("DB Error", "Database not connected. Cannot submit application.")
            return
            
        result = database.db['loans'].insert_one(loan_data)
        
        if result.inserted_id:
            messagebox.showinfo("Success", f"Application submitted successfully! Loan ID: {result.inserted_id}")
            clear_form() # Clear form on successful submission
        else:
            messagebox.showerror("Submission Failed", "Failed to save application to the database.")

    except Exception as e:
        messagebox.showerror("System Error", f"An unexpected error occurred: {e}")


def clear_form():
    """Clears all fields in the form."""
    name_entry.delete(0, END)
    amount_entry.delete(0, END)
    type_combo.set('')
    duration_combo.set('')
    repayment_method_var.set("Monthly")
    loan_purpose_text.delete("1.0", END)
    collateral_entry.delete(0, END)
    terms_var.set(0)
    return_amount_entry.config(state="normal")
    return_amount_entry.delete(0, END)
    return_amount_entry.config(state="readonly")


def update_return_amount(event=None):
    """Updates the return amount entry based on user input."""
    total = calculate_return_amount()
    return_amount_entry.config(state="normal")
    return_amount_entry.delete(0, END)
    return_amount_entry.insert(0, f"{total:,.2f}")
    return_amount_entry.config(state="readonly")


# ------------------------------------------------------------------
# --- GUI SETUP (Modified) ---
# ------------------------------------------------------------------

window=Tk()
window.title("Apply For A Loan")
window.geometry("800x600")
window.configure(bg="#e1ffc9")

title_label=Label(window,text="APPLY FOR A LOAN",font=("Arial",25,"bold"),bg="#e1ffc9")
title_label.pack(pady=20)

widget_frame=Frame(window,bg="white", padx=20, pady=20, relief="raised", bd=3)
widget_frame.pack()

# Full Name
name_label=Label(widget_frame,text="Full Name:",font=("Arial"), bg="white")
name_label.grid(row=0,column=0,padx=5,pady=5,sticky=W)
name_entry=Entry(widget_frame,font=("Arial"),width=30)
name_entry.grid(row=0,column=1,padx=5,pady=5)

# Loan Amount (Added binding for calculation)
amount_label=Label(widget_frame,text="Loan Amount:",font=("Arial"), bg="white")
amount_label.grid(row=1,column=0,padx=5,pady=5,sticky=W)
amount_entry=Entry(widget_frame,font=("Arial"),width=30)
amount_entry.grid(row=1,column=1,padx=5,pady=5)
amount_entry.bind('<KeyRelease>', update_return_amount) # Trigger calculation on key release

# Loan Type (Combo)
type_label=Label(widget_frame,text="Loan type",font=("Arial"), bg="white")
type_label.grid(row=2,column=0,padx=5,pady=5,sticky=W)
type_combo = ttk.Combobox(widget_frame, values=["Personal Loan", "Business Loan", "Car Loan", "Home Loan","School Fees Loan"], font=("Arial", 12), state="readonly", width=28)
type_combo.grid(row=2, column=1, pady=5)
type_combo.bind("<<ComboboxSelected>>", update_return_amount)

# Repayment Duration (Combo - Added binding for calculation)
duration_label=Label(widget_frame,text="Repayment Duration",font=("Arial"), bg="white")
duration_label.grid(row=3,column=0,padx=5,pady=5,sticky=W)
duration_combo = ttk.Combobox(widget_frame, values=["6 months", "1 year", "2 years", "3 years","5 years"], font=("Arial", 12), state="readonly", width=28)
duration_combo.grid(row=3, column=1, pady=5,sticky=W)
duration_combo.bind("<<ComboboxSelected>>", update_return_amount) # Trigger calculation on selection

# Repayment Method (Radiobuttons)
method_label=Label(widget_frame,text="Repayment Method",font=("Arial"), bg="white")
method_label.grid(row=4, column=0, pady=5,sticky=W)
monthly_radio=Radiobutton(widget_frame, text="Monthly", value="Monthly", variable=repayment_method_var, font=("Arial"), bg="white")
monthly_radio.grid(row=4, column=1, pady=5, sticky="w")
weekly_radio = Radiobutton(widget_frame, text="Weekly", value="Weekly", variable=repayment_method_var, font=("Arial"), bg="white")
weekly_radio.grid(row=4, column=2, pady=5, sticky="w")

# Loan Purpose (Textarea)
purpose_label=Label(widget_frame,text="Loan purpose:", font=("Arial", 12), bg="white")
purpose_label.grid(row=5,column=0,sticky="w",pady=5)
loan_purpose_text = Text(widget_frame, height=3, width=30, font=("Arial", 12))
loan_purpose_text.grid(row=5, column=1, pady=5)

# Collateral Security
security_label=Label(widget_frame,text="Collateral Security:", font=("Arial", 12), bg="white")
security_label.grid(row=6, column=0, sticky="w", pady=5)
collateral_entry = Entry(widget_frame, font=("Arial", 12), width=30)
collateral_entry.grid(row=6, column=1, pady=5)

# Return Amount (Display only)
return_label=Label(widget_frame,text="Estimated Return Amount:", font=("Arial", 12), bg="white")
return_label.grid(row=7, column=0, sticky="w", pady=5)
return_amount_entry = Entry(widget_frame, font=("Arial", 12), width=30, state="readonly")
return_amount_entry.grid(row=7, column=1, pady=5)

# Terms and Conditions
terms_var = IntVar()
terms_check = Checkbutton(widget_frame, text="I accept the terms and conditions", variable=terms_var, font=("Arial", 12), bg="white")
terms_check.grid(row=8, columnspan=2, pady=10)

btn_frame = Frame(window, bg="#e1ffc9")
btn_frame.pack(pady=10)

# Submit Button (Linked to submit_application function)
submit_btn = Button(btn_frame, text="Submit Application", bg="#28a745", fg="white", font=("Arial", 12, "bold"), width=18, command=submit_application)
submit_btn.grid(row=0, column=0, padx=10)

# Clear Button (Linked to clear_form function)
clear_btn = Button(btn_frame, text="Clear", bg="#dc3545", fg="white", font=("Arial", 12, "bold"), width=10, command=clear_form)
clear_btn.grid(row=0, column=1, padx=10)

window.mainloop()