import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from bson.objectid import ObjectId

# --- Import Database Functions ---
from database import get_loan_by_id, get_payments_by_loan, get_total_paid_for_loan 


class ViewLoanDetailsPage:
    """
    A Tkinter Toplevel window content class to display all detailed information 
    and payment history for a single loan, fetched from the MongoDB database.
    """
    def __init__(self, master, loan_id, switch_to_dashboard_callback):
        """
        Initializes the loan details page.
        :param master: The parent Tkinter Toplevel/Frame.
        :param loan_id: The string ID of the loan to display.
        :param switch_to_dashboard_callback: Function to call when 'Back' is clicked.
        """
        self.master = master
        self.loan_id = loan_id
        self.switch_to_dashboard_callback = switch_to_dashboard_callback

        # Clear any existing widgets in the master frame
        for widget in self.master.winfo_children():
            widget.destroy()

        self.frame = ttk.Frame(self.master, padding="20 20 20 5")
        self.frame.pack(fill='both', expand=True)

        # 1. Fetch Data
        self.loan_data = self._fetch_loan_details(self.loan_id)
        
        if not self.loan_data:
            self._show_not_found()
            return
            
        self.payment_history = self._fetch_payment_history(self.loan_id)
        self.loan_amount = self.loan_data.get('loan_amount', 0.00)
        self.total_paid = get_total_paid_for_loan(self.loan_id)
        self.remaining_balance = self.loan_amount - self.total_paid

        # 2. Build UI
        self._create_styles()
        self._create_header_and_back_button()
        self._create_summary_panel()
        self._create_notebook()

    def _create_styles(self):
        """Define custom styles for status colors and labels."""
        style = ttk.Style()
        style.configure('TFrame', background='#f7f9fa')
        style.configure('Header.TLabel', font=('Arial', 24, 'bold'), foreground='#2c3e50')
        style.configure('Summary.TLabel', font=('Arial', 12))
        style.configure('InfoKey.TLabel', font=('Arial', 11, 'bold'), foreground='#555555')
        style.configure('InfoValue.TLabel', font=('Arial', 11))
        
        # Status Tags
        style.configure('Pending.TLabel', background='#fff3cd', foreground='#856404', borderwidth=1, relief='solid')
        style.configure('Approved.TLabel', background='#d4edda', foreground='#155724', borderwidth=1, relief='solid')
        style.configure('Active.TLabel', background='#cce5ff', foreground='#004085', borderwidth=1, relief='solid')
        style.configure('FullyPaid.TLabel', background='#d1ecf1', foreground='#0c5460', borderwidth=1, relief='solid')
        style.configure('Rejected.TLabel', background='#f8d7da', foreground='#721c24', borderwidth=1, relief='solid')


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

    def _create_header_and_back_button(self):
        """Creates the main title header and the back button."""
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Back Button - Placed on the left
        ttk.Button(header_frame, text="← Back to Loans Dashboard", 
                   command=self.switch_to_dashboard_callback).pack(side=tk.LEFT, padx=(0, 20))
        
        # Title - Placed on the right
        customer_name = self.loan_data.get('customer_name', 'N/A')
        ttk.Label(header_frame, text=f"Loan File: {customer_name}", 
                  style='Header.TLabel').pack(side=tk.LEFT)
        
        # Separator line
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=(0, 15))


    def _create_summary_panel(self):
        """Creates a panel to highlight the financial summary."""
        summary_frame = ttk.Frame(self.frame, padding="15", relief='groove', borderwidth=1)
        summary_frame.pack(fill='x', pady=10)
        
        # Status Label Logic
        current_status = self.loan_data.get('status', 'Unknown')
        status_tag = current_status.replace(" ", "").replace("/", "").lower()
        
        # Summary Grid
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(2, weight=1)

        # 1. Amount Borrowed
        ttk.Label(summary_frame, text="Borrowed Amount", font=('Arial', 10), foreground='#777').grid(row=0, column=0, sticky='w')
        ttk.Label(summary_frame, text=f"RWF {self.loan_amount:,.2f}", font=('Arial', 16, 'bold')).grid(row=1, column=0, sticky='w', pady=(0, 10))

        # 2. Total Paid
        ttk.Label(summary_frame, text="Total Paid", font=('Arial', 10), foreground='#777').grid(row=0, column=1, sticky='w')
        ttk.Label(summary_frame, text=f"RWF {self.total_paid:,.2f}", font=('Arial', 16, 'bold'), foreground='#2ecc71').grid(row=1, column=1, sticky='w', pady=(0, 10))

        # 3. Remaining Balance
        ttk.Label(summary_frame, text="Remaining Balance", font=('Arial', 10), foreground='#777').grid(row=0, column=2, sticky='w')
        ttk.Label(summary_frame, text=f"RWF {self.remaining_balance:,.2f}", font=('Arial', 16, 'bold'), foreground='#e74c3c').grid(row=1, column=2, sticky='w', pady=(0, 10))
        
        # Status Row
        ttk.Label(summary_frame, text="Current Status:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(5, 0))
        ttk.Label(summary_frame, text=current_status, style=f'{status_tag.capitalize()}.TLabel', 
                  font=('Arial', 10, 'bold'), padding='5 2').grid(row=2, column=1, columnspan=2, sticky='w', pady=(5, 0))


    def _create_notebook(self):
        """Creates a tabbed interface for Loan Info and Payment History."""
        
        # Create the notebook (tab container)
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill='both', expand=True, pady=10)

        # --- Tab 1: Loan Information ---
        loan_info_tab = ttk.Frame(notebook, padding="15")
        notebook.add(loan_info_tab, text="📄 Loan Details")
        self._populate_loan_info_tab(loan_info_tab)

        # --- Tab 2: Payment History ---
        payment_history_tab = ttk.Frame(notebook, padding="15")
        notebook.add(payment_history_tab, text="💳 Payment History")
        self._populate_payment_history_tab(payment_history_tab)


    def _populate_loan_info_tab(self, parent_frame):
        """Populates the Loan Information tab."""
        # Use Grid layout for cleaner key/value alignment
        parent_frame.columnconfigure(1, weight=1) # Make value column expand
        
        # Helper function to add a row of key/value pairs
        def add_info_row(key, value, row):
            ttk.Label(parent_frame, text=f"{key}:", style='InfoKey.TLabel').grid(row=row, column=0, sticky='w', padx=10, pady=5)
            ttk.Label(parent_frame, text=value, style='InfoValue.TLabel').grid(row=row, column=1, sticky='w', padx=10, pady=5)
            
        # Format key data points
        loan_id_str = str(self.loan_data.get('_id', 'N/A'))
        interest_str = f"{self.loan_data.get('interest_rate', 0.0)}%"
        
        app_date = self.loan_data.get('application_date', None)
        app_date_str = app_date.strftime('%Y-%m-%d') if isinstance(app_date, datetime) else 'N/A'
        
        # Display the information
        add_info_row("Full Loan ID", loan_id_str, 0)
        add_info_row("Loan Type", self.loan_data.get('loan_type', 'N/A'), 1)
        add_info_row("Interest Rate", interest_str, 2)
        add_info_row("Duration", self.loan_data.get('duration', 'N/A'), 3)
        add_info_row("Application Date", app_date_str, 4)
        add_info_row("Approved By", self.loan_data.get('approved_by', 'N/A'), 5)
        add_info_row("Next Payment Date", self.loan_data.get('next_payment', 'N/A'), 6)
        
        ttk.Label(parent_frame, text="Note: For edit functionality, please add separate buttons and database update logic.", 
                  font=('Arial', 9, 'italic'), foreground='#7f8c8d').grid(row=10, column=0, columnspan=2, sticky='w', pady=(20, 0))


    def _populate_payment_history_tab(self, parent_frame):
        """Populates the Payment History tab with a Treeview."""
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)

        # Define the Treeview (table)
        self.payment_tree = ttk.Treeview(parent_frame, columns=('Date', 'Amount', 'Recorded'), show='headings')
        self.payment_tree.heading('Date', text='Payment Date')
        self.payment_tree.heading('Amount', text='Amount Paid (RWF)', anchor='e')
        self.payment_tree.heading('Recorded', text='Record Date/Time')
        
        # Column widths 
        self.payment_tree.column('Date', anchor='center', width=120, stretch=tk.YES)
        self.payment_tree.column('Amount', anchor='e', width=150, stretch=tk.YES)
        self.payment_tree.column('Recorded', anchor='center', width=150, stretch=tk.YES)

        # Insert data into the table
        if self.payment_history:
            for payment in self.payment_history:
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
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=self.payment_tree.yview)
        self.payment_tree.configure(yscrollcommand=vsb.set)

        vsb.grid(row=0, column=1, sticky='ns')
        self.payment_tree.grid(row=0, column=0, sticky='nsew')