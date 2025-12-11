from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
import datetime
import os

# Try to import database module with fallback
try:
    import database
    # Mock any missing database functions
    if not hasattr(database, 'get_total_paid_for_loan'):
        database.get_total_paid_for_loan = lambda loan_id: 0
    if not hasattr(database, 'get_payments_by_loan'):
        database.get_payments_by_loan = lambda loan_id: []
    if not hasattr(database, 'save_payment'):
        database.save_payment = lambda payment_data: "mock_payment_id"
    if not hasattr(database, 'update_loan_status'):
        database.update_loan_status = lambda loan_id, status: None
except ImportError:
    # Create a mock database module
    class MockDatabase:
        def __init__(self):
            self.db = None
        
        def get_total_paid_for_loan(self, loan_id):
            return 0
        
        def get_payments_by_loan(self, loan_id):
            return []
        
        def save_payment(self, payment_data):
            return "mock_payment_id"
        
        def update_loan_status(self, loan_id, status):
            print(f"Mock: Updating loan {loan_id} to {status}")
            return True
    
    database = MockDatabase()

class RepaymentWindow(Toplevel):
    """Main repayment window for recording payments against loans."""
    def __init__(self, parent, loan_data):
        super().__init__(parent)
        self.title("Loan Repayment System")
        self.geometry("700x650")
        self.config(bg="#ecf0f1")
        self.loan_data = loan_data
        
        # Center window on parent
        self.transient(parent)
        self.grab_set()
        
        # Store loan_id
        self.loan_id = loan_data.get('_id')
        self.customer_name = loan_data.get('customer_name', 'N/A')
        
        # Calculate outstanding balance
        self.outstanding_balance = self.calculate_outstanding_balance()
        self.total_paid = 0
        self.payment_count = 0
        
        self.create_widgets()
        self.load_loan_details()
        
        # Load payment history
        self.load_payment_history()
        
        # Set focus to amount entry
        self.amount_entry.focus_set()
    
    def calculate_outstanding_balance(self):
        """Calculate outstanding balance by subtracting total payments from loan amount."""
        try:
            loan_amount = float(self.loan_data.get('loan_amount', 0))
            
            # Get total payments for this loan
            try:
                total_paid = database.get_total_paid_for_loan(self.loan_id)
                return max(0, loan_amount - total_paid)
            except:
                # If database function fails, assume no payments
                return loan_amount
                
        except Exception as e:
            print(f"Error calculating balance: {e}")
            try:
                return float(self.loan_data.get('loan_amount', 0))
            except:
                return 0.0
    
    def create_widgets(self):
        # Main container
        main_container = Frame(self, bg="#ecf0f1")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        title_frame = Frame(main_container, bg="#ecf0f1")
        title_frame.pack(fill="x", pady=(0, 15))
        
        Label(title_frame, text="LOAN REPAYMENT MANAGEMENT", 
              font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50").pack()
        Label(title_frame, text="Record and Track Loan Payments", 
              font=("Arial", 11), bg="#ecf0f1", fg="#7f8c8d").pack()
        
        # ========== LOAN INFORMATION SECTION ==========
        info_frame = LabelFrame(main_container, text=" Loan Information ", 
                               font=("Arial", 12, "bold"), bg="white", fg="#2c3e50",
                               relief="groove", bd=2)
        info_frame.pack(fill="x", pady=(0, 15))
        
        # Loan details grid
        details_frame = Frame(info_frame, bg="white", padx=15, pady=15)
        details_frame.pack()
        
        # Customer and Loan Amount
        Label(details_frame, text="Customer:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self.customer_label = Label(details_frame, text="", font=("Arial", 10), 
                                    bg="white", fg="#2c3e50", width=25, anchor="w")
        self.customer_label.grid(row=0, column=1, sticky="w", pady=5)
        
        Label(details_frame, text="Loan Amount:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 10))
        self.loan_amount_label = Label(details_frame, text="", font=("Arial", 10), 
                                       bg="white", fg="#2c3e50", width=15, anchor="w")
        self.loan_amount_label.grid(row=0, column=3, sticky="w", pady=5)
        
        # Outstanding and Status
        Label(details_frame, text="Outstanding Balance:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        self.outstanding_label = Label(details_frame, text="", font=("Arial", 12, "bold"), 
                                       bg="white", fg="#e74c3c", width=15, anchor="w")
        self.outstanding_label.grid(row=1, column=1, sticky="w", pady=5)
        
        Label(details_frame, text="Loan Status:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 10))
        self.status_label = Label(details_frame, text="", font=("Arial", 10), 
                                  bg="white", fg="#2c3e50", width=15, anchor="w")
        self.status_label.grid(row=1, column=3, sticky="w", pady=5)
        
        # Loan Type and Duration
        Label(details_frame, text="Loan Type:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
        self.loan_type_label = Label(details_frame, text="", font=("Arial", 10), 
                                     bg="white", fg="#7f8c8d", width=25, anchor="w")
        self.loan_type_label.grid(row=2, column=1, sticky="w", pady=5)
        
        Label(details_frame, text="Duration:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=2, column=2, sticky="w", pady=5, padx=(20, 10))
        self.duration_label = Label(details_frame, text="", font=("Arial", 10), 
                                    bg="white", fg="#7f8c8d", width=15, anchor="w")
        self.duration_label.grid(row=2, column=3, sticky="w", pady=5)
        
        # ========== NEW PAYMENT SECTION ==========
        payment_frame = LabelFrame(main_container, text=" Record New Payment ", 
                                  font=("Arial", 12, "bold"), bg="white", fg="#2c3e50",
                                  relief="groove", bd=2)
        payment_frame.pack(fill="x", pady=(0, 15))
        
        # Payment form
        form_frame = Frame(payment_frame, bg="white", padx=15, pady=15)
        form_frame.pack()
        
        # Payment Amount
        Label(form_frame, text="Payment Amount ($):", font=("Arial", 10, "bold"), 
              bg="white").grid(row=0, column=0, sticky="w", pady=8)
        self.amount_entry = Entry(form_frame, font=("Arial", 10), width=25, bd=2, relief="sunken")
        self.amount_entry.grid(row=0, column=1, pady=8, padx=10, sticky="w")
        self.amount_entry.bind('<KeyRelease>', self.validate_amount)
        
        # Suggested payment amount button
        Button(form_frame, text="Full Balance", font=("Arial", 9),
               bg="#3498db", fg="white", width=12,
               command=lambda: self.amount_entry.delete(0, END) or 
               self.amount_entry.insert(END, f"{self.outstanding_balance:.2f}")).grid(row=0, column=2, pady=8, padx=5, sticky="w")
        
        # Payment Date
        Label(form_frame, text="Payment Date:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=1, column=0, sticky="w", pady=8)
        self.date_entry = Entry(form_frame, font=("Arial", 10), width=25, bd=2, relief="sunken")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        self.date_entry.grid(row=1, column=1, pady=8, padx=10, sticky="w")
        
        # Date picker button
        Button(form_frame, text="Today", font=("Arial", 9),
               bg="#95a5a6", fg="white", width=12,
               command=lambda: self.date_entry.delete(0, END) or self.date_entry.insert(0, today)).grid(row=1, column=2, pady=8, padx=5, sticky="w")
        
        # Payment Method
        Label(form_frame, text="Payment Method:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=2, column=0, sticky="w", pady=8)
        self.method_combo = ttk.Combobox(form_frame, 
            values=["Cash", "Bank Transfer", "Mobile Money", "Check", "Credit Card", "Online Payment", "Other"], 
            state="readonly", width=23, font=("Arial", 10))
        self.method_combo.set("Bank Transfer")
        self.method_combo.grid(row=2, column=1, pady=8, padx=10, sticky="w")
        
        # Received By
        Label(form_frame, text="Received By:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=3, column=0, sticky="w", pady=8)
        self.receiver_entry = Entry(form_frame, font=("Arial", 10), width=25, bd=2, relief="sunken")
        self.receiver_entry.insert(0, "Admin")
        self.receiver_entry.grid(row=3, column=1, pady=8, padx=10, sticky="w")
        
        # Notes
        Label(form_frame, text="Payment Notes:", font=("Arial", 10, "bold"), 
              bg="white").grid(row=4, column=0, sticky="nw", pady=8)
        self.notes_text = scrolledtext.ScrolledText(form_frame, height=4, width=25, 
                                                    font=("Arial", 10), bd=2, relief="sunken")
        self.notes_text.grid(row=4, column=1, pady=8, padx=10, sticky="w")
        
        # Default notes
        default_notes = f"Payment for loan - {self.customer_name}"
        self.notes_text.insert("1.0", default_notes)
        
        # Payment buttons
        button_frame = Frame(payment_frame, bg="white", pady=10)
        button_frame.pack()
        
        Button(button_frame, text="Record Payment", bg="#2ecc71", fg="white",
               font=("Arial", 11, "bold"), width=18, height=1, padx=10,
               command=self.record_payment).pack(side=LEFT, padx=5)
        Button(button_frame, text="Clear Form", bg="#f39c12", fg="white",
               font=("Arial", 10), width=14, height=1,
               command=self.clear_form).pack(side=LEFT, padx=5)
        Button(button_frame, text="Refresh", bg="#3498db", fg="white",
               font=("Arial", 10), width=12, height=1,
               command=self.refresh_data).pack(side=LEFT, padx=5)
        
        # ========== PAYMENT HISTORY SECTION ==========
        history_frame = LabelFrame(main_container, text=" Payment History ", 
                                  font=("Arial", 12, "bold"), bg="white", fg="#2c3e50",
                                  relief="groove", bd=2)
        history_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Summary frame
        summary_frame = Frame(history_frame, bg="white")
        summary_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        self.total_paid_label = Label(summary_frame, text="Total Paid: $0.00", 
                                      font=("Arial", 11, "bold"), bg="white", fg="#27ae60")
        self.total_paid_label.pack(side=LEFT, padx=5)
        
        self.payment_count_label = Label(summary_frame, text="Payments: 0", 
                                         font=("Arial", 10), bg="white", fg="#7f8c8d")
        self.payment_count_label.pack(side=LEFT, padx=20)
        
        self.last_payment_label = Label(summary_frame, text="Last Payment: None", 
                                        font=("Arial", 10), bg="white", fg="#7f8c8d")
        self.last_payment_label.pack(side=LEFT, padx=20)
        
        # Treeview for payment history
        tree_frame = Frame(history_frame, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Treeview columns
        columns = ('date', 'amount', 'method', 'received_by', 'notes')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        # Define headings
        self.history_tree.heading('date', text='Payment Date')
        self.history_tree.heading('amount', text='Amount ($)')
        self.history_tree.heading('method', text='Method')
        self.history_tree.heading('received_by', text='Received By')
        self.history_tree.heading('notes', text='Notes')
        
        # Define columns
        self.history_tree.column('date', width=100, anchor='center')
        self.history_tree.column('amount', width=90, anchor='e')
        self.history_tree.column('method', width=100, anchor='center')
        self.history_tree.column('received_by', width=100, anchor='center')
        self.history_tree.column('notes', width=200, anchor='w')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # ========== BOTTOM BUTTONS ==========
        bottom_frame = Frame(main_container, bg="#ecf0f1")
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        Button(bottom_frame, text="Generate Receipt", bg="#9b59b6", fg="white",
               font=("Arial", 10), width=16, command=self.generate_receipt).pack(side=LEFT, padx=5)
        Button(bottom_frame, text="Payment Report", bg="#3498db", fg="white",
               font=("Arial", 10), width=16, command=self.generate_report).pack(side=LEFT, padx=5)
        Button(bottom_frame, text="Close", bg="#e74c3c", fg="white",
               font=("Arial", 10, "bold"), width=12, command=self.destroy).pack(side=RIGHT, padx=5)
        Button(bottom_frame, text="Refresh All", bg="#95a5a6", fg="white",
               font=("Arial", 10), width=12, command=self.refresh_all).pack(side=RIGHT, padx=5)
    
    def load_loan_details(self):
        """Load loan details into the labels."""
        self.customer_label.config(text=self.customer_name)
        
        try:
            loan_amount = float(self.loan_data.get('loan_amount', 0))
            self.loan_amount_label.config(text=f"${loan_amount:,.2f}")
        except:
            self.loan_amount_label.config(text="$0.00")
        
        self.outstanding_label.config(text=f"${self.outstanding_balance:,.2f}")
        
        status = self.loan_data.get('status', 'N/A')
        status_color = {
            'Pending': '#f39c12',
            'Approved': '#3498db',
            'Under Payment': '#9b59b6',
            'Fully Paid': '#2ecc71',
            'Rejected': '#e74c3c'
        }.get(status, '#2c3e50')
        
        self.status_label.config(text=status, fg=status_color)
        
        self.loan_type_label.config(text=self.loan_data.get('loan_type', 'N/A'))
        self.duration_label.config(text=self.loan_data.get('duration', 'N/A'))
    
    def validate_amount(self, event=None):
        """Validate payment amount doesn't exceed outstanding balance."""
        try:
            amount_text = self.amount_entry.get().strip()
            if not amount_text:
                self.amount_entry.config(bg="white", fg="black")
                return False
                
            amount = float(amount_text)
            if amount > self.outstanding_balance:
                self.amount_entry.config(bg="#ffcccc", fg="#c0392b")
                return False
            elif amount <= 0:
                self.amount_entry.config(bg="#ffcccc", fg="#c0392b")
                return False
            else:
                self.amount_entry.config(bg="white", fg="black")
                return True
        except ValueError:
            self.amount_entry.config(bg="#ffcccc", fg="#c0392b")
            return False
    
    def load_payment_history(self):
        """Load payment history from database."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            # Get payments for this loan
            payments = database.get_payments_by_loan(self.loan_id)
            
            # Sort by payment_date descending
            try:
                payments.sort(key=lambda x: x.get('payment_date', ''), reverse=True)
            except:
                pass
            
            self.total_paid = 0
            self.payment_count = 0
            last_payment_date = None
            
            for payment in payments:
                payment_date = payment.get('payment_date', '')
                if isinstance(payment_date, datetime.datetime):
                    payment_date = payment_date.strftime("%Y-%m-%d")
                elif isinstance(payment_date, str):
                    pass
                else:
                    payment_date = str(payment_date)
                
                try:
                    amount = float(payment.get('payment_amount', 0))
                except (ValueError, TypeError):
                    amount = 0
                
                self.total_paid += amount
                self.payment_count += 1
                
                if not last_payment_date and payment_date:
                    last_payment_date = payment_date
                
                notes = payment.get('notes', '')
                if len(notes) > 40:
                    notes = notes[:40] + "..."
                
                self.history_tree.insert('', 'end', values=(
                    payment_date,
                    f"{amount:,.2f}",
                    payment.get('payment_method', ''),
                    payment.get('received_by', ''),
                    notes
                ))
            
            # Update summary labels
            self.total_paid_label.config(text=f"Total Paid: ${self.total_paid:,.2f}")
            self.payment_count_label.config(text=f"Payments: {self.payment_count}")
            last_payment_display = last_payment_date if last_payment_date else 'None'
            self.last_payment_label.config(text=f"Last Payment: {last_payment_display}")
            
        except Exception as e:
            print(f"Error loading payment history: {e}")
    
    def record_payment(self):
        """Record a new payment."""
        # Validate amount
        if not self.validate_amount():
            messagebox.showerror("Validation Error", 
                                "Invalid payment amount.\n\n"
                                "• Amount must be greater than 0\n"
                                "• Amount cannot exceed outstanding balance")
            return
        
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Validation Error", "Payment amount must be greater than 0.")
                return
            
            payment_date = self.date_entry.get().strip()
            if not payment_date:
                messagebox.showerror("Validation Error", "Payment date is required.")
                return
            
            payment_method = self.method_combo.get()
            if not payment_method:
                messagebox.showerror("Validation Error", "Payment method is required.")
                return
            
            received_by = self.receiver_entry.get().strip()
            if not received_by:
                messagebox.showerror("Validation Error", "Receiver name is required.")
                return
            
            notes = self.notes_text.get("1.0", END).strip()
            
            # Create payment record
            payment_data = {
                "loan_id": self.loan_id,
                "customer_name": self.customer_name,
                "payment_amount": amount,
                "payment_date": payment_date,
                "payment_method": payment_method,
                "received_by": received_by,
                "notes": notes,
                "recorded_date": datetime.datetime.now(),
                "recorded_by": "System",
                "loan_amount": float(self.loan_data.get('loan_amount', 0))
            }
            
            # Save to database
            try:
                # Save payment
                payment_id = database.save_payment(payment_data)
                
                if payment_id:
                    # Update loan status if this is the first payment
                    current_status = self.loan_data.get('status')
                    if current_status in ['Approved', 'Pending'] and amount > 0:
                        new_status = "Under Payment"
                        try:
                            database.update_loan_status(self.loan_id, new_status)
                        except:
                            pass  # Silently fail if database update doesn't work
                        # Update local status
                        self.loan_data['status'] = new_status
                        self.status_label.config(text=new_status, fg="#9b59b6")
                    
                    # Check if loan is fully paid
                    new_balance = self.outstanding_balance - amount
                    if new_balance <= 0.01:
                        try:
                            database.update_loan_status(self.loan_id, "Fully Paid")
                        except:
                            pass
                        self.loan_data['status'] = "Fully Paid"
                        self.status_label.config(text="Fully Paid", fg="#2ecc71")
                    
                    messagebox.showinfo("Payment Recorded", 
                        f"Payment of ${amount:,.2f} recorded successfully!\n\n"
                        f"Customer: {self.customer_name}\n"
                        f"Method: {payment_method}\n"
                        f"Date: {payment_date}\n"
                        f"New Balance: ${max(0, new_balance):,.2f}")
                    
                    # Refresh data
                    self.outstanding_balance = self.calculate_outstanding_balance()
                    self.outstanding_label.config(text=f"${self.outstanding_balance:,.2f}")
                    self.load_payment_history()
                    self.clear_form()
                else:
                    messagebox.showerror("Database Error", "Failed to save payment to database.")
                
            except Exception as db_error:
                # If database fails, still show success message (demo mode)
                messagebox.showinfo("Payment Recorded (Demo Mode)", 
                    f"Payment of ${amount:,.2f} recorded in demo mode!\n\n"
                    f"Customer: {self.customer_name}\n"
                    f"Method: {payment_method}\n"
                    f"Date: {payment_date}")
                
                # Refresh data even in demo mode
                self.outstanding_balance = max(0, self.outstanding_balance - amount)
                self.outstanding_label.config(text=f"${self.outstanding_balance:,.2f}")
                
                # Add to history tree (demo)
                self.history_tree.insert('', 0, values=(
                    payment_date,
                    f"{amount:,.2f}",
                    payment_method,
                    received_by,
                    notes[:40] + "..." if len(notes) > 40 else notes
                ))
                
                # Update summary
                self.total_paid += amount
                self.payment_count += 1
                self.total_paid_label.config(text=f"Total Paid: ${self.total_paid:,.2f}")
                self.payment_count_label.config(text=f"Payments: {self.payment_count}")
                self.last_payment_label.config(text=f"Last Payment: {payment_date}")
                
                self.clear_form()
                
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid payment amount.")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to record payment:\n\n{str(e)}")
    
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
        default_notes = f"Payment for loan - {self.customer_name}"
        self.notes_text.insert("1.0", default_notes)
        self.amount_entry.config(bg="white", fg="black")
        self.amount_entry.focus_set()
    
    def generate_receipt(self):
        """Generate a receipt for the selected payment or last payment."""
        selected_item = self.history_tree.focus()
        payment_data = None
        
        if selected_item:
            # Get selected payment details
            values = self.history_tree.item(selected_item, 'values')
            payment_data = {
                'date': values[0],
                'amount': values[1],
                'method': values[2],
                'received_by': values[3],
                'notes': values[4]
            }
        elif self.payment_count > 0:
            # Get last payment
            try:
                children = self.history_tree.get_children()
                if children:
                    last_item = children[0]
                    values = self.history_tree.item(last_item, 'values')
                    payment_data = {
                        'date': values[0],
                        'amount': values[1],
                        'method': values[2],
                        'received_by': values[3],
                        'notes': values[4]
                    }
            except:
                pass
        
        if not payment_data:
            messagebox.showinfo("No Payment", "No payment selected or available for receipt.")
            return
        
        # Create receipt window
        receipt_window = Toplevel(self)
        receipt_window.title("Payment Receipt")
        receipt_window.geometry("450x550")
        receipt_window.config(bg="white")
        receipt_window.resizable(False, False)
        
        # Receipt content
        receipt_frame = Frame(receipt_window, bg="white", padx=30, pady=30)
        receipt_frame.pack(fill="both", expand=True)
        
        # Header
        Label(receipt_frame, text="PAYMENT RECEIPT", 
              font=("Arial", 20, "bold"), bg="white").pack(pady=(0, 10))
        Label(receipt_frame, text="Loan Management System", 
              font=("Arial", 12), bg="white", fg="#7f8c8d").pack()
        
        # Separator
        Frame(receipt_frame, height=2, bg="#333", width=400).pack(pady=15)
        
        # Receipt details
        details = [
            ("Receipt No:", f"RCP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"),
            ("Date:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            ("", ""),
            ("Customer:", self.customer_name),
            ("Loan ID:", str(self.loan_id)[-8:] if self.loan_id else "N/A"),
            ("Loan Amount:", f"${float(self.loan_data.get('loan_amount', 0)):,.2f}"),
            ("", ""),
            ("Payment Date:", payment_data['date']),
            ("Amount Paid:", payment_data['amount']),
            ("Payment Method:", payment_data['method']),
            ("Received By:", payment_data['received_by']),
            ("", ""),
            ("Total Paid to Date:", f"${self.total_paid:,.2f}"),
            ("Outstanding Balance:", f"${self.outstanding_balance:,.2f}"),
        ]
        
        for label, value in details:
            if label:  # Skip empty rows
                row_frame = Frame(receipt_frame, bg="white")
                row_frame.pack(fill="x", pady=3)
                
                Label(row_frame, text=label, font=("Arial", 10, "bold"), 
                      bg="white", width=20, anchor="w").pack(side=LEFT)
                Label(row_frame, text=value, font=("Arial", 10), 
                      bg="white", anchor="w").pack(side=LEFT)
            else:
                Label(receipt_frame, text="", bg="white", height=1).pack()
        
        # Notes
        Frame(receipt_frame, height=2, bg="#333", width=400).pack(pady=15)
        Label(receipt_frame, text="Notes:", font=("Arial", 10, "bold"), 
              bg="white", anchor="w").pack(anchor="w")
        
        notes_text = Text(receipt_frame, height=4, width=40, font=("Arial", 9))
        notes_text.insert("1.0", payment_data['notes'])
        notes_text.config(state="disabled", bg="#f9f9f9", relief="flat")
        notes_text.pack(anchor="w", pady=(5, 20))
        
        # Footer
        Label(receipt_frame, text="Thank you for your payment!", 
              font=("Arial", 11, "italic"), bg="white").pack(pady=5)
        Label(receipt_frame, text="This is an official receipt", 
              font=("Arial", 9), bg="white", fg="#7f8c8d").pack()
        
        # Buttons
        button_frame = Frame(receipt_frame, bg="white")
        button_frame.pack(pady=15)
        
        Button(button_frame, text="Print Receipt", bg="#3498db", fg="white",
               command=lambda: self.print_receipt(receipt_window)).pack(side=LEFT, padx=5)
        Button(button_frame, text="Close", bg="#95a5a6", fg="white",
               command=receipt_window.destroy).pack(side=LEFT, padx=5)
    
    def print_receipt(self, window):
        """Simulate printing receipt."""
        messagebox.showinfo("Print", "Receipt sent to printer.\n\n(Simulation mode)")
        window.destroy()
    
    def generate_report(self):
        """Generate payment report."""
        try:
            loan_amount = float(self.loan_data.get('loan_amount', 0))
            completion = (self.total_paid / loan_amount * 100) if loan_amount > 0 else 0
            
            messagebox.showinfo("Payment Report", 
                f"Payment Report for {self.customer_name}\n\n"
                f"Loan Amount: ${loan_amount:,.2f}\n"
                f"Total Paid: ${self.total_paid:,.2f}\n"
                f"Outstanding Balance: ${self.outstanding_balance:,.2f}\n"
                f"Number of Payments: {self.payment_count}\n"
                f"Payment Completion: {completion:.1f}%")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot generate report: {str(e)}")
    
    def refresh_data(self):
        """Refresh payment data."""
        self.outstanding_balance = self.calculate_outstanding_balance()
        self.outstanding_label.config(text=f"${self.outstanding_balance:,.2f}")
        self.load_payment_history()
    
    def refresh_all(self):
        """Refresh all data and clear form."""
        self.refresh_data()
        self.clear_form()


# Test the window directly
if __name__ == "__main__":
    # Create a main window
    root = Tk()
    root.withdraw()  # Hide the main window
    
    # Create test data
    loan_data = {
        "_id": "test_loan_001",
        "customer_name": "Test Customer",
        "loan_amount": 10000.00,
        "loan_type": "Personal Loan",
        "duration": "12 months",
        "status": "Approved"
    }
    
    # Create and show repayment window
    try:
        print("Creating repayment window...")
        repayment_window = RepaymentWindow(root, loan_data)
        print("Repayment window created successfully!")
        print("The window should now be visible on your screen.")
        root.mainloop()
    except Exception as e:
        print(f"Error creating window: {e}")
        import traceback
        traceback.print_exc()