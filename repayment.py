import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
import database # Import the database module directly

class RepaymentWindow(tk.Toplevel):
    def __init__(self, master, loan_data, go_back_callback):
        # 1. Initialize Window
        super().__init__(master)
        self.master = master
        self.loan_data = loan_data
        self.loan_id = self.loan_data['_id'] # Use '_id' as the unique loan identifier
        self.go_back_callback = go_back_callback # Callback function for the back button
        
        self.title(f"Repayment - {self.loan_data['customer_name']}")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 2. Configure Grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1) # Payments view takes up extra space

        # 3. Create Widgets
        self.create_summary_frame()
        self.create_payment_form()
        self.create_payment_view()
        self.create_action_buttons()

        # 4. Initial Load
        self.load_payments()

    # --- Frame & Widget Creation ---

    def create_summary_frame(self):
        """Creates the frame displaying loan summary details."""
        summary_frame = ttk.LabelFrame(self, text="Loan Summary", padding="10")
        summary_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Configure internal grid
        summary_frame.columnconfigure((0, 2), weight=1)
        summary_frame.columnconfigure((1, 3), weight=2)
        
        data = self.loan_data
        
        ttk.Label(summary_frame, text="Loan ID:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(summary_frame, text=data['_id'], font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(summary_frame, text="Customer:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(summary_frame, text=data['customer_name']).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(summary_frame, text="Amount:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.amount_label = ttk.Label(summary_frame, text=f"€{data['loan_amount']:,.2f}")
        self.amount_label.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(summary_frame, text="Status:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.status_label = ttk.Label(summary_frame, text=data.get('status', 'N/A'), foreground='blue')
        self.status_label.grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Separator(summary_frame, orient='horizontal').grid(row=2, column=0, columnspan=4, sticky="ew", pady=5)
        
        ttk.Label(summary_frame, text="Total Paid:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.total_paid_var = tk.StringVar(value="€0.00")
        ttk.Label(summary_frame, textvariable=self.total_paid_var, font=("Arial", 11, "bold"), foreground='green').grid(row=3, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(summary_frame, text="Remaining:").grid(row=3, column=2, sticky="w", padx=5, pady=2)
        self.remaining_var = tk.StringVar(value=f"€{data['loan_amount']:,.2f}")
        ttk.Label(summary_frame, textvariable=self.remaining_var, font=("Arial", 11, "bold"), foreground='red').grid(row=3, column=3, sticky="w", padx=5, pady=2)

    def create_payment_form(self):
        """Creates the form for adding new payments."""
        form_frame = ttk.LabelFrame(self, text="Record New Payment", padding="10")
        form_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        form_frame.columnconfigure((0, 2, 4), weight=1)
        form_frame.columnconfigure((1, 3, 5), weight=2)
        
        # Amount
        ttk.Label(form_frame, text="Payment Amount (€):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.amount_entry = ttk.Entry(form_frame, width=15)
        self.amount_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Payment Date (using tkcalendar)
        ttk.Label(form_frame, text="Payment Date:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.date_entry = DateEntry(form_frame, width=12, background='darkblue', 
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Payment Method
        ttk.Label(form_frame, text="Method:").grid(row=0, column=4, sticky="w", padx=5, pady=2)
        self.method_var = tk.StringVar(value='Cash')
        self.method_combo = ttk.Combobox(form_frame, textvariable=self.method_var, 
                                        values=['Cash', 'Bank Transfer', 'Mobile Money', 'Cheque'], width=15, state='readonly')
        self.method_combo.grid(row=0, column=5, sticky="w", padx=5, pady=2)
        
        # Received By
        ttk.Label(form_frame, text="Received By:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.received_by_entry = ttk.Entry(form_frame, width=15)
        self.received_by_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.notes_entry = ttk.Entry(form_frame, width=40)
        self.notes_entry.grid(row=1, column=3, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # Submit Button
        submit_button = ttk.Button(form_frame, text="Record Payment", command=self.record_payment, style='Accent.TButton')
        submit_button.grid(row=1, column=5, sticky="e", padx=5, pady=2)

    def create_payment_view(self):
        """Creates the Treeview widget to display payment history."""
        view_frame = ttk.LabelFrame(self, text="Payment History", padding="10")
        view_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        view_frame.columnconfigure(0, weight=1)
        view_frame.rowconfigure(0, weight=1)

        columns = ("payment_id", "date", "amount", "method", "received_by", "recorded_date")
        self.payments_tree = ttk.Treeview(view_frame, columns=columns, show="headings", selectmode='browse')
        
        # Define headings and widths
        self.payments_tree.heading("payment_id", text="ID")
        self.payments_tree.heading("date", text="Pmt Date")
        self.payments_tree.heading("amount", text="Amount (€)")
        self.payments_tree.heading("method", text="Method")
        self.payments_tree.heading("received_by", text="Receiver")
        self.payments_tree.heading("recorded_date", text="Recorded On")
        
        self.payments_tree.column("payment_id", width=100, anchor=tk.CENTER)
        self.payments_tree.column("date", width=80, anchor=tk.CENTER)
        self.payments_tree.column("amount", width=80, anchor=tk.E)
        self.payments_tree.column("method", width=100, anchor=tk.CENTER)
        self.payments_tree.column("received_by", width=100, anchor=tk.W)
        self.payments_tree.column("recorded_date", width=120, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.payments_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def create_action_buttons(self):
        """Creates the action button frame (Back button)."""
        action_frame = ttk.Frame(self)
        action_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        action_frame.columnconfigure(0, weight=1)
        
        # Back Button
        back_button = ttk.Button(action_frame, text="← Back to Loans Management", command=self.go_back_callback)
        back_button.grid(row=0, column=0, sticky="w")
        
    # --- Data & Logic Methods ---

    def load_payments(self):
        """Fetches and displays payment history and updates summary."""
        # Clear existing entries
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
            
        # 1. Fetch data
        payment_list = database.get_payments_by_loan(self.loan_id)
        total_paid = database.get_total_paid_for_loan(self.loan_id)
        
        # 2. Update Treeview
        for payment in payment_list:
            # Format date fields for display
            payment_date_str = payment.get('payment_date')
            recorded_date_str = payment.get('recorded_date', 'N/A')
            
            # Format recorded date for display (handle datetime object or string)
            if isinstance(recorded_date_str, datetime.datetime):
                recorded_date_str = recorded_date_str.strftime("%Y-%m-%d %H:%M")
            elif recorded_date_str != 'N/A':
                # Try to parse and format if it's a string from the DB
                try:
                    recorded_date_str = datetime.datetime.strptime(recorded_date_str, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            self.payments_tree.insert("", tk.END, values=(
                str(payment.get('_id', 'N/A'))[:8] + '...', # Truncate ID for view
                payment_date_str,
                f"{payment.get('payment_amount', 0.0):,.2f}",
                payment.get('payment_method', 'N/A'),
                payment.get('received_by', 'N/A'),
                recorded_date_str
            ))
            
        # 3. Update Summary
        loan_amount = float(self.loan_data['loan_amount'])
        remaining = loan_amount - total_paid
        
        self.total_paid_var.set(f"€{total_paid:,.2f}")
        self.remaining_var.set(f"€{remaining:,.2f}")
        
        # 4. Check Loan Status Update
        new_status = self.loan_data.get('status', 'Approved')
        if remaining <= 0.01: # Use a small tolerance for floating point errors
            new_status = "Fully Repaid"
        
        if self.status_label['text'] != new_status:
            database.update_loan_status(self.loan_id, new_status)
            self.status_label.config(text=new_status, foreground='green' if new_status == 'Fully Repaid' else 'blue')


    def record_payment(self):
        """Handles validation and saving of the new payment."""
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get()
        received_by = self.received_by_entry.get().strip()
        notes = self.notes_entry.get().strip()
        
        # 1. Validation
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid positive payment amount.")
            self.amount_entry.focus_set()
            return
            
        if not received_by:
            messagebox.showerror("Validation Error", "Please enter the name of the staff member receiving the payment.")
            self.received_by_entry.focus_set()
            return

        # 2. Prepare Data
        payment_data = {
            'loan_id': self.loan_id,
            'customer_name': self.loan_data['customer_name'],
            'payment_amount': amount,
            'payment_date': date_str,
            'payment_method': self.method_var.get(),
            'received_by': received_by,
            'notes': notes
        }
        
        # 3. Save to Database
        payment_id = database.save_payment(payment_data)
        
        if payment_id:
            messagebox.showinfo("Success", f"Payment of €{amount:,.2f} recorded successfully (ID: {payment_id[:8]}...).")
            # Clear form fields
            self.amount_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
            # Reload data
            self.load_payments()
        else:
            messagebox.showerror("Database Error", "Failed to save payment record.")

    def on_close(self):
        """Handles cleanup when the window is closed."""
        self.destroy()

# ================================================
# DEMO/TESTING BLOCK (MOCK LOAN DATA)
# ================================================
if __name__ == "__main__":
    # 1. Create the main Tkinter root window
    root = tk.Tk()
    root.title("Main Application (Hidden)")
    root.withdraw() # Hide the main window

    # 2. Define mock loan data (must match the structure expected by the window)
    mock_loan_data = {
        '_id': 'LOAN-12345', # Critical ID matching the mock DB placeholder
        'customer_name': 'Jane Doe',
        'loan_amount': 5000.00,
        'loan_type': 'Business',
        'duration': '12 Months',
        'status': 'Approved'
    }

    # 3. Define the placeholder callback for the back button
    def go_back_to_management():
        print("\n--- Back Button Pressed ---")
        print("ACTION: The actual Loans Management Window should be opened here.")
        app.destroy()
        root.quit() # End the main loop for this demo

    # 4. Initialize and run the Repayment Window
    app = RepaymentWindow(root, mock_loan_data, go_back_to_management)
    
    # 5. Apply a default ttk theme for better visuals
    style = ttk.Style()
    style.theme_use('clam')
    
    # Optional Accent Style for the button
    style.configure('Accent.TButton', background='#007BFF', foreground='white', font=('Arial', 10, 'bold'))

    root.mainloop()