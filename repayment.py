from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
import database
import datetime
from bson import ObjectId

class RepaymentWindow(Toplevel):
    """Main repayment window for recording payments against loans."""
    def __init__(self, parent, loan_data):
        super().__init__(parent)
        self.title("Loan Repayment Management")
        self.geometry("600x550")
        self.config(bg="#ecf0f1")
        self.loan_data = loan_data
        
        # Center window on parent
        self.transient(parent)
        self.grab_set()
        
        # Store loan_id
        self.loan_id = loan_data.get('_id')
        
        # Calculate outstanding balance
        self.outstanding_balance = self.calculate_outstanding_balance()
        
        self.create_widgets()
        self.load_loan_details()
        
        # Load payment history
        self.load_payment_history()
    
    def calculate_outstanding_balance(self):
        """Calculate outstanding balance by subtracting total payments from loan amount."""
        try:
            loan_amount = float(self.loan_data.get('loan_amount', 0))
            
            # Get total payments for this loan
            if database.db:
                total_payments = database.db['payments'].aggregate([
                    {"$match": {"loan_id": self.loan_id}},
                    {"$group": {"_id": None, "total": {"$sum": "$payment_amount"}}}
                ])
                
                total_payments_list = list(total_payments)
                if total_payments_list:
                    total_paid = total_payments_list[0].get('total', 0)
                else:
                    total_paid = 0
                    
                return max(0, loan_amount - total_paid)
            else:
                return loan_amount  # Fallback if no database
                
        except Exception as e:
            print(f"Error calculating balance: {e}")
            return float(self.loan_data.get('loan_amount', 0))
    
    def create_widgets(self):
        # Main container
        main_container = Frame(self, bg="#ecf0f1")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = Frame(main_container, bg="#ecf0f1")
        title_frame.pack(fill="x", pady=(0, 10))
        
        Label(title_frame, text="LOAN REPAYMENT SYSTEM", 
              font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").pack()
        
        # Loan Information Card
        info_card = Frame(main_container, bg="white", relief="raised", bd=2)
        info_card.pack(fill="x", pady=(0, 15))
        
        # Card header
        card_header = Frame(info_card, bg="#3498db", height=30)
        card_header.pack(fill="x")
        Label(card_header, text="Loan Information", font=("Arial", 12, "bold"), 
              bg="#3498db", fg="white").pack(side=LEFT, padx=10)
        
        # Loan details grid
        details_frame = Frame(info_card, bg="white", padx=15, pady=15)
        details_frame.pack()
        
        # Row 1
        Label(details_frame, text="Customer:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self.customer_label = Label(details_frame, text="", font=("Arial", 10), 
                                    bg="white", fg="#2c3e50")
        self.customer_label.grid(row=0, column=1, sticky="w", pady=5)
        
        Label(details_frame, text="Loan Amount:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 10))
        self.loan_amount_label = Label(details_frame, text="", font=("Arial", 10), 
                                       bg="white", fg="#2c3e50")
        self.loan_amount_label.grid(row=0, column=3, sticky="w", pady=5)
        
        # Row 2
        Label(details_frame, text="Outstanding:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        self.outstanding_label = Label(details_frame, text="", font=("Arial", 10), 
                                       bg="white", fg="#e74c3c", font=("Arial", 10, "bold"))
        self.outstanding_label.grid(row=1, column=1, sticky="w", pady=5)
        
        Label(details_frame, text="Status:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 10))
        self.status_label = Label(details_frame, text="", font=("Arial", 10), 
                                  bg="white", fg="#2c3e50")
        self.status_label.grid(row=1, column=3, sticky="w", pady=5)
        
        # Row 3
        Label(details_frame, text="Loan ID:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
        self.loan_id_label = Label(details_frame, text="", font=("Arial", 9), 
                                   bg="white", fg="#7f8c8d")
        self.loan_id_label.grid(row=2, column=1, sticky="w", pady=5)
        
        Label(details_frame, text="Duration:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=2, column=2, sticky="w", pady=5, padx=(20, 10))
        self.duration_label = Label(details_frame, text="", font=("Arial", 10), 
                                    bg="white", fg="#2c3e50")
        self.duration_label.grid(row=2, column=3, sticky="w", pady=5)
        
        # Payment Form Card
        payment_card = Frame(main_container, bg="white", relief="groove", bd=1)
        payment_card.pack(fill="x", pady=(0, 15))
        
        # Card header
        payment_header = Frame(payment_card, bg="#2ecc71", height=30)
        payment_header.pack(fill="x")
        Label(payment_header, text="New Payment", font=("Arial", 12, "bold"), 
              bg="#2ecc71", fg="white").pack(side=LEFT, padx=10)
        
        # Payment form
        form_frame = Frame(payment_card, bg="white", padx=15, pady=15)
        form_frame.pack()
        
        # Payment Amount
        Label(form_frame, text="Amount ($):", font=("Arial", 10), 
              bg="white").grid(row=0, column=0, sticky="w", pady=8)
        self.amount_entry = Entry(form_frame, font=("Arial", 10), width=20)
        self.amount_entry.grid(row=0, column=1, pady=8, padx=10)
        self.amount_entry.bind('<KeyRelease>', self.validate_amount)
        
        # Payment Date
        Label(form_frame, text="Date:", font=("Arial", 10), 
              bg="white").grid(row=1, column=0, sticky="w", pady=8)
        self.date_entry = Entry(form_frame, font=("Arial", 10), width=20)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        self.date_entry.grid(row=1, column=1, pady=8, padx=10)
        
        # Payment Method
        Label(form_frame, text="Method:", font=("Arial", 10), 
              bg="white").grid(row=2, column=0, sticky="w", pady=8)
        self.method_combo = ttk.Combobox(form_frame, 
            values=["Cash", "Bank Transfer", "Mobile Money", "Check", "Credit Card", "Other"], 
            state="readonly", width=18, font=("Arial", 10))
        self.method_combo.set("Bank Transfer")
        self.method_combo.grid(row=2, column=1, pady=8, padx=10)
        
        # Received By
        Label(form_frame, text="Received By:", font=("Arial", 10), 
              bg="white").grid(row=3, column=0, sticky="w", pady=8)
        self.receiver_entry = Entry(form_frame, font=("Arial", 10), width=20)
        self.receiver_entry.insert(0, "Admin")  # Default, in real app get from login
        self.receiver_entry.grid(row=3, column=1, pady=8, padx=10)
        
        # Notes
        Label(form_frame, text="Notes:", font=("Arial", 10), 
              bg="white").grid(row=4, column=0, sticky="nw", pady=8)
        self.notes_text = scrolledtext.ScrolledText(form_frame, height=4, width=25, 
                                                    font=("Arial", 10))
        self.notes_text.grid(row=4, column=1, pady=8, padx=10)
        
        # Payment buttons
        button_frame = Frame(payment_card, bg="white", pady=10)
        button_frame.pack()
        
        Button(button_frame, text="Record Payment", bg="#2ecc71", fg="white",
               font=("Arial", 10, "bold"), width=15, height=1,
               command=self.record_payment).pack(side=LEFT, padx=5)
        Button(button_frame, text="Clear Form", bg="#f39c12", fg="white",
               font=("Arial", 10), width=12, height=1,
               command=self.clear_form).pack(side=LEFT, padx=5)
        
        # Payment History Card
        history_card = Frame(main_container, bg="white", relief="groove", bd=1)
        history_card.pack(fill="both", expand=True, pady=(0, 10))
        
        # Card header
        history_header = Frame(history_card, bg="#9b59b6", height=30)
        history_header.pack(fill="x")
        Label(history_header, text="Payment History", font=("Arial", 12, "bold"), 
              bg="#9b59b6", fg="white").pack(side=LEFT, padx=10)
        
        # History frame with treeview
        history_frame = Frame(history_card, bg="white")
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview for payment history
        columns = ('date', 'amount', 'method', 'received_by', 'notes')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=6)
        
        # Define headings
        self.history_tree.heading('date', text='Date')
        self.history_tree.heading('amount', text='Amount')
        self.history_tree.heading('method', text='Method')
        self.history_tree.heading('received_by', text='Received By')
        self.history_tree.heading('notes', text='Notes')
        
        # Define columns
        self.history_tree.column('date', width=100)
        self.history_tree.column('amount', width=80, anchor='e')
        self.history_tree.column('method', width=100)
        self.history_tree.column('received_by', width=100)
        self.history_tree.column('notes', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        # Summary frame
        summary_frame = Frame(history_card, bg="white")
        summary_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.total_paid_label = Label(summary_frame, text="Total Paid: $0.00", 
                                      font=("Arial", 10, "bold"), bg="white", fg="#27ae60")
        self.total_paid_label.pack(side=LEFT, padx=5)
        
        self.payment_count_label = Label(summary_frame, text="Payments: 0", 
                                         font=("Arial", 10), bg="white", fg="#7f8c8d")
        self.payment_count_label.pack(side=LEFT, padx=20)
        
        # Bottom buttons
        bottom_frame = Frame(main_container, bg="#ecf0f1")
        bottom_frame.pack(fill="x", pady=(5, 0))
        
        Button(bottom_frame, text="Generate Receipt", bg="#3498db", fg="white",
               font=("Arial", 10), width=15, command=self.generate_receipt).pack(side=LEFT, padx=5)
        Button(bottom_frame, text="Close", bg="#e74c3c", fg="white",
               font=("Arial", 10), width=10, command=self.destroy).pack(side=RIGHT, padx=5)
        Button(bottom_frame, text="Refresh", bg="#95a5a6", fg="white",
               font=("Arial", 10), width=10, command=self.refresh_data).pack(side=RIGHT, padx=5)
    
    def load_loan_details(self):
        """Load loan details into the labels."""
        self.customer_label.config(
            text=self.loan_data.get('customer_name', 'N/A'))
        
        loan_amount = float(self.loan_data.get('loan_amount', 0))
        self.loan_amount_label.config(
            text=f"${loan_amount:,.2f}")
        
        self.outstanding_label.config(
            text=f"${self.outstanding_balance:,.2f}")
        
        self.status_label.config(
            text=self.loan_data.get('status', 'N/A'))
        
        # Format loan ID (show last 8 chars)
        loan_id = str(self.loan_id)
        if len(loan_id) > 8:
            loan_id = "..." + loan_id[-8:]
        self.loan_id_label.config(text=loan_id)
        
        self.duration_label.config(
            text=self.loan_data.get('duration', 'N/A'))
    
    def validate_amount(self, event=None):
        """Validate payment amount doesn't exceed outstanding balance."""
        try:
            amount_text = self.amount_entry.get()
            if amount_text:
                amount = float(amount_text)
                if amount > self.outstanding_balance:
                    self.amount_entry.config(bg="#ffcccc")
                    return False
                else:
                    self.amount_entry.config(bg="white")
                    return True
        except ValueError:
            self.amount_entry.config(bg="#ffcccc")
            return False
    
    def load_payment_history(self):
        """Load payment history from database."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        if not database.db:
            return
        
        try:
            # Get payments for this loan
            payments = database.db['payments'].find(
                {"loan_id": self.loan_id}
            ).sort("payment_date", -1)
            
            total_paid = 0
            payment_count = 0
            
            for payment in payments:
                payment_date = payment.get('payment_date', '')
                if isinstance(payment_date, datetime.datetime):
                    payment_date = payment_date.strftime("%Y-%m-%d")
                
                amount = payment.get('payment_amount', 0)
                total_paid += amount
                payment_count += 1
                
                self.history_tree.insert('', 'end', values=(
                    payment_date,
                    f"${amount:,.2f}",
                    payment.get('payment_method', ''),
                    payment.get('received_by', ''),
                    payment.get('notes', '')[:30] + "..." if len(payment.get('notes', '')) > 30 else payment.get('notes', '')
                ))
            
            # Update summary labels
            self.total_paid_label.config(text=f"Total Paid: ${total_paid:,.2f}")
            self.payment_count_label.config(text=f"Payments: {payment_count}")
            
        except Exception as e:
            print(f"Error loading payment history: {e}")
    
    def record_payment(self):
        """Record a new payment."""
        # Validate amount
        if not self.validate_amount():
            messagebox.showerror("Validation Error", 
                                "Invalid payment amount. Amount cannot exceed outstanding balance.")
            return
        
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Validation Error", "Payment amount must be greater than 0.")
                return
            
            payment_date = self.date_entry.get()
            if not payment_date:
                messagebox.showerror("Validation Error", "Payment date is required.")
                return
            
            payment_method = self.method_combo.get()
            if not payment_method:
                messagebox.showerror("Validation Error", "Payment method is required.")
                return
            
            received_by = self.receiver_entry.get()
            if not received_by:
                messagebox.showerror("Validation Error", "Receiver name is required.")
                return
            
            notes = self.notes_text.get("1.0", END).strip()
            
            # Create payment record
            payment_data = {
                "loan_id": self.loan_id,
                "customer_name": self.loan_data.get('customer_name'),
                "payment_amount": amount,
                "payment_date": payment_date,
                "payment_method": payment_method,
                "received_by": received_by,
                "notes": notes,
                "recorded_date": datetime.datetime.now(),
                "recorded_by": "System"  # In real app, get from user session
            }
            
            # Save to database
            if database.db:
                result = database.db['payments'].insert_one(payment_data)
                
                # Update loan status if this is the first payment
                if self.loan_data.get('status') == 'Approved' and amount > 0:
                    database.db['loans'].update_one(
                        {"_id": self.loan_id},
                        {"$set": {"status": "Under Payment"}}
                    )
                    # Update local status
                    self.loan_data['status'] = "Under Payment"
                    self.status_label.config(text="Under Payment")
                
                # If fully paid, update status
                if amount >= self.outstanding_balance:
                    database.db['loans'].update_one(
                        {"_id": self.loan_id},
                        {"$set": {"status": "Fully Paid"}}
                    )
                    self.loan_data['status'] = "Fully Paid"
                    self.status_label.config(text="Fully Paid")
                
                messagebox.showinfo("Success", 
                    f"Payment of ${amount:,.2f} recorded successfully!\n"
                    f"Payment ID: {result.inserted_id}")
                
                # Refresh data
                self.outstanding_balance = self.calculate_outstanding_balance()
                self.outstanding_label.config(text=f"${self.outstanding_balance:,.2f}")
                self.load_payment_history()
                self.clear_form()
                
            else:
                messagebox.showerror("Database Error", "Cannot connect to database.")
                
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid payment amount.")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to record payment: {str(e)}")
    
    def clear_form(self):
        """Clear the payment form."""
        self.amount_entry.delete(0, END)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_entry.delete(0, END)
        self.date_entry.insert(0, today)
        self.method_combo.set("Bank Transfer")
        self.receiver_entry.delete(0, END)
        self.receiver_entry.insert(0, "Admin")
        self.notes_text.delete("1.0", END)
        self.amount_entry.config(bg="white")
    
    def generate_receipt(self):
        """Generate a receipt for the selected payment."""
        selected_item = self.history_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", 
                                 "Please select a payment from the history to generate a receipt.")
            return
        
        # Get selected payment details
        values = self.history_tree.item(selected_item, 'values')
        
        # Create receipt window
        receipt_window = Toplevel(self)
        receipt_window.title("Payment Receipt")
        receipt_window.geometry("400x500")
        receipt_window.config(bg="white")
        
        # Simple receipt layout
        receipt_frame = Frame(receipt_window, bg="white", padx=20, pady=20)
        receipt_frame.pack(fill="both", expand=True)
        
        # Header
        Label(receipt_frame, text="PAYMENT RECEIPT", 
              font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 20))
        
        # Company info
        Label(receipt_frame, text="Loan Management System", 
              font=("Arial", 12), bg="white").pack()
        Label(receipt_frame, text="123 Finance Street", 
              font=("Arial", 10), bg="white").pack()
        Label(receipt_frame, text="Phone: (123) 456-7890", 
              font=("Arial", 10), bg="white").pack(pady=(0, 20))
        
        # Separator
        Frame(receipt_frame, height=2, bg="#333").pack(fill="x", pady=10)
        
        # Receipt details
        details_frame = Frame(receipt_frame, bg="white")
        details_frame.pack(fill="x", pady=10)
        
        details = [
            ("Receipt Date:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            ("Customer:", self.loan_data.get('customer_name', 'N/A')),
            ("Payment Date:", values[0]),
            ("Amount:", values[1]),
            ("Method:", values[2]),
            ("Received By:", values[3]),
            ("Loan ID:", str(self.loan_id)[-8:]),
        ]
        
        for i, (label, value) in enumerate(details):
            Label(details_frame, text=label, font=("Arial", 10, "bold"), 
                  bg="white", anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            Label(details_frame, text=value, font=("Arial", 10), 
                  bg="white", anchor="w").grid(row=i, column=1, sticky="w", padx=10, pady=3)
        
        # Notes
        Label(receipt_frame, text="Notes:", font=("Arial", 10, "bold"), 
              bg="white", anchor="w").pack(anchor="w", pady=(10, 0))
        notes_text = Text(receipt_frame, height=4, width=40, font=("Arial", 9))
        notes_text.insert("1.0", values[4] if len(values) > 4 else "")
        notes_text.config(state="disabled")
        notes_text.pack(anchor="w", pady=(0, 20))
        
        # Footer
        Frame(receipt_frame, height=2, bg="#333").pack(fill="x", pady=10)
        Label(receipt_frame, text="Thank you for your payment!", 
              font=("Arial", 11, "italic"), bg="white").pack()
        
        # Print button
        Button(receipt_frame, text="Print Receipt", bg="#3498db", fg="white",
               command=lambda: self.print_receipt(receipt_window)).pack(pady=10)
    
    def print_receipt(self, window):
        """Simulate printing receipt."""
        messagebox.showinfo("Print", "Receipt sent to printer. (Simulation)")
        window.destroy()
    
    def refresh_data(self):
        """Refresh all data."""
        self.outstanding_balance = self.calculate_outstanding_balance()
        self.outstanding_label.config(text=f"${self.outstanding_balance:,.2f}")
        self.load_payment_history()


def main():
    """Test function to run the repayment window independently."""
    root = Tk()
    root.withdraw()  # Hide main window
    
    # Sample loan data for testing
    sample_loan = {
        "_id": ObjectId(),
        "customer_name": "John Doe",
        "loan_amount": 5000.00,
        "duration": "12 months",
        "status": "Approved",
        "loan_id": "LN-001"
    }
    
    repayment_window = RepaymentWindow(root, sample_loan)
    root.mainloop()


if __name__ == "__main__":
    main()