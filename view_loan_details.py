import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import datetime

# Assume database.py is available for connection/mocking
try:
    # database.py handles connecting to the real DB or setting up the Mock DB
    import database 
except ImportError:
    messagebox.showerror("Error", "Could not import database.py. Make sure it is in the same directory.")
    sys.exit(1)

class LoanDetailsViewer(tk.Tk):
    """
    A window to display comprehensive loan details (Overview and Payment History).
    Data is fetched entirely via the database.py module.
    """
    def __init__(self, loan_id):
        super().__init__()
        self.loan_id = loan_id
        
        # --- Data Fetching ---
        self.loan_data = database.get_loan_by_id(loan_id)
        # This function must internally call the 'payments' collection
        self.payment_history = database.get_payments_by_loan(loan_id) 
        
        if self.loan_data is None:
            self.title("Error")
            messagebox.showerror("Error", f"Loan details not found for ID: {self.loan_id}. Check database connection or ID.")
            self.destroy() 
            return

        # --- Window Setup ---
        short_id = str(self.loan_data.get('_id', 'N/A'))[-8:]
        self.title(f"Loan Details: {self.loan_data.get('customer_name', 'N/A')} ({short_id})")
        self.geometry("800x600") 
        self.config(bg="#ecf0f1")
        
        self._create_widgets()

    def _create_widgets(self):
        """Builds the main structure with a Notebook (tabs) for navigation."""
        
        # Configure a consistent style
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
        # 1. Main Notebook Container
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # 2. Loan Overview Tab
        overview_frame = tk.Frame(self.notebook, bg="white", padx=15, pady=15)
        self.notebook.add(overview_frame, text="Loan Overview")
        self._build_overview_tab(overview_frame)

        # 3. Payment History Tab
        # Note: We keep the variable name 'payment_history' for clarity in the GUI context,
        # but the data comes from the 'payments' collection via the database function.
        history_frame = tk.Frame(self.notebook, bg="white", padx=10, pady=10)
        self.notebook.add(history_frame, text=f"Payment History ({len(self.payment_history)})")
        self._build_history_tab(history_frame)
        
    def _build_overview_tab(self, parent_frame):
        """Builds the comprehensive loan detail display."""
        
        # Header
        tk.Label(parent_frame, text="Detailed Loan Information", font=("Arial", 18, "bold"), bg="white", fg="#1abc9c").grid(row=0, column=0, columnspan=4, pady=(0, 20), sticky="w")
        
        # Define fields and their organization
        data_fields = {
            "ID & Status": [
                ("Full ID", str(self.loan_data.get('_id', 'N/A'))),
                ("Current Status", self.loan_data.get('status', 'Unknown')),
                ("Customer Name", self.loan_data.get('customer_name', 'N/A')),
            ],
            "Financials": [
                ("Amount", f"€{self.loan_data.get('loan_amount', 0.00):,.2f}"),
                ("Interest Rate", f"{self.loan_data.get('interest_rate', 'N/A')}%"),
                ("Term (Duration)", self.loan_data.get('duration', 'N/A')),
            ],
            "Administration": [
                ("Loan Type", self.loan_data.get('loan_type', 'N/A')),
                ("Next Payment Date", self.loan_data.get('next_payment', 'N/A')),
                ("Approved By", self.loan_data.get('approved_by', 'N/A')),
            ]
        }
        
        # Use a higher-level frame for grouping
        details_frame = tk.Frame(parent_frame, bg='white')
        details_frame.grid(row=1, column=0, columnspan=4, sticky='nsew')
        parent_frame.grid_rowconfigure(1, weight=1)
        parent_frame.grid_columnconfigure(3, weight=1)
        
        col_count = 0
        for group_name, fields in data_fields.items():
            group_frame = tk.LabelFrame(details_frame, text=group_name, font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f5f5f5")
            group_frame.grid(row=0, column=col_count, padx=15, pady=5, sticky='nsw')
            
            for i, (label_text, value) in enumerate(fields):
                # Field Name Label (Column 0 of group_frame)
                tk.Label(group_frame, text=f"{label_text}:", font=("Arial", 10, "bold"), bg="#f5f5f5", fg="#2c3e50", anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=2)
                # Field Value Label (Column 1 of group_frame)
                tk.Label(group_frame, text=value, font=("Arial", 10), bg="#f5f5f5", fg="#7f8c8d", anchor="w").grid(row=i, column=1, sticky="w", padx=5, pady=2)
            
            col_count += 1
            
        # Notes/Additional Info section below the main groups
        notes_frame = tk.LabelFrame(parent_frame, text="Notes", font=("Arial", 12, "bold"), padx=10, pady=5, bg="#f5f5f5")
        notes_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        
        notes_text = self.loan_data.get('notes', 'No additional notes provided.')
        tk.Label(notes_frame, text=notes_text, font=("Arial", 10, "italic"), bg="#f5f5f5", fg="#7f8c8d", wraplength=750, justify=tk.LEFT, anchor="w").pack(fill='x', expand=True, padx=5, pady=5)


    def _build_history_tab(self, parent_frame):
        """Builds the payment history table using ttk.Treeview."""
        
        # 1. Define columns for the Treeview
        columns = ("#", "Date", "Amount", "Method", "Reference")
        self.tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=20)

        # 2. Set column headings and properties
        self.tree.heading("#", text="No.", anchor=tk.CENTER)
        self.tree.heading("Date", text="Payment Date", anchor=tk.W)
        self.tree.heading("Amount", text="Amount (€)", anchor=tk.E)
        self.tree.heading("Method", text="Method", anchor=tk.W)
        self.tree.heading("Reference", text="Reference/ID", anchor=tk.W)

        # 3. Set column widths
        self.tree.column("#", width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.tree.column("Date", width=150, stretch=tk.NO, anchor=tk.W)
        self.tree.column("Amount", width=100, stretch=tk.NO, anchor=tk.E)
        self.tree.column("Method", width=120, stretch=tk.NO, anchor=tk.W)
        self.tree.column("Reference", width=300, stretch=tk.YES, anchor=tk.W)
        
        # 4. Populate data
        if self.payment_history:
            for i, payment in enumerate(self.payment_history):
                # Format date object to a readable string
                payment_date_str = payment.get('payment_date')
                if isinstance(payment_date_str, datetime.datetime):
                    payment_date_str = payment_date_str.strftime('%Y-%m-%d %H:%M:%S')
                
                # Format amount
                amount_str = f"{payment.get('payment_amount', 0.00):,.2f}"
                
                self.tree.insert("", tk.END, values=(
                    i + 1,
                    payment_date_str,
                    amount_str,
                    payment.get('payment_method', 'N/A'),
                    str(payment.get('_id', 'N/A')) # Ensure ID is a string for display
                ))
        
        # 5. Add scrollbar
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 6. Grid placement
        self.tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 5), pady=5)
        
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)


# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    
    # Check for the loan ID passed as a command-line argument from loan_management.py
    if len(sys.argv) > 1:
        loan_id_to_view = sys.argv[1]
    else:
        # If run independently, use a hardcoded ID from the mock data in database.py for testing
        loan_id_to_view = "65b4c1a6f0e1d2c3b4a59877" 
        messagebox.showinfo("Info", f"Running stand-alone. No loan ID provided. Using example ID: {loan_id_to_view}")
    
    try:
        # Initialize and run the application with the fetched ID
        viewer_app = LoanDetailsViewer(loan_id_to_view)
        # Check if the viewer was successfully initialized (i.e., data was found)
        if viewer_app.loan_data is not None:
             viewer_app.mainloop()
    except Exception as e:
        # Catch unexpected errors during application launch
        messagebox.showerror("Runtime Error", f"An unexpected error occurred: {e}")
        sys.exit(1)