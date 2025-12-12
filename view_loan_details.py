import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Assume database.py is available for connection/mocking
try:
    import database 
except ImportError:
    messagebox.showerror("Error", "Could not import database.py. Make sure it is in the same directory.")
    sys.exit(1)

# --- MOCK DATA (Must match the data in loan_management.py for consistency) ---
MOCK_LOAN_DATA = [
    {"_id": "65b4c1a5f0e1d2c3b4a59876", "customer_name": "Alice Smith", "loan_amount": 5000.00, "duration": "2 years", "status": "Approved", "next_payment": "2025-12-15",
     "loan_type": "Personal", "interest_rate": 8.5, "approved_by": "Manager A", "notes": "Good credit score."},
    {"_id": "65b4c1a6f0e1d2c3b4a59877", "customer_name": "Bob Johnson", "loan_amount": 12000.00, "duration": "5 years", "status": "Under Payment", "next_payment": "2025-12-20",
     "loan_type": "Mortgage", "interest_rate": 4.2, "approved_by": "Manager B", "notes": "Collateral attached."},
    {"_id": "65b4c1a7f0e1d2c3b4a59878", "customer_name": "Charlie Brown", "loan_amount": 1500.00, "duration": "6 months", "status": "Fully Paid", "next_payment": "N/A",
     "loan_type": "Short Term", "interest_rate": 10.0, "approved_by": "Manager C", "notes": "No issues."},
    {"_id": "65b4c1a8f0e1d2c3b4a59879", "customer_name": "David Wilson", "loan_amount": 8000.00, "duration": "3 years", "status": "Rejected", "next_payment": "N/A",
     "loan_type": "Business", "interest_rate": 7.0, "approved_by": "Manager D", "notes": "Failed background check."},
    {"_id": "65b4c1a9f0e1d2c3b4a5987a", "customer_name": "Eve Miller", "loan_amount": 3000.00, "duration": "1 year", "status": "Pending", "next_payment": "To be set upon app",
     "loan_type": "Personal", "interest_rate": 9.0, "approved_by": "Pending", "notes": "New application, awaiting review."},
]

class LoanDetailsViewer(tk.Tk):
    def __init__(self, loan_id):
        super().__init__()
        self.loan_id = loan_id
        self.loan_data = self._fetch_loan_data(loan_id)
        
        if self.loan_data is None:
            # If data retrieval failed, show error and exit
            self.title("Error")
            messagebox.showerror("Error", f"Loan details not found for ID: {self.loan_id}")
            self.destroy()
            return

        self.title(f"Loan Details: {self.loan_data.get('customer_name', 'N/A')} ({str(loan_id)[-4:]})")
        self.geometry("450x350")
        self.config(bg="#ecf0f1")
        
        self._create_widgets()

    def _fetch_loan_data(self, loan_id):
        """Fetches a single loan record by its full ID."""
        if database.db is None:
            # Mock data lookup
            for loan in MOCK_LOAN_DATA:
                if str(loan.get('_id')) == str(loan_id):
                    return loan
            return None

        try:
            # Use the mock_find_one logic provided in loan_management.py's __main__ block
            # If database.db is a MockDatabase instance, this will use mock_find_one
            loan = database.db['loans'].find_one({'_id': loan_id})
            # NOTE: If using PyMongo, you need to ensure the ID is converted to ObjectId first.
            # We rely on the database.py layer to handle ObjectId conversion.
            if not loan:
                # If the database returns None, try the mock data as a fallback
                for loan in MOCK_LOAN_DATA:
                    if str(loan.get('_id')) == str(loan_id):
                        return loan
            return loan

        except Exception as e:
            print(f"Database error during single loan fetch: {e}")
            messagebox.showwarning("Database Warning", "Failed to connect to the database. Trying mock data.")
            # Fallback to mock data if DB fails
            for loan in MOCK_LOAN_DATA:
                if str(loan.get('_id')) == str(loan_id):
                    return loan
            return None


    def _create_widgets(self):
        """Builds the details frame."""
        main_frame = tk.Frame(self, bg="white", padx=15, pady=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Loan Overview", font=("Arial", 16, "bold"), bg="white", fg="#34495e").grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")
        
        data_fields = {
            "Full ID": str(self.loan_data.get('_id', 'N/A')),
            "Customer Name": self.loan_data.get('customer_name', 'N/A'),
            "Amount": f"€{self.loan_data.get('loan_amount', 0.00):,.2f}",
            "Term (Duration)": self.loan_data.get('duration', 'N/A'),
            "Loan Type": self.loan_data.get('loan_type', 'N/A'),
            "Interest Rate": f"{self.loan_data.get('interest_rate', 'N/A')}%",
            "Current Status": self.loan_data.get('status', 'Unknown'),
            "Next Payment Date": self.loan_data.get('next_payment', 'N/A'),
            "Approved By": self.loan_data.get('approved_by', 'N/A'),
        }

        row_num = 1
        for label_text, value in data_fields.items():
            # Label for field name
            tk.Label(main_frame, text=f"{label_text}:", font=("Arial", 10, "bold"), bg="white", fg="#2c3e50", anchor="w").grid(row=row_num, column=0, sticky="w", padx=5, pady=2)
            # Label for field value
            tk.Label(main_frame, text=value, font=("Arial", 10), bg="white", fg="#7f8c8d", anchor="w").grid(row=row_num, column=1, sticky="w", padx=5, pady=2)
            row_num += 1
            
        # Notes/Additional Info (takes up full width)
        tk.Label(main_frame, text="Notes:", font=("Arial", 10, "bold"), bg="white", fg="#2c3e50", anchor="w").grid(row=row_num, column=0, sticky="w", padx=5, pady=(10, 2))
        notes_text = self.loan_data.get('notes', 'No additional notes provided.')
        tk.Label(main_frame, text=notes_text, font=("Arial", 10, "italic"), bg="white", fg="#7f8c8d", wraplength=400, justify=tk.LEFT, anchor="w").grid(row=row_num + 1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Configure columns to resize
        main_frame.grid_columnconfigure(1, weight=1)

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # --- Mock database setup for independent run ---
    # This must match the mock logic in loan_management.py for standalone testing
    
    def mock_find_one(collection, query):
        if collection == 'loans':
            if '_id' in query:
                for loan in MOCK_LOAN_DATA:
                    # Using str() for ID comparison
                    if str(loan.get('_id')) == str(query.get('_id')): 
                        return loan
        return None
        
    class MockCollection:
        def __init__(self, name):
            self.name = name

        def find(self, query=None):
            return MOCK_LOAN_DATA

        def find_one(self, query):
            return mock_find_one(self.name, query)
            
        def update_one(self, filter_query, update_data):
            # Not used in viewer, but included for completeness
            return type('MockResult', (object,), {'modified_count': 1})() 

    class MockDatabase:
        def __getitem__(self, key):
            return MockCollection(key)
        
        # Add the helper function the app expects
        def get_loan_by_id(self, loan_id):
            return mock_find_one('loans', {'_id': loan_id})

    # Initialize the database mock instance for standalone run
    # This is critical if database.py doesn't establish a real connection
    if 'db' not in dir(database) or database.db is None:
           database.db = MockDatabase()
    
    # Check for the loan ID passed as a command-line argument
    if len(sys.argv) > 1:
        loan_id_to_view = sys.argv[1]
        try:
            viewer_app = LoanDetailsViewer(loan_id_to_view)
            viewer_app.mainloop()
        except Exception as e:
            messagebox.showerror("Runtime Error", f"An error occurred while launching viewer: {e}")
            sys.exit(1)
    else:
        # If run independently without an ID (for testing)
        messagebox.showinfo("Info", "Running stand-alone. No loan ID provided. Use '65b4c1a5f0e1d2c3b4a59876' as example ID.")
        # Example to run stand-alone:
        try:
            viewer_app = LoanDetailsViewer("65b4c1a5f0e1d2c3b4a59876")
            viewer_app.mainloop()
        except Exception as e:
            messagebox.showerror("Runtime Error", f"An error occurred while launching viewer: {e}")
            sys.exit(1)