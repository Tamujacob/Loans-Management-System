from tkinter import *
from tkinter import ttk, messagebox
# NOTE: database.py is not included, assuming it handles MongoDB connection
import database # Import your MongoDB connection file
import datetime 
import uuid 
import subprocess
import sys
import os

# --- MOCK DATA (Fallback for database failure) ---
MOCK_LOAN_DATA = [
    {"_id": "65b4c1a5", "customer_name": "Alice Smith", "loan_amount": 5000.00, "duration": "2 years", "status": "Approved", "next_payment": "2025-12-15"},
    {"_id": "65b4c1a6", "customer_name": "Bob Johnson", "loan_amount": 12000.00, "duration": "5 years", "status": "Under Payment", "next_payment": "2025-12-20"},
    {"_id": "65b4c1a7", "customer_name": "Charlie Brown", "loan_amount": 1500.00, "duration": "6 months", "status": "Fully Paid", "next_payment": "N/A"},
    {"_id": "65b4c1a8", "customer_name": "David Wilson", "loan_amount": 8000.00, "duration": "3 years", "status": "Rejected", "next_payment": "N/A"},  # Added a rejected loan
]

# --- MAIN APPLICATION CLASS (Manages Screen Switching) ---

class LoanApp(Tk):
    """Main application window managing different screens/frames."""
    def __init__(self):
        super().__init__()
        self.title("Unified Loan Management System")
        # Reduced geometry from 1100x750 to 800x550 for a smaller window
        self.geometry("800x550") 
        self.config(bg="#ecf0f1")
        
        # Global variables for cross-frame data
        self.repayment_method_var = StringVar(value="Monthly")
        self.terms_var = IntVar()

        # Create a container frame where all other frames will be stacked
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # Initialize and stack the frames (screens) - ONLY DashboardFrame now
        # REMOVED: ApplicationFrame from the list of frames
        for F in (DashboardFrame,):  # Only DashboardFrame
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            # put all the pages in the same location; 
            # the one on top of the stacking order will be the one visible.
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
            # Try to find the loan application.py file in the current directory
            loan_app_file = "loan application.py"
            
            # Check if file exists
            if not os.path.exists(loan_app_file):
                # Try with different variations
                variations = [
                    "loan_application.py",
                    "loanapplication.py",
                    "LoanApplication.py",
                    "./loan application.py",
                    "../loan application.py"
                ]
                
                found = False
                for variation in variations:
                    if os.path.exists(variation):
                        loan_app_file = variation
                        found = True
                        break
                
                if not found:
                    messagebox.showerror("File Not Found", 
                        f"Could not find 'loan application.py' file.\n"
                        f"Please ensure it's in the same directory as this file.\n"
                        f"Current directory: {os.getcwd()}")
                    return
            
            # Open the loan application file
            subprocess.Popen([sys.executable, loan_app_file])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open loan application: {str(e)}")


# --- SCREEN 1: LOAN MANAGEMENT DASHBOARD ---
class DashboardFrame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="#ecf0f1")
        
        # Make the dashboard content resizable
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. SIDEBAR FRAME (Search and Filters) ---
        # Fixed width reduced to 200 to save space
        sidebar = Frame(self, bg="#34495e", width=200, padx=10, pady=10) 
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew") 

        Label(sidebar, text="Loan Filter & Search", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=(10, 15)) # Reduced font/padding

        # Button to switch to Application Form - NOW OPENS EXTERNAL FILE
        Button(sidebar, text="Open New Application", font=("Arial", 10, "bold"), 
               bg="#2ecc71", fg="white", width=18, 
               command=controller.open_loan_application).pack(pady=(5, 10)) # Reduced width/font

        # Search Section
        Label(sidebar, text="SEARCH LOANS", font=("Arial", 10), bg="#34495e", fg="#bdc3c7").pack(pady=(10, 5))
        self.search_entry = Entry(sidebar, font=("Arial", 10), width=20) # Reduced font/width
        self.search_entry.pack(pady=5)
        Button(sidebar, text="Search", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", width=18, command=self.search_loans).pack(pady=(0, 15)) # Reduced width/font

        # Status Filter Buttons
        Label(sidebar, text="FILTER BY STATUS", font=("Arial", 10), bg="#34495e", fg="#bdc3c7").pack(pady=(5, 5))

        Button(sidebar, text="All Loans", font=("Arial", 10), bg="#ecf0f1", width=18, command=lambda: self.filter_loans(None)).pack(pady=3)
        Button(sidebar, text="Pending/New", font=("Arial", 10), bg="#f1c40f", width=18, command=lambda: self.filter_loans("Pending")).pack(pady=3)
        Button(sidebar, text="Under Payment", font=("Arial", 10), bg="#3498db", fg="white", width=18, command=lambda: self.filter_loans("Active")).pack(pady=3)
        Button(sidebar, text="Fully Paid", font=("Arial", 10), bg="#2ecc71", fg="white", width=18, command=lambda: self.filter_loans("Closed")).pack(pady=3)
        # ADDED: Rejected Loans button
        Button(sidebar, text="Rejected Loans", font=("Arial", 10), bg="#e74c3c", fg="white", width=18, command=lambda: self.filter_loans("Rejected")).pack(pady=3)


        # --- 2. MAIN HEADER & STATUS (Top Row) ---
        header_frame = Frame(self, bg="white", padx=10, pady=5)
        header_frame.grid(row=0, column=1, sticky="ew")

        Label(header_frame, text="Current Loan Applications", font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(side=LEFT) # Reduced font
        self.current_status_label = Label(header_frame, text="Status: All Loans", font=("Arial", 12), bg="white", fg="#2c3e50") # Reduced font
        self.current_status_label.pack(side=RIGHT)


        # --- 3. TREEVIEW (Main Data Table) ---
        main_content_frame = Frame(self, bg="#ecf0f1")
        main_content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        # Treeview Columns
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
        self.tree.tag_configure('pending', background='#fcf8e3', foreground='#8a6d3b') # Light Yellow
        self.tree.tag_configure('underpayment', background='#d9edf7', foreground='#31708f') # Light Blue
        self.tree.tag_configure('fullypaid', background='#dff0d8', foreground='#3c763d') # Light Green
        self.tree.tag_configure('approved', background='#fae8ff', foreground='#9c27b0') # Light Purple
        # ADDED: Style for rejected loans
        self.tree.tag_configure('rejected', background='#fdecea', foreground='#d32f2f') # Light Red

        # Add Scrollbar
        scrollbar = ttk.Scrollbar(main_content_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)


        # --- 4. ACTION BUTTONS (Bottom Row) ---
        action_frame = Frame(self, bg="#ecf0f1", padx=10, pady=5)
        action_frame.grid(row=2, column=1, sticky="ew")

        # Reduced font/padding
        Button(action_frame, text="View/Edit Details", font=("Arial", 10), bg="#3498db", fg="white", padx=5).pack(side=LEFT, padx=5)
        Button(action_frame, text="Approve Loan", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", padx=5, command=self.approve_loan).pack(side=LEFT, padx=5)
        Button(action_frame, text="Reject Loan", font=("Arial", 10), bg="#e74c3c", fg="white", padx=5, command=self.reject_loan).pack(side=LEFT, padx=5)
        Button(action_frame, text="Record Repayment", font=("Arial", 10), 
               bg="#9b59b6", fg="white", padx=5, command=self.record_repayment).pack(side=LEFT, padx=5)
        Button(action_frame, text="Export Data", font=("Arial", 10), bg="#95a5a6", fg="white", padx=5).pack(side=RIGHT, padx=5)

    # --- Dashboard Functions ---

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
                elif status_filter == "Rejected":  # ADDED: Handle rejected loans filter
                     query["status"] = "Rejected"
                
            loans = list(database.db['loans'].find(query).sort("application_date", -1))
            return loans
        
        except Exception:
            # Fallback to mock data if DB access fails
            return MOCK_LOAN_DATA 

    def update_treeview(self, loan_list):
        """Clears and repopulates the Treeview with loan data."""
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for loan in loan_list:
            data = (
                str(loan.get('_id', 'N/A'))[-4:], # Show last 4 chars of ID
                loan.get('customer_name', 'N/A'),
                f"${loan.get('loan_amount', 0.00):,.2f}",
                loan.get('duration', 'N/A'),
                loan.get('status', 'Unknown'),
                loan.get('next_payment', 'N/A')
            )
            tag = loan.get('status', '').replace(" ", "").lower()
            self.tree.insert('', END, values=data, tags=(tag,))

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
        elif status == "Rejected":  # ADDED: Status text for rejected loans
            status_text = "Rejected Loans"
            
        self.current_status_label.config(text=f"Status: {status_text}")

    def search_loans(self):
        """Searches current Treeview data by name or status."""
        search_term = self.search_entry.get().lower()
        all_loans = self.fetch_loans(None) # Search across all data
        
        filtered_loans = [
            loan for loan in all_loans 
            if search_term in loan.get("customer_name", "").lower() or search_term in loan.get("status", "").lower()
        ]
        self.update_treeview(filtered_loans)
        self.current_status_label.config(text=f"Search Results for: '{search_term}'")

    def approve_loan(self):
        """Approves a selected loan by updating its status in the database."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a loan to approve.")
            return
        
        # Get the selected loan's full ID from the database
        selected_loan_id = self.tree.item(selected_item, 'values')[0]
        selected_loan_name = self.tree.item(selected_item, 'values')[1]
        
        # In a real application, you would use the actual loan ID from your data
        # For now, let's update based on customer name
        try:
            if database.db is not None:
                # Update the loan status in MongoDB
                result = database.db['loans'].update_one(
                    {"customer_name": selected_loan_name},
                    {"$set": {"status": "Approved"}}
                )
                
                if result.modified_count > 0:
                    messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been approved!")
                    # Refresh the treeview
                    self.filter_loans()
                else:
                    messagebox.showerror("Error", "Failed to update the loan status.")
            else:
                # For mock data, just show success message
                messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been approved!")
                self.filter_loans()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update loan status: {e}")

    def reject_loan(self):
        """Rejects a selected loan by updating its status in the database."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a loan to reject.")
            return
        
        # Get the selected loan's details
        selected_loan_id = self.tree.item(selected_item, 'values')[0]
        selected_loan_name = self.tree.item(selected_item, 'values')[1]
        
        try:
            if database.db is not None:
                # Update the loan status in MongoDB
                result = database.db['loans'].update_one(
                    {"customer_name": selected_loan_name},
                    {"$set": {"status": "Rejected"}}
                )
                
                if result.modified_count > 0:
                    messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been rejected!")
                    # Refresh the treeview
                    self.filter_loans()
                else:
                    messagebox.showerror("Error", "Failed to update the loan status.")
            else:
                # For mock data, just show success message
                messagebox.showinfo("Success", f"Loan for '{selected_loan_name}' has been rejected!")
                self.filter_loans()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update loan status: {e}")

    def record_repayment(self):
        """Opens repayment window for selected loan."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a loan to record repayment.")
            return
        
        # Get loan ID from selection
        selected_loan_name = self.tree.item(selected_item, 'values')[1]
        
        try:
            # Fetch loan details from database
            if database.db is not None:
                loan_data = database.db['loans'].find_one({"customer_name": selected_loan_name})
                if loan_data:
                    # Import and open repayment window
                    try:
                        from repayment import RepaymentWindow
                        repayment_win = RepaymentWindow(self, loan_data)
                    except ImportError as e:
                        # Fallback: show error message
                        messagebox.showerror("Import Error", 
                            f"Cannot import repayment module: {str(e)}\n"
                            f"Make sure 'repayment.py' exists in the same directory.")
                else:
                    messagebox.showerror("Error", "Could not find loan details.")
            else:
                messagebox.showinfo("Info", "Repayment feature requires database connection.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open repayment: {str(e)}")


if __name__ == "__main__":
    # Mock the database object if not running in the environment
    try:
        if 'db' not in dir(database):
            class MockDatabase:
                def __getitem__(self, key):
                    return self
                def insert_one(self, data):
                    return type('MockResult', (object,), {'inserted_id': 'mock_id'})()
                def find(self, query=None):
                    return MOCK_LOAN_DATA # Return mock data for dashboard
                def update_one(self, filter_query, update_data):
                    # Mock update functionality
                    print(f"Mock update: {filter_query} -> {update_data}")
                    return type('MockResult', (object,), {'modified_count': 1})()
                def sort(self, *args):
                    return self
                def __iter__(self):
                    return iter(MOCK_LOAN_DATA)
            database.db = MockDatabase()
    except NameError:
        class MockDatabase:
            def __getitem__(self, key):
                return self
            def insert_one(self, data):
                return type('MockResult', (object,), {'inserted_id': 'mock_id'})()
            def find(self, query=None):
                return MOCK_LOAN_DATA
            def update_one(self, filter_query, update_data):
                # Mock update functionality
                print(f"Mock update: {filter_query} -> {update_data}")
                return type('MockResult', (object,), {'modified_count': 1})()
            def sort(self, *args):
                return self
            def __iter__(self):
                return iter(MOCK_LOAN_DATA)
        database.db = MockDatabase()


    app = LoanApp()
    app.mainloop()