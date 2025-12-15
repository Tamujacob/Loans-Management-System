import tkinter as tk
from tkinter import ttk, messagebox
import database # Import your MongoDB connection file
import subprocess
import sys
import os

# --- MAIN APPLICATION CLASS (Manages Screen Switching) ---

class LoanApp(tk.Tk):
    """Main application window managing different screens/frames."""
    def __init__(self):
        super().__init__()
        self.title("Unified Loan Management System")
        self.geometry("800x550")
        self.config(bg="#ecf0f1")
        
        # --- Database Check ---
        # Ensure the database connection is available before proceeding
        if not hasattr(database, 'db') or database.db is None:
            messagebox.showerror("Initialization Error", 
                                 "Database connection failed. Please check 'database.py'. Exiting.")
            self.destroy()
            sys.exit()
        
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
        try:
            loan_app_file = "loan application.py" 
            
            if not os.path.exists(loan_app_file):
                variations = ["loan_application.py", "loanapplication.py", "LoanApplication.py"]
                found_file = next((v for v in variations if os.path.exists(v)), None)

                if not found_file:
                    messagebox.showerror("File Not Found", 
                        f"Could not find '{loan_app_file}' or common variations.")
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
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. SIDEBAR FRAME (Search and Filters) ---
        sidebar = tk.Frame(self, bg="#34495e", width=200, padx=10, pady=10)
        sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew") 

        tk.Label(sidebar, text="Loan Filter & Search", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=(10, 15))

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

        tk.Button(action_frame, text="View/Edit Details", font=("Arial", 10), bg="#3498db", fg="white", padx=5, 
                  command=self.view_loan_details).pack(side=tk.LEFT, padx=5)

        tk.Button(action_frame, text="Approve Loan", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", padx=5, command=self.approve_loan).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Reject Loan", font=("Arial", 10), bg="#e74c3c", fg="white", padx=5, command=self.reject_loan).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Record Repayment", font=("Arial", 10),
                  bg="#9b59b6", fg="white", padx=5, command=self.record_repayment).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Export Data", font=("Arial", 10), bg="#95a5a6", fg="white", padx=5).pack(side=tk.RIGHT, padx=5)

    # --- Helper Functions ---
    def _get_selected_loan_full_id(self):
        """
        Retrieves the full loan ID which is stored invisibly as the Treeview item's iid.
        This is the most reliable way to pass the ID to other components.
        """
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Selection Error", "Please select a loan first.")
            return None
        
        # The iid contains the full ID string
        return selected_item_iid 

    def _get_loan_data_from_db(self, loan_id):
        """Retrieves the full loan document using the database helper function."""
        try:
            # Assumes database.get_loan_by_id(loan_id) is implemented in database.py
            return database.get_loan_by_id(loan_id)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch loan details for ID {loan_id[-4:]}: {e}")
            return None
    

    # === METHOD TO VIEW LOAN DETAILS (Uses full ID directly from Treeview iid) ===
    def view_loan_details(self):
        """
        Retrieves the full ID of the selected loan and launches the 
        view_loan_details.py script, passing the ID as an argument.
        """
        full_loan_id = self._get_selected_loan_full_id()
        
        if full_loan_id:
            try:
                view_file = "view_loan_details.py" 
                
                if not os.path.exists(view_file):
                    messagebox.showerror("File Not Found", 
                        f"The file '{view_file}' required to view details was not found.")
                    return

                # Launch the external script, passing the full loan ID
                subprocess.Popen([sys.executable, view_file, full_loan_id])
                
            except Exception as e:
                messagebox.showerror("Execution Error", f"Failed to open loan details window: {str(e)}")
    # ==============================================================================


    # --- Dashboard Data & Action Functions ---

    def fetch_loans(self, status_filter=None):
        """Fetches loan data from MongoDB, applying an optional status filter."""
        try:
            query = {}
            if status_filter:
                if status_filter == "Active":
                    query["status"] = {"$in": ["Under Payment", "Approved"]}
                elif status_filter == "Closed":
                    query["status"] = "Fully Paid"
                else:
                    query["status"] = status_filter
                    
            # Direct query to the MongoDB collection
            loans = database.db['loans'].find(query)
            return list(loans)
        
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve loan data: {e}")
            return [] # Return empty list on failure

    def update_treeview(self, loan_list):
        """
        Clears and repopulates the Treeview, storing the full loan ID 
        in the internal 'iid' field.
        """
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for loan in loan_list:
            # Use the full ID as the internal identifier (iid)
            full_loan_id = str(loan.get('_id', 'N/A'))
            loan_id_display = full_loan_id[-4:] 

            data = (
                loan_id_display,
                loan.get('customer_name', 'N/A'),
                f"€{loan.get('loan_amount', 0.00):,.2f}", 
                loan.get('duration', 'N/A'),
                loan.get('status', 'Unknown'),
                loan.get('next_payment', 'N/A')
            )
            tag = loan.get('status', '').replace(" ", "").lower()
            
            # CRITICAL: Pass the full_loan_id as the item identifier (iid)
            self.tree.insert('', tk.END, iid=full_loan_id, values=data, tags=(tag,))


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
        """Fetches all loans and filters them locally based on search term."""
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
        loan_id = self._get_selected_loan_full_id()
        if not loan_id: return
        
        loan_data = self._get_loan_data_from_db(loan_id)
        if not loan_data: return

        selected_loan_name = loan_data.get('customer_name', 'N/A Customer')

        if loan_data.get('status') == 'Approved':
            messagebox.showinfo("Info", f"Loan for '{selected_loan_name}' is already Approved.")
            return

        try:
            # Assumes database.update_loan_status(loan_id, status) exists in database.py
            database.update_loan_status(loan_id, "Approved")
            messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been approved!")
            self.filter_loans(None) # Refresh
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to approve loan: {e}")

    def reject_loan(self):
        """Rejects a selected loan by updating its status in the database."""
        loan_id = self._get_selected_loan_full_id()
        if not loan_id: return
        
        loan_data = self._get_loan_data_from_db(loan_id)
        if not loan_data: return

        selected_loan_name = loan_data.get('customer_name', 'N/A Customer')

        if loan_data.get('status') == 'Rejected':
            messagebox.showinfo("Info", f"Loan for '{selected_loan_name}' is already Rejected.")
            return
        
        try:
            # Assumes database.update_loan_status(loan_id, status) exists in database.py
            database.update_loan_status(loan_id, "Rejected")
            messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been rejected!")
            self.filter_loans(None) # Refresh
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to reject loan: {e}")

    def record_repayment(self):
        """Opens repayment window for selected loan."""
        loan_id = self._get_selected_loan_full_id()
        if not loan_id: return
        
        loan_data = self._get_loan_data_from_db(loan_id)
        if not loan_data: return

        if loan_data.get('status') in ['Rejected', 'Fully Paid']:
             messagebox.showwarning("Repayment Not Allowed", f"Loan status is '{loan_data.get('status')}'. Repayments are not allowed.")
             return

        try:
            # Import and open repayment window (repayment.py must be available)
            try:
                from repayment import RepaymentWindow
                
                # Pass self.filter_loans as the callback to refresh the dashboard after payment
                repayment_win = RepaymentWindow(self, loan_data, self.filter_loans)
                
            except ImportError as e:
                messagebox.showerror("Import Error",
                    f"Cannot import repayment module: {str(e)}\n"
                    f"Make sure 'repayment.py' exists in the same directory.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open repayment: {str(e)}")


if __name__ == "__main__":
    # Ensure database.py connection is initialized before running the app
    # If database.py doesn't automatically connect on import, 
    # you might need to add a line here like: database.initialize_connection() 
    # based on how your database.py is structured.
    
    app = LoanApp()
    app.mainloop()