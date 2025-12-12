import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Assume database.py is available for connection/mocking
try:
    # database.py handles connecting to the real DB or setting up the Mock DB
    import database 
except ImportError:
    messagebox.showerror("Error", "Could not import database.py. Make sure it is in the same directory.")
    # Exit if the critical dependency is missing
    sys.exit(1)

class LoanDetailsViewer(tk.Tk):
    """
    A window to display and eventually edit the full details of a specific loan.
    Data is fetched entirely via the database.py module.
    """
    def __init__(self, loan_id):
        super().__init__()
        self.loan_id = loan_id
        
        # --- Data Fetching: Centralized in database.py ---
        # This call handles both real MongoDB fetch (with ObjectId conversion) 
        # and mock data lookup based on the internal state of database.py
        self.loan_data = database.get_loan_by_id(loan_id)
        
        if self.loan_data is None:
            # If data retrieval failed, show error and destroy the window instance
            self.title("Error")
            messagebox.showerror("Error", f"Loan details not found for ID: {self.loan_id}. Check database connection or ID.")
            self.destroy() 
            return

        # Use the last few characters of the ID for a cleaner title
        short_id = str(self.loan_data.get('_id', 'N/A'))[-8:]
        self.title(f"Loan Details: {self.loan_data.get('customer_name', 'N/A')} ({short_id})")
        self.geometry("450x350")
        self.config(bg="#ecf0f1")
        
        self._create_widgets()

    def _create_widgets(self):
        """Builds the details frame using fetched loan_data."""
        main_frame = tk.Frame(self, bg="white", padx=15, pady=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        tk.Label(main_frame, text="Loan Overview", font=("Arial", 16, "bold"), bg="white", fg="#34495e").grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")
        
        # Dictionary of fields to display
        # Note: We rely on loan_data having all these keys, which it should if 
        # the database or mock data is structured correctly.
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
            
        # Notes/Additional Info
        tk.Label(main_frame, text="Notes:", font=("Arial", 10, "bold"), bg="white", fg="#2c3e50", anchor="w").grid(row=row_num, column=0, sticky="w", padx=5, pady=(10, 2))
        notes_text = self.loan_data.get('notes', 'No additional notes provided.')
        tk.Label(main_frame, text=notes_text, font=("Arial", 10, "italic"), bg="white", fg="#7f8c8d", wraplength=400, justify=tk.LEFT, anchor="w").grid(row=row_num + 1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Configure columns to resize
        main_frame.grid_columnconfigure(1, weight=1)

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    
    # Check for the loan ID passed as a command-line argument from loan_management.py
    if len(sys.argv) > 1:
        loan_id_to_view = sys.argv[1]
    else:
        # If run independently, use a hardcoded ID from the mock data in database.py for testing
        loan_id_to_view = "65b4c1a5f0e1d2c3b4a59876" 
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