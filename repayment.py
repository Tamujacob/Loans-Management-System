import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
import database
import sys
import subprocess
import os
from bson.objectid import ObjectId

# --- SESSION PERSISTENCE ---
try:
    # Check if opened via subprocess with arguments (LoanID, Role, Username)
    if len(sys.argv) > 3:
        LOAN_ID_FROM_ARGS = sys.argv[1]
        CURRENT_USER_ROLE = sys.argv[2]
        CURRENT_USER_NAME = sys.argv[3]
    else:
        LOAN_ID_FROM_ARGS = None
        CURRENT_USER_ROLE = "Staff"
        CURRENT_USER_NAME = "Guest"
except IndexError:
    LOAN_ID_FROM_ARGS = None
    CURRENT_USER_ROLE = "Staff"
    CURRENT_USER_NAME = "Guest"

class RepaymentWindow(tk.Tk): 
    def __init__(self, loan_data=None):
        super().__init__()
        
        # Resolve database connection and loan data
        if loan_data is None and LOAN_ID_FROM_ARGS:
            try:
                self.loan_data = database.db['loans'].find_one({"_id": ObjectId(LOAN_ID_FROM_ARGS)})
            except Exception:
                self.loan_data = None
        else:
            self.loan_data = loan_data

        if not self.loan_data:
            messagebox.showerror("Error", "No loan record found. Returning to management.")
            self._handle_go_back()
            return

        self.loan_id = self.loan_data['_id'] 
        
        # Formatting UI
        self.title(f"Repayment Management - {self.loan_data.get('customer_name', 'Unknown')} (User: {CURRENT_USER_NAME})")
        self.geometry("1150x700") 
        self.config(bg="#f8f9fa") 
        
        self.colors = {
            "primary": "#2c3e50",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "logout": "#e67e22",
            "bg": "#f8f9fa"
        }

        self.setup_styles()
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1) 

        self.create_summary_frame()
        self.create_payment_form()
        self.create_payment_view()
        self.create_action_buttons()

        self.load_payments()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabelframe", background="#f8f9fa", bordercolor="#dcdde1")
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground=self.colors["primary"])
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#dcdde1")
        style.map("Treeview", background=[('selected', self.colors["accent"])])

    def create_summary_frame(self):
        summary_frame = tk.LabelFrame(self, text=" LOAN SUMMARY ", font=("Segoe UI", 11, "bold"), 
                                     bg="white", fg=self.colors["primary"], padx=15, pady=10, relief="flat", highlightthickness=1, highlightbackground="#dcdde1")
        summary_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        summary_frame.columnconfigure((0, 2), weight=1)
        
        data = self.loan_data
        tk.Label(summary_frame, text="Customer Name", bg="white", fg="#7f8c8d").grid(row=0, column=0, sticky="w")
        tk.Label(summary_frame, text=data.get('customer_name', 'N/A'), bg="white", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", pady=(0,5))
        
        tk.Label(summary_frame, text="Total Loan Amount", bg="white", fg="#7f8c8d").grid(row=2, column=0, sticky="w")
        tk.Label(summary_frame, text=f"RWF {float(data.get('loan_amount', 0)):,.2f}", bg="white", font=("Segoe UI", 12, "bold"), fg=self.colors["primary"]).grid(row=3, column=0, sticky="w")

        stats_frame = tk.Frame(summary_frame, bg="#f1f2f6", padx=10, pady=5)
        stats_frame.grid(row=0, column=2, rowspan=4, sticky="nsew")
        
        tk.Label(stats_frame, text="TOTAL PAID", bg="#f1f2f6", font=("Segoe UI", 9, "bold")).pack()
        self.total_paid_var = tk.StringVar(value="RWF 0.00")
        tk.Label(stats_frame, textvariable=self.total_paid_var, bg="#f1f2f6", font=("Segoe UI", 14, "bold"), fg=self.colors["success"]).pack()
        
        tk.Frame(stats_frame, height=1, bg="#dcdde1").pack(fill="x", pady=2)
        
        tk.Label(stats_frame, text="REMAINING BALANCE", bg="#f1f2f6", font=("Segoe UI", 9, "bold")).pack()
        self.remaining_var = tk.StringVar(value="RWF 0.00")
        tk.Label(stats_frame, textvariable=self.remaining_var, bg="#f1f2f6", font=("Segoe UI", 14, "bold"), fg=self.colors["danger"]).pack()

    def create_payment_form(self):
        form_frame = tk.LabelFrame(self, text=" RECORD NEW PAYMENT ", font=("Segoe UI", 10, "bold"), 
                                   bg="white", fg=self.colors["accent"], padx=15, pady=10, relief="flat", highlightthickness=1, highlightbackground="#dcdde1")
        form_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        tk.Label(form_frame, text="Amount (RWF)", bg="white", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(form_frame, font=("Segoe UI", 11), width=12, highlightthickness=1, highlightbackground="#dcdde1", relief="flat")
        self.amount_entry.grid(row=1, column=0, padx=(0,10), pady=5)
        
        tk.Label(form_frame, text="Payment Date", bg="white", font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w")
        self.date_entry = DateEntry(form_frame, width=12, background=self.colors["accent"], 
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=1, padx=(0,10), pady=5)
        
        tk.Label(form_frame, text="Next Payment Date", bg="white", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w")
        self.next_payment_date_entry = DateEntry(form_frame, width=12, background=self.colors["primary"], 
                                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        
        plan = str(self.loan_data.get('payment_plan', 'Monthly')).lower()
        suggested_date = datetime.date.today() + (datetime.timedelta(days=7) if "weekly" in plan else datetime.timedelta(days=30))
        self.next_payment_date_entry.set_date(suggested_date)
        self.next_payment_date_entry.grid(row=1, column=2, padx=(0,10), pady=5)
        
        tk.Label(form_frame, text="Payment Method", bg="white", font=("Segoe UI", 9)).grid(row=0, column=3, sticky="w")
        self.method_var = tk.StringVar(value='Bank Transfer')
        self.method_combo = ttk.Combobox(form_frame, textvariable=self.method_var, 
                                          values=['Cash', 'Bank Transfer', 'Mobile Money', 'Cheque'], width=12, state='readonly')
        self.method_combo.grid(row=1, column=3, padx=(0,10), pady=5)

        tk.Label(form_frame, text="Received By", bg="white", font=("Segoe UI", 9)).grid(row=0, column=4, sticky="w")
        self.received_by_entry = tk.Entry(form_frame, font=("Segoe UI", 11), width=12, highlightthickness=1, highlightbackground="#dcdde1", relief="flat")
        self.received_by_entry.insert(0, CURRENT_USER_NAME)
        self.received_by_entry.grid(row=1, column=4, pady=5)

        btn_submit = tk.Button(form_frame, text="CONFIRM PAYMENT", bg=self.colors["success"], fg="white", 
                               font=("Segoe UI", 9, "bold"), relief="flat", padx=15, command=self.record_payment, cursor="hand2")
        btn_submit.grid(row=0, column=5, rowspan=2, padx=(15, 0), sticky="ns")

    def create_payment_view(self):
        view_frame = tk.Frame(self, bg=self.colors["bg"])
        view_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew") 
        view_frame.columnconfigure(0, weight=1)
        view_frame.rowconfigure(1, weight=1)

        tk.Label(view_frame, text="PAYMENT TRANSACTION HISTORY", font=("Segoe UI", 10, "bold"), bg=self.colors["bg"], fg=self.colors["primary"]).grid(row=0, column=0, sticky="w", pady=5)

        columns = ("date", "amount", "method", "received_by", "recorded_date")
        self.payments_tree = ttk.Treeview(view_frame, columns=columns, show="headings", selectmode='browse')
        
        for col in columns:
            self.payments_tree.heading(col, text=col.replace("_", " ").title())
            self.payments_tree.column(col, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)
        self.payments_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

    def create_action_buttons(self):
        action_frame = tk.Frame(self, bg=self.colors["bg"])
        action_frame.grid(row=3, column=0, padx=20, pady=15, sticky="ew") 
        
        tk.Button(action_frame, text="← Return to Management", font=("Segoe UI", 10), bg="#95a5a6", fg="white", 
                  relief="flat", padx=15, command=self._handle_go_back, cursor="hand2").pack(side="left")
        
        tk.Button(action_frame, text="🛑 Sign Out System", font=("Segoe UI", 10, "bold"), bg=self.colors["logout"], fg="white", 
                  relief="flat", padx=20, command=self.handle_logout, cursor="hand2").pack(side="left", padx=20)
        
        tk.Button(action_frame, text="🖨️ Print Receipt for Selected", font=("Segoe UI", 10, "bold"), bg=self.colors["accent"], fg="white", 
                  relief="flat", padx=20, command=self.generate_receipt, cursor="hand2").pack(side="right")

    def _handle_go_back(self):
        try:
            # FIX: Ensure filename matches the actual file name on your disk
            # If your main file is "loan management.py", change underscore to space.
            filename = "loan management.py" if os.path.exists("loan management.py") else "loan_management.py"
            subprocess.Popen([sys.executable, filename, CURRENT_USER_ROLE, CURRENT_USER_NAME])
            self.destroy()
        except Exception as e:
            messagebox.showerror("Navigation Error", f"Failed to open management: {e}")

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out?"):
            try:
                subprocess.Popen([sys.executable, "login.py"])
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to logout: {e}")

    def load_payments(self):
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
            
        payment_list = database.get_payments_by_loan(self.loan_id)
        total_paid = database.get_total_paid_for_loan(self.loan_id)
        
        for payment in payment_list:
            rec_date = payment.get('recorded_date', 'N/A')
            if isinstance(rec_date, datetime.datetime):
                rec_date = rec_date.strftime("%Y-%m-%d %H:%M")
            
            self.payments_tree.insert("", tk.END, values=(
                payment.get('payment_date'),
                f"{float(payment.get('payment_amount', 0.0)):,.2f}",
                payment.get('payment_method', 'N/A'),
                payment.get('received_by', 'N/A'),
                rec_date
            ))
            
        loan_amount = float(self.loan_data.get('loan_amount', 0))
        remaining = loan_amount - total_paid
        self.total_paid_var.set(f"RWF {total_paid:,.2f}")
        self.remaining_var.set(f"RWF {max(0, remaining):,.2f}")
        
        new_status = self.loan_data.get('status', 'Approved')
        if remaining <= 0.01:
            new_status = "Fully Paid" 
        elif remaining > 0.01 and self.loan_data.get('status') == "Fully Paid":
            new_status = "Under Payment"
        
        if self.loan_data.get('status') != new_status:
            database.update_loan_status(self.loan_id, new_status)
            self.loan_data['status'] = new_status

    def record_payment(self):
        amount_str = self.amount_entry.get().strip()
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Enter a valid payment amount.")
            return

        received_by = self.received_by_entry.get().strip()
        next_payment_date = self.next_payment_date_entry.get()
        payment_date = self.date_entry.get()

        payment_data = {
            'loan_id': self.loan_id,
            'customer_name': self.loan_data.get('customer_name'),
            'payment_amount': amount,
            'payment_date': payment_date,
            'next_payment_date': next_payment_date,
            'payment_method': self.method_var.get(),
            'received_by': received_by,
            'recorded_date': datetime.datetime.now()
        }
        
        if database.save_payment(payment_data):
            database.db['loans'].update_one({"_id": self.loan_id}, {"$set": {"next_payment": next_payment_date}})
            messagebox.showinfo("Success", "Payment recorded successfully.")
            self.amount_entry.delete(0, tk.END)
            self.load_payments()
        else:
            messagebox.showerror("Error", "Failed to save payment.")

    def generate_receipt(self):
        selected = self.payments_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a payment.")
            return

        values = self.payments_tree.item(selected)['values']
        receipt_win = tk.Toplevel(self)
        receipt_win.title("Payment Receipt")
        receipt_win.geometry("400x550")
        receipt_win.config(bg="white")
        
        receipt_text = f"""
        ===============================
                OFFICIAL RECEIPT
        ===============================
        LOAN MANAGEMENT SYSTEM
        Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
        -------------------------------
        CUSTOMER DETAILS:
        Name: {self.loan_data.get('customer_name')}
        
        PAYMENT DETAILS:
        Date Paid: {values[0]}
        Amount: RWF {values[1]}
        Method: {values[2]}
        Received By: {values[3]}
        
        LOAN STATUS:
        Total Paid: {self.total_paid_var.get()}
        Balance: {self.remaining_var.get()}
        -------------------------------
        NEXT DUE DATE: {self.loan_data.get('next_payment', 'N/A')}
        
        Thank you!
        ===============================
        """
        text_widget = tk.Text(receipt_win, font=("Courier", 10), padx=20, pady=20, relief="flat")
        text_widget.insert(tk.END, receipt_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(expand=True, fill="both")
        tk.Button(receipt_win, text="PRINT", bg=self.colors["primary"], fg="white", command=lambda: messagebox.showinfo("Printer", "Printing...")).pack(pady=10)

if __name__ == "__main__":
    app = RepaymentWindow()
    app.mainloop()