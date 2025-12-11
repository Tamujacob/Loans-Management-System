import tkinter as tk
from tkinter import ttk, messagebox
# NOTE: database.py is not included, assuming it handles MongoDB connection
import database # Import your MongoDB connection file
import datetime
import uuid
import subprocess
import sys
import os

# --- MOCK DATA (Fallback for database failure - Loans list) ---
# NOTE: Using a list of dictionaries with full IDs is essential for lookup
MOCK_LOAN_DATA = [
    {"_id": "65b4c1a5f0e1d2c3b4a59876", "customer_name": "Alice Smith", "loan_amount": 5000.00, "duration": "2 years", "status": "Approved", "next_payment": "2025-12-15"},
    {"_id": "65b4c1a6f0e1d2c3b4a59877", "customer_name": "Bob Johnson", "loan_amount": 12000.00, "duration": "5 years", "status": "Under Payment", "next_payment": "2025-12-20"},
    {"_id": "65b4c1a7f0e1d2c3b4a59878", "customer_name": "Charlie Brown", "loan_amount": 1500.00, "duration": "6 months", "status": "Fully Paid", "next_payment": "N/A"},
    {"_id": "65b4c1a8f0e1d2c3b4a59879", "customer_name": "David Wilson", "loan_amount": 8000.00, "duration": "3 years", "status": "Rejected", "next_payment": "N/A"},
    {"_id": "65b4c1a9f0e1d2c3b4a5987a", "customer_name": "Eve Miller", "loan_amount": 3000.00, "duration": "1 year", "status": "Pending", "next_payment": "To be set upon app"},
]

# --- MAIN APPLICATION CLASS (Manages Screen Switching) ---

class LoanApp(tk.Tk):
    """Main application window managing different screens/frames."""
    def __init__(self):
        super().__init__()
        self.title("Unified Loan Management System")
        self.geometry("800x550")
        self.config(bg="#ecf0f1")
        
        # Create a container frame where all other frames will be stacked
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # Initialize and stack the frames (screens)
        for F in (DashboardFrame,):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start with the Dashboard
        self.show_frame("DashboardFrame")

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()
        # If navigating to the dashboard, refresh the loan data
        if page_name == "DashboardFrame":
            frame.filter_loans(None)

    def open_loan_application(self):
        """Opens the external loan application.py file."""
        # This implementation remains the same
        try:
            loan_app_file = "loan application.py" # Assuming the name for external file
            
            if not os.path.exists(loan_app_file):
                # Search for common variations
                variations = ["loan_application.py", "loanapplication.py", "LoanApplication.py"]
                found_file = next((v for v in variations if os.path.exists(v)), None)

                if not found_file:
                    messagebox.showerror("File Not Found", 
                        f"Could not find '{loan_app_file}' or common variations.\n"
                        f"Ensure it's in the current directory: {os.getcwd()}")
                    return
                loan_app_file = found_file
            
            subprocess.Popen([sys.executable, loan_app_file])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open loan application: {str(e)}")


# --- SCREEN 1: LOAN MANAGEMENT DASHBOARD ---
class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="#ecf0f1")
        
        # Make the dashboard content resizable
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. SIDEBAR FRAME (Search and Filters) ---
        sidebar = tk.Frame(self, bg="#34495e", width=200, padx=10, pady=10)
        sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew") # Changed rowspan to 3

        tk.Label(sidebar, text="Loan Filter & Search", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=(10, 15))

        # Button to switch to Application Form
        tk.Button(sidebar, text="Open New Application", font=("Arial", 10, "bold"),
                 bg="#2ecc71", fg="white", width=18,
                 command=controller.open_loan_application).pack(pady=(5, 10))

        # Search Section
        tk.Label(sidebar, text="SEARCH LOANS", font=("Arial", 10), bg="#34495e", fg="#bdc3c7").pack(pady=(10, 5))
        self.search_entry = tk.Entry(sidebar, font=("Arial", 10), width=20)
        self.search_entry.pack(pady=5)
        tk.Button(sidebar, text="Search", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", width=18, command=self.search_loans).pack(pady=(0, 15))

        # Status Filter Buttons
        tk.Label(sidebar, text="FILTER BY STATUS", font=("Arial", 10), bg="#34495e", fg="#bdc3c7").pack(pady=(5, 5))

        tk.Button(sidebar, text="All Loans", font=("Arial", 10), bg="#ecf0f1", width=18, command=lambda: self.filter_loans(None)).pack(pady=3)
        tk.Button(sidebar, text="Pending/New", font=("Arial", 10), bg="#f1c40f", width=18, command=lambda: self.filter_loans("Pending")).pack(pady=3)
        tk.Button(sidebar, text="Under Payment", font=("Arial", 10), bg="#3498db", fg="white", width=18, command=lambda: self.filter_loans("Active")).pack(pady=3)
        tk.Button(sidebar, text="Fully Paid", font=("Arial", 10), bg="#2ecc71", fg="white", width=18, command=lambda: self.filter_loans("Closed")).pack(pady=3)
        tk.Button(sidebar, text="Rejected Loans", font=("Arial", 10), bg="#e74c3c", fg="white", width=18, command=lambda: self.filter_loans("Rejected")).pack(pady=3)


        # --- 2. MAIN HEADER & STATUS (Top Row) ---
        header_frame = tk.Frame(self, bg="white", padx=10, pady=5)
        header_frame.grid(row=0, column=1, sticky="ew")

        tk.Label(header_frame, text="Current Loan Applications", font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT)
        self.current_status_label = tk.Label(header_frame, text="Status: All Loans", font=("Arial", 12), bg="white", fg="#2c3e50")
        self.current_status_label.pack(side=tk.RIGHT)


        # --- 3. TREEVIEW (Main Data Table) ---
        main_content_frame = tk.Frame(self, bg="#ecf0f1")
        main_content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(0, weight=1)

        columns = ('#id', 'customer_name', 'loan_amount', 'duration', 'status', 'next_payment')
        self.tree = ttk.Treeview(main_content_frame, columns=columns, show='headings')

        self.tree.heading('#id', text='ID')
        self.tree.heading('customer_name', text='Customer Name')
        self.tree.heading('loan_amount', text='Amount')
        self.tree.heading('duration', text='Term')
        self.tree.heading('status', text='Status')
        self.tree.heading('next_payment', text='Next Payment')

        # Reduced column widths to fit the smaller window size
        self.tree.column('#id', width=40, anchor='center')
        self.tree.column('customer_name', width=120)
        self.tree.column('loan_amount', width=80, anchor='e')
        self.tree.column('duration', width=60, anchor='center')
        self.tree.column('status', width=80, anchor='center')
        self.tree.column('next_payment', width=100, anchor='center')

        # Treeview Styling for Status Coloring 
        self.tree.tag_configure('pending', background='#fcf8e3', foreground='#8a6d3b')
        self.tree.tag_configure('underpayment', background='#d9edf7', foreground='#31708f')
        self.tree.tag_configure('fullypaid', background='#dff0d8', foreground='#3c763d')
        self.tree.tag_configure('approved', background='#fae8ff', foreground='#9c27b0')
        self.tree.tag_configure('rejected', background='#fdecea', foreground='#d32f2f')

        # Add Scrollbar
        scrollbar = ttk.Scrollbar(main_content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- 4. ACTION BUTTONS (Bottom Row) ---
        action_frame = tk.Frame(self, bg="#ecf0f1", padx=10, pady=5)
        action_frame.grid(row=2, column=1, sticky="ew")

        tk.Button(action_frame, text="View/Edit Details", font=("Arial", 10), bg="#3498db", fg="white", padx=5).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Approve Loan", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", padx=5, command=self.approve_loan).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Reject Loan", font=("Arial", 10), bg="#e74c3c", fg="white", padx=5, command=self.reject_loan).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Record Repayment", font=("Arial", 10),
                 bg="#9b59b6", fg="white", padx=5, command=self.record_repayment).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Export Data", font=("Arial", 10), bg="#95a5a6", fg="white", padx=5).pack(side=tk.RIGHT, padx=5)

    # --- Helper Functions ---
    def _get_selected_loan_full_data(self):
        """Retrieves the full loan data based on the selected item's ID in the Treeview."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a loan first.")
            return None, None
        
        # The display ID is the last 4 characters of the full ID
        display_id = self.tree.item(selected_item, 'values')[0]
        
        # Search the database or mock data for the loan that ends with this ID
        for loan in self.fetch_loans(None):
            if str(loan.get('_id', ''))[-4:] == display_id:
                return str(loan['_id']), loan
        
        messagebox.showerror("Error", "Could not find full loan details in database.")
        return None, None


    # --- Dashboard Data & Action Functions ---

    def fetch_loans(self, status_filter=None):
        """Fetches loan data from MongoDB, applying an optional status filter."""
        if database.db is None:
            return MOCK_LOAN_DATA

        try:
            query = {}
            if status_filter:
                if status_filter == "Active":
                    query["status"] = {"$in": ["Under Payment", "Approved"]}
                elif status_filter == "Closed":
                    query["status"] = "Fully Paid"
                elif status_filter == "Pending":
                    query["status"] = "Pending"
                elif status_filter == "Rejected":
                    query["status"] = "Rejected"
                
            # Use database mock or actual database call
            loans = database.db['loans'].find(query)
            return list(loans)
        
        except Exception as e:
            print(f"Database error during fetch: {e}")
            messagebox.showerror("Database Error", "Failed to connect to the database. Displaying mock data.")
            return MOCK_LOAN_DATA

    def update_treeview(self, loan_list):
        """Clears and repopulates the Treeview with loan data."""
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for loan in loan_list:
            # Use the last 4 characters of the full ID for display
            loan_id_display = str(loan.get('_id', 'N/A'))[-4:]

            data = (
                loan_id_display,
                loan.get('customer_name', 'N/A'),
                f"€{loan.get('loan_amount', 0.00):,.2f}", # Changed $ to € for generic example
                loan.get('duration', 'N/A'),
                loan.get('status', 'Unknown'),
                loan.get('next_payment', 'N/A')
            )
            tag = loan.get('status', '').replace(" ", "").lower()
            self.tree.insert('', tk.END, values=data, tags=(tag,))

    def filter_loans(self, status=None):
        """Filters data based on status and updates the Treeview."""
        loans = self.fetch_loans(status)
        self.update_treeview(loans)
        
        status_text = "All Loans"
        if status == "Active":
            status_text = "Under Payment/Approved"
        elif status == "Closed":
            status_text = "Fully Paid"
        elif status == "Pending":
            status_text = "Pending Applications"
        elif status == "Rejected":
            status_text = "Rejected Loans"
            
        self.current_status_label.config(text=f"Status: {status_text}")

    def search_loans(self):
        """Searches current Treeview data by name or status."""
        search_term = self.search_entry.get().lower()
        all_loans = self.fetch_loans(None)
        
        filtered_loans = [
            loan for loan in all_loans
            if search_term in loan.get("customer_name", "").lower() or search_term in loan.get("status", "").lower()
        ]
        self.update_treeview(filtered_loans)
        self.current_status_label.config(text=f"Search Results for: '{search_term}'")

    def approve_loan(self):
        """Approves a selected loan by updating its status in the database."""
        loan_id, loan_data = self._get_selected_loan_full_data()
        if not loan_id:
            return

        selected_loan_name = loan_data['customer_name']

        if loan_data.get('status') == 'Approved':
            messagebox.showinfo("Info", f"Loan for '{selected_loan_name}' is already Approved.")
            return

        try:
            # Assumes database.update_loan_status(loan_id, status) exists in database.py
            database.update_loan_status(loan_id, "Approved")
            messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been approved!")
            self.filter_loans(None) # Refresh
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update loan status: {e}")

    def reject_loan(self):
        """Rejects a selected loan by updating its status in the database."""
        loan_id, loan_data = self._get_selected_loan_full_data()
        if not loan_id:
            return

        selected_loan_name = loan_data['customer_name']

        if loan_data.get('status') == 'Rejected':
            messagebox.showinfo("Info", f"Loan for '{selected_loan_name}' is already Rejected.")
            return
        
        try:
            # Assumes database.update_loan_status(loan_id, status) exists in database.py
            database.update_loan_status(loan_id, "Rejected")
            messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been rejected!")
            self.filter_loans(None) # Refresh
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update loan status: {e}")

    def record_repayment(self):
        """
        Opens repayment window for selected loan.
        FIXED: Passes the required 'go_back_callback' argument.
        """
        loan_id, loan_data = self._get_selected_loan_full_data()
        if not loan_id:
            return
        
        if loan_data.get('status') in ['Rejected', 'Fully Paid']:
             messagebox.showwarning("Repayment Not Allowed", f"Loan status is '{loan_data.get('status')}'. Repayments are not allowed.")
             return

        try:
            # Check for database connection for actual data fetch
            if database.db is None:
                messagebox.showinfo("Info", "Repayment feature requires database connection. Cannot open window with mock data.")
                return

            # Import and open repayment window
            try:
                from repayment import RepaymentWindow
                
                # *** FIX APPLIED HERE: Pass self.filter_loans as the callback ***
                # This function (self.filter_loans) will be called when the user clicks 'Back' 
                # or records a payment in the RepaymentWindow.
                repayment_win = RepaymentWindow(self, loan_data, self.filter_loans)
                
            except ImportError as e:
                messagebox.showerror("Import Error",
                    f"Cannot import repayment module: {str(e)}\n"
                    f"Make sure 'repayment.py' exists in the same directory.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open repayment: {str(e)}")


if __name__ == "__main__":
    # Mock the database object if not running in the environment
    
    # --- Mock database functions (MUST match the calls used in the app) ---
    def mock_find_one(collection, query):
        if collection == 'loans':
            for loan in MOCK_LOAN_DATA:
                if str(loan.get('_id')) == query.get('_id'):
                    return loan
                if loan.get('customer_name') == query.get('customer_name'): # Fallback for name-based lookup
                    return loan
        return None

    def mock_update_status(loan_id, new_status):
        """Finds loan by full ID and updates status in MOCK_LOAN_DATA list."""
        for loan in MOCK_LOAN_DATA:
            if str(loan.get('_id')) == str(loan_id):
                loan['status'] = new_status
                # Also mock next_payment change
                if new_status == 'Approved':
                    loan['next_payment'] = 'To be set upon repayment'
                elif new_status == 'Rejected' or new_status == 'Fully Paid':
                     loan['next_payment'] = 'N/A'
                print(f"Mock DB: Updated loan {loan_id[-4:]} to status '{new_status}'")
                return type('MockResult', (object,), {'modified_count': 1})()
        return type('MockResult', (object,), {'modified_count': 0})()
        
    class MockCollection:
        def __init__(self, name):
            self.name = name

        def find(self, query=None):
            # Apply filtering logic to MOCK_LOAN_DATA
            if query and 'status' in query:
                status_val = query['status']
                if isinstance(status_val, dict) and '$in' in status_val:
                    # Handle {"$in": ["Under Payment", "Approved"]}
                    return [loan for loan in MOCK_LOAN_DATA if loan['status'] in status_val['$in']]
                else:
                    # Handle single status filter
                    return [loan for loan in MOCK_LOAN_DATA if loan['status'] == status_val]
            return MOCK_LOAN_DATA

        def find_one(self, query):
            # Mock find_one logic
            return mock_find_one(self.name, query)
            
        def update_one(self, filter_query, update_data):
            # update_one is now handled via the helper function in the app logic
            # For direct access, we return a mock update result
            return type('MockResult', (object,), {'modified_count': 1})() 
            
        def sort(self, *args):
            return self

    class MockDatabase:
        def __getitem__(self, key):
            return MockCollection(key)
        
        # Add the helper functions the app expects
        def get_loan_by_id(self, loan_id):
            return mock_find_one('loans', {'_id': loan_id})
        
        def update_loan_status(self, loan_id, new_status):
            return mock_update_status(loan_id, new_status)


    # Initialize the database mock instance
    if 'db' not in dir(database) or database.db is None:
         database.db = MockDatabase()


    app = LoanApp()
    app.mainloop()