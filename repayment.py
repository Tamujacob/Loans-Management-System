import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
import database

class RepaymentWindow(tk.Toplevel):
    def __init__(self, master, loan_data, go_back_callback):
        super().__init__(master)
        self.master = master
        self.loan_data = loan_data
        self.loan_id = self.loan_data['_id'] 
        self.go_back_callback = go_back_callback 
        
        self.title(f"Repayment Management - {self.loan_data['customer_name']}")
        self.geometry("900x650")
        self.config(bg="#f8f9fa") # Light professional background
        
        # Define Colors
        self.colors = {
            "primary": "#2c3e50",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "bg": "#f8f9fa"
        }

        self.transient(master)
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
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
        
        # LabelFrame styling
        style.configure("TLabelframe", background="#f8f9fa", bordercolor="#dcdde1")
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground=self.colors["primary"])
        
        # Treeview styling
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#dcdde1")
        style.map("Treeview", background=[('selected', self.colors["accent"])])

    def create_summary_frame(self):
        summary_frame = tk.LabelFrame(self, text=" LOAN SUMMARY ", font=("Segoe UI", 11, "bold"), 
                                     bg="white", fg=self.colors["primary"], padx=15, pady=15, relief="flat", highlightthickness=1, highlightbackground="#dcdde1")
        summary_frame.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        
        summary_frame.columnconfigure((0, 2), weight=1)
        
        data = self.loan_data
        
        # Column 1
        tk.Label(summary_frame, text="Customer Name", bg="white", fg="#7f8c8d").grid(row=0, column=0, sticky="w")
        tk.Label(summary_frame, text=data['customer_name'], bg="white", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", pady=(0,10))
        
        tk.Label(summary_frame, text="Total Loan Amount", bg="white", fg="#7f8c8d").grid(row=2, column=0, sticky="w")
        tk.Label(summary_frame, text=f"RWF {data['loan_amount']:,.2f}", bg="white", font=("Segoe UI", 12, "bold"), fg=self.colors["primary"]).grid(row=3, column=0, sticky="w")

        # Column 2 (Financial Stats)
        stats_frame = tk.Frame(summary_frame, bg="#f1f2f6", padx=10, pady=10)
        stats_frame.grid(row=0, column=2, rowspan=4, sticky="nsew")
        
        tk.Label(stats_frame, text="TOTAL PAID", bg="#f1f2f6", font=("Segoe UI", 9, "bold")).pack()
        self.total_paid_var = tk.StringVar(value="RWF 0.00")
        tk.Label(stats_frame, textvariable=self.total_paid_var, bg="#f1f2f6", font=("Segoe UI", 16, "bold"), fg=self.colors["success"]).pack()
        
        tk.Frame(stats_frame, height=1, bg="#dcdde1").pack(fill="x", pady=5)
        
        tk.Label(stats_frame, text="REMAINING BALANCE", bg="#f1f2f6", font=("Segoe UI", 9, "bold")).pack()
        self.remaining_var = tk.StringVar(value="RWF 0.00")
        tk.Label(stats_frame, textvariable=self.remaining_var, bg="#f1f2f6", font=("Segoe UI", 16, "bold"), fg=self.colors["danger"]).pack()

    def create_payment_form(self):
        form_frame = tk.LabelFrame(self, text=" RECORD NEW PAYMENT ", font=("Segoe UI", 10, "bold"), 
                                   bg="white", fg=self.colors["accent"], padx=15, pady=15, relief="flat", highlightthickness=1, highlightbackground="#dcdde1")
        form_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # Amount Entry
        tk.Label(form_frame, text="Amount (RWF)", bg="white", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(form_frame, font=("Segoe UI", 11), width=15, highlightthickness=1, highlightbackground="#dcdde1", relief="flat")
        self.amount_entry.grid(row=1, column=0, padx=(0,15), pady=5)
        
        # Date Entry
        tk.Label(form_frame, text="Payment Date", bg="white", font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w")
        self.date_entry = DateEntry(form_frame, width=14, background=self.colors["accent"], 
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=1, padx=(0,15), pady=5)
        
        # Method Entry
        tk.Label(form_frame, text="Payment Method", bg="white", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w")
        self.method_var = tk.StringVar(value='Bank Transfer')
        self.method_combo = ttk.Combobox(form_frame, textvariable=self.method_var, 
                                         values=['Cash', 'Bank Transfer', 'Mobile Money', 'Cheque'], width=15, state='readonly')
        self.method_combo.grid(row=1, column=2, padx=(0,15), pady=5)

        # Staff Name
        tk.Label(form_frame, text="Received By", bg="white", font=("Segoe UI", 9)).grid(row=0, column=3, sticky="w")
        self.received_by_entry = tk.Entry(form_frame, font=("Segoe UI", 11), width=15, highlightthickness=1, highlightbackground="#dcdde1", relief="flat")
        self.received_by_entry.grid(row=1, column=3, pady=5)

        # Submit Button
        btn_submit = tk.Button(form_frame, text="CONFIRM PAYMENT", bg=self.colors["accent"], fg="white", 
                              font=("Segoe UI", 10, "bold"), relief="flat", padx=20, command=self.record_payment, cursor="hand2")
        btn_submit.grid(row=0, column=4, rowspan=2, padx=(20, 0), sticky="ns")

    def create_payment_view(self):
        view_frame = tk.Frame(self, bg=self.colors["bg"])
        view_frame.grid(row=2, column=0, padx=20, pady=15, sticky="nsew") 
        view_frame.columnconfigure(0, weight=1)
        view_frame.rowconfigure(1, weight=1)

        tk.Label(view_frame, text="PAYMENT TRANSACTION HISTORY", font=("Segoe UI", 10, "bold"), bg=self.colors["bg"], fg=self.colors["primary"]).grid(row=0, column=0, sticky="w", pady=5)

        columns = ("date", "amount", "method", "received_by", "recorded_date")
        self.payments_tree = ttk.Treeview(view_frame, columns=columns, show="headings", selectmode='browse')
        
        self.payments_tree.heading("date", text="Date Paid")
        self.payments_tree.heading("amount", text="Amount (RWF)")
        self.payments_tree.heading("method", text="Payment Method")
        self.payments_tree.heading("received_by", text="Staff")
        self.payments_tree.heading("recorded_date", text="System Log Time")
        
        self.payments_tree.column("date", width=100, anchor=tk.CENTER)
        self.payments_tree.column("amount", width=150, anchor=tk.E)
        self.payments_tree.column("method", width=120, anchor=tk.CENTER)
        self.payments_tree.column("received_by", width=120, anchor=tk.CENTER)
        self.payments_tree.column("recorded_date", width=180, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.payments_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

    def create_action_buttons(self):
        action_frame = tk.Frame(self, bg=self.colors["bg"])
        action_frame.grid(row=3, column=0, padx=20, pady=15, sticky="ew") 
        
        tk.Button(action_frame, text="← Return to Loan Management", font=("Segoe UI", 10), bg="#95a5a6", fg="white", 
                  relief="flat", padx=15, command=self._handle_go_back, cursor="hand2").pack(side="left")

    def load_payments(self):
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
            
        payment_list = database.get_payments_by_loan(self.loan_id)
        total_paid = database.get_total_paid_for_loan(self.loan_id)
        
        for i, payment in enumerate(payment_list):
            recorded_date = payment.get('recorded_date', 'N/A')
            if isinstance(recorded_date, datetime.datetime):
                recorded_date = recorded_date.strftime("%Y-%m-%d %H:%M")
            
            self.payments_tree.insert("", tk.END, values=(
                payment.get('payment_date'),
                f"{payment.get('payment_amount', 0.0):,.2f}",
                payment.get('payment_method', 'N/A'),
                payment.get('received_by', 'N/A'),
                recorded_date
            ))
            
        loan_amount = float(self.loan_data['loan_amount'])
        remaining = loan_amount - total_paid
        
        self.total_paid_var.set(f"RWF {total_paid:,.2f}")
        self.remaining_var.set(f"RWF {remaining:,.2f}")
        
        # Logic for status update
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
        if not received_by:
            messagebox.showerror("Validation Error", "Please enter who received the payment.")
            return

        payment_data = {
            'loan_id': self.loan_id,
            'customer_name': self.loan_data['customer_name'],
            'payment_amount': amount,
            'payment_date': self.date_entry.get(),
            'payment_method': self.method_var.get(),
            'received_by': received_by,
            'recorded_date': datetime.datetime.now()
        }
        
        if database.save_payment(payment_data):
            messagebox.showinfo("Success", "Payment recorded successfully.")
            self.amount_entry.delete(0, tk.END)
            self.load_payments()
            self.go_back_callback()
        else:
            messagebox.showerror("Error", "Failed to save payment.")

    def _handle_go_back(self):
        self.go_back_callback()
        self.on_close()

    def on_close(self):
        self.grab_release()
        self.destroy()