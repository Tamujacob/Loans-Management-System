import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from bson.objectid import ObjectId # Kept for ObjectId type reference/safety

# --- Import Database Functions ---
# This imports the real MongoDB getter functions defined in database.py
from database import get_loan_by_id, get_payments_by_loan, get_total_paid_for_loan 


class ViewLoanDetailsPage:
    """
    A Tkinter frame class to display all detailed information and payment history 
    for a single loan, fetched from the MongoDB database.
    """
    def __init__(self, master, loan_id, switch_to_dashboard_callback):
        """
        Initializes the loan details page.
        :param master: The parent Tkinter frame (e.g., the dashboard's main container).
        :param loan_id: The string ID of the loan to display.
        :param switch_to_dashboard_callback: Function to call when 'Back' is clicked.
        """
        self.master = master
        self.loan_id = loan_id
        self.switch_to_dashboard_callback = switch_to_dashboard_callback

        # Clear any existing widgets in the master frame (standard dashboard practice)
        for widget in self.master.winfo_children():
            widget.destroy()

        self.frame = ttk.Frame(self.master, padding="20")
        self.frame.pack(fill='both', expand=True)

        # 1. Fetch Data
        self.loan_data = self._fetch_loan_details(self.loan_id)
        
        if not self.loan_data:
            self._show_not_found()
            return
            
        self.payment_history = self._fetch_payment_history(self.loan_id)

        # 2. Build UI
        self._create_header()
        self._create_loan_info_section()
        self._create_payment_history_section()
        self._create_back_button()

    def _fetch_loan_details(self, loan_id):
        """Fetches loan details using the database function."""
        return get_loan_by_id(loan_id)

    def _fetch_payment_history(self, loan_id):
        """Fetches payment history using the database function."""
        return get_payments_by_loan(loan_id)

    def _show_not_found(self):
        """Displays an error if the loan ID is invalid or not found."""
        ttk.Label(self.frame, text="🛑 Loan Not Found", 
                  font=('Arial', 18, 'bold'), foreground='#a83232').pack(pady=20)
        ttk.Label(self.frame, text=f"No loan details found for ID: {self.loan_id}", font=('Arial', 12)).pack(pady=5)
        self._create_back_button()

    def _create_header(self):
        """Creates the main title header."""
        title_text = f"📝 Loan Details for: {self.loan_data.get('customer_name', 'N/A')}"
        ttk.Label(self.frame, text=title_text, font=('Arial', 20, 'bold')).pack(pady=(10, 15))

    def _create_loan_info_section(self):
        """Creates the section displaying the core loan data."""
        loan_info_frame = ttk.LabelFrame(self.frame, text=" Loan Information ", padding="15")
        loan_info_frame.pack(fill='x', pady=10, padx=5)

        # Helper function to add a row of key/value pairs
        def add_info_row(key, value, row):
            ttk.Label(loan_info_frame, text=f"{key}:", font=('Arial', 11, 'bold')).grid(row=row, column=0, sticky='w', padx=10, pady=3)
            ttk.Label(loan_info_frame, text=value, font=('Arial', 11)).grid(row=row, column=1, sticky='w', padx=10, pady=3)
            loan_info_frame.grid_columnconfigure(1, weight=1) 

        # Format key data points
        loan_id_str = str(self.loan_data.get('_id', 'N/A'))
        amount_str = f"RWF {self.loan_data.get('loan_amount', 0.00):,.2f}"
        interest_str = f"{self.loan_data.get('interest_rate', 0.0)}%"
        
        app_date = self.loan_data.get('application_date', None)
        # Handle datetime object from MongoDB
        app_date_str = app_date.strftime('%Y-%m-%d') if isinstance(app_date, datetime) else 'N/A'
        
        # Display the information
        add_info_row("Loan ID", loan_id_str, 0)
        add_info_row("Loan Type", self.loan_data.get('loan_type', 'N/A'), 1)
        add_info_row("Amount Borrowed", amount_str, 2)
        add_info_row("Interest Rate", interest_str, 3)
        add_info_row("Duration", self.loan_data.get('duration', 'N/A'), 4)
        add_info_row("Application Date", app_date_str, 5)
        add_info_row("Current Status", self.loan_data.get('status', 'N/A'), 6)
        add_info_row("Approved By", self.loan_data.get('approved_by', 'N/A'), 7)

    def _create_payment_history_section(self):
        """Creates a Treeview table for the loan's payment history."""
        
        loan_amount = self.loan_data.get('loan_amount', 0.00)
        # Use the database aggregation function to calculate total paid
        total_paid = get_total_paid_for_loan(self.loan_id)
        remaining_balance = loan_amount - total_paid

        payment_frame = ttk.LabelFrame(self.frame, 
                                       text=f" 💰 Payment History (Paid: RWF {total_paid:,.2f} | Balance: RWF {remaining_balance:,.2f}) ", 
                                       padding="15")
        payment_frame.pack(fill='both', expand=True, pady=15, padx=5)

        # Define the Treeview (table)
        self.payment_tree = ttk.Treeview(payment_frame, columns=('Date', 'Amount', 'Recorded'), show='headings')
        self.payment_tree.heading('Date', text='Payment Date')
        self.payment_tree.heading('Amount', text='Amount Paid (RWF)', anchor='e')
        self.payment_tree.heading('Recorded', text='Record Date')
        
        # Column widths 
        self.payment_tree.column('Date', anchor='center', width=120, stretch=tk.YES)
        self.payment_tree.column('Amount', anchor='e', width=150, stretch=tk.YES)
        self.payment_tree.column('Recorded', anchor='center', width=120, stretch=tk.YES)

        # Insert data into the table
        if self.payment_history:
            for payment in self.payment_history:
                # Use 'payment_date' (user input string) and 'recorded_date' (MongoDB datetime) keys
                pay_date_str = payment.get('payment_date', 'N/A')
                rec_date_obj = payment.get('recorded_date', None)
                
                # Format the MongoDB datetime object
                rec_date_str = rec_date_obj.strftime('%Y-%m-%d %H:%M') if isinstance(rec_date_obj, datetime) else 'N/A'
                
                amount = payment.get('payment_amount', 0.00)
                amount_str = f"{amount:,.2f}"
                
                self.payment_tree.insert('', 'end', values=(pay_date_str, amount_str, rec_date_str))
        else:
            self.payment_tree.insert('', 'end', values=('No payments recorded yet.', '', ''))
            
        # Add scrollbar
        vsb = ttk.Scrollbar(payment_frame, orient="vertical", command=self.payment_tree.yview)
        self.payment_tree.configure(yscrollcommand=vsb.set)

        vsb.pack(side='right', fill='y')
        self.payment_tree.pack(side='left', fill='both', expand=True)

    def _create_back_button(self):
        """Creates a button to return to the main view/dashboard."""
        ttk.Button(self.frame, text="← Back to Loans Dashboard", command=self.switch_to_dashboard_callback).pack(pady=20)