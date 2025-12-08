from tkinter import *
from tkinter import ttk, messagebox
# NOTE: database.py is not included, assuming it handles MongoDB connection
import database # Import your MongoDB connection file
import datetime 
import uuid 

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
        
        # Initialize and stack the frames (screens)
        for F in (ApplicationFrame, DashboardFrame):
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


# --- SCREEN 1: LOAN APPLICATION FORM ---
class ApplicationFrame(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="#e1ffc9") # Background color for the form screen
        
        # --- Application Variables (References from main controller) ---
        self.repayment_method_var = controller.repayment_method_var
        self.terms_var = controller.terms_var

        title_label=Label(self,text="APPLY FOR A LOAN",font=("Arial",20,"bold"),bg="#e1ffc9") # Reduced font size
        title_label.pack(pady=10)

        # Reduced padx/pady to fit content better in smaller window
        widget_frame=Frame(self,bg="white", padx=15, pady=15, relief="raised", bd=3) 
        widget_frame.pack()
        
        # --- Form Widgets (Instance variables for access) ---
        # Full Name
        Label(widget_frame,text="Full Name:",font=("Arial"), bg="white").grid(row=0,column=0,padx=5,pady=3,sticky=W)
        self.name_entry=Entry(widget_frame,font=("Arial"),width=25) # Reduced width
        self.name_entry.grid(row=0,column=1,padx=5,pady=3)

        # Loan Amount
        Label(widget_frame,text="Loan Amount:",font=("Arial"), bg="white").grid(row=1,column=0,padx=5,pady=3,sticky=W)
        self.amount_entry=Entry(widget_frame,font=("Arial"),width=25) # Reduced width
        self.amount_entry.grid(row=1,column=1,padx=5,pady=3)
        self.amount_entry.bind('<KeyRelease>', self.update_return_amount) 

        # Loan Type (Combo)
        Label(widget_frame,text="Loan type",font=("Arial"), bg="white").grid(row=2,column=0,padx=5,pady=3,sticky=W)
        self.type_combo = ttk.Combobox(widget_frame, values=["Personal Loan", "Business Loan", "Car Loan", "Home Loan","School Fees Loan"], font=("Arial", 10), state="readonly", width=23) # Reduced font/width
        self.type_combo.grid(row=2, column=1, pady=3)
        self.type_combo.bind("<<ComboboxSelected>>", self.update_return_amount)

        # Repayment Duration (Combo)
        Label(widget_frame,text="Repayment Duration",font=("Arial"), bg="white").grid(row=3,column=0,padx=5,pady=3,sticky=W)
        self.duration_combo = ttk.Combobox(widget_frame, values=["6 months", "1 year", "2 years", "3 years","5 years"], font=("Arial", 10), state="readonly", width=23) # Reduced font/width
        self.duration_combo.grid(row=3, column=1, pady=3,sticky=W)
        self.duration_combo.bind("<<ComboboxSelected>>", self.update_return_amount) 

        # Repayment Method (Radiobuttons)
        Label(widget_frame,text="Repayment Method",font=("Arial"), bg="white").grid(row=4, column=0, pady=3,sticky=W)
        Radiobutton(widget_frame, text="Monthly", value="Monthly", variable=self.repayment_method_var, font=("Arial"), bg="white").grid(row=4, column=1, pady=3, sticky="w")
        Radiobutton(widget_frame, text="Weekly", value="Weekly", variable=self.repayment_method_var, font=("Arial"), bg="white").grid(row=4, column=2, pady=3, sticky="w")

        # Loan Purpose (Textarea)
        Label(widget_frame,text="Loan purpose:", font=("Arial", 12), bg="white").grid(row=5,column=0,sticky="w",pady=3)
        self.loan_purpose_text = Text(widget_frame, height=3, width=25, font=("Arial", 10)) # Reduced height/width/font
        self.loan_purpose_text.grid(row=5, column=1, pady=3)

        # Collateral Security
        Label(widget_frame,text="Collateral Security:", font=("Arial", 12), bg="white").grid(row=6, column=0, sticky="w", pady=3)
        self.collateral_entry = Entry(widget_frame, font=("Arial", 10), width=25) # Reduced font/width
        self.collateral_entry.grid(row=6, column=1, pady=3)

        # Return Amount (Display only)
        Label(widget_frame,text="Estimated Return Amount:", font=("Arial", 12), bg="white").grid(row=7, column=0, sticky="w", pady=3)
        self.return_amount_entry = Entry(widget_frame, font=("Arial", 10), width=25, state="readonly") # Reduced font/width
        self.return_amount_entry.grid(row=7, column=1, pady=3)

        # Terms and Conditions
        Checkbutton(widget_frame, text="I accept the terms and conditions", variable=self.terms_var, font=("Arial", 10), bg="white").grid(row=8, columnspan=2, pady=8)

        btn_frame = Frame(self, bg="#e1ffc9")
        btn_frame.pack(pady=10)

        # Submit Button
        Button(btn_frame, text="Submit Application", bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=15, command=self.submit_application).grid(row=0, column=0, padx=5) # Reduced width/font
        # Clear Button
        Button(btn_frame, text="Clear", bg="#dc3545", fg="white", font=("Arial", 10, "bold"), width=8, command=self.clear_form).grid(row=0, column=1, padx=5) # Reduced width/font
        # Back to Dashboard Button (Now uses the controller's show_frame method)
        Button(btn_frame, text="Dashboard", bg="#007bff", fg="white", font=("Arial", 10, "bold"), width=12, command=lambda: controller.show_frame("DashboardFrame")).grid(row=0, column=2, padx=5) # Reduced width/font


    def calculate_return_amount(self):
        """Calculates the total repayment amount (Principal + Interest)."""
        try:
            loan_amount = float(self.amount_entry.get())
            duration_text = self.duration_combo.get()
            
            if "year" in duration_text:
                years = int(duration_text.split()[0])
            elif "month" in duration_text:
                months = int(duration_text.split()[0])
                years = months / 12.0
            else:
                return 0
                
            ANNUAL_INTEREST_RATE = 0.12 
            interest_amount = loan_amount * ANNUAL_INTEREST_RATE * years
            total_return_amount = loan_amount + interest_amount
            
            return round(total_return_amount, 2)
            
        except (ValueError, Exception):
            return 0


    def update_return_amount(self, event=None):
        """Updates the return amount entry based on user input."""
        total = self.calculate_return_amount()
        self.return_amount_entry.config(state="normal")
        self.return_amount_entry.delete(0, END)
        self.return_amount_entry.insert(0, f"{total:,.2f}")
        self.return_amount_entry.config(state="readonly")


    def submit_application(self):
        """Gathers form data, validates, and saves to MongoDB."""
        try:
            customer_name = self.name_entry.get()
            loan_amount_str = self.amount_entry.get()
            loan_type = self.type_combo.get()
            repayment_duration = self.duration_combo.get()
            repayment_method = self.repayment_method_var.get()
            loan_purpose = self.loan_purpose_text.get("1.0", END).strip()
            collateral_security = self.collateral_entry.get()
            terms_accepted = self.terms_var.get()
            
            if not all([customer_name, loan_amount_str, loan_type, repayment_duration]) or not loan_purpose:
                messagebox.showerror("Validation Error", "Please fill in all required fields.")
                return
            
            if terms_accepted != 1:
                messagebox.showerror("Validation Error", "You must accept the terms and conditions.")
                return

            try:
                loan_amount = float(loan_amount_str)
                if loan_amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Loan Amount must be a valid number greater than zero.")
                return
                
            total_return_amount = self.calculate_return_amount()

            loan_data = {
                "loan_id": str(uuid.uuid4()), 
                "customer_name": customer_name,
                "loan_amount": loan_amount,
                "loan_type": loan_type, 
                "duration": repayment_duration,
                "repayment_method": repayment_method,
                "purpose": loan_purpose,
                "collateral": collateral_security if collateral_security else "None Provided",
                "return_amount": total_return_amount,
                "interest_rate": 0.12, 
                "application_date": datetime.datetime.now(),
                "status": "Pending",
                "next_payment": "N/A" 
            }
            
            if database.db is None:
                messagebox.showerror("DB Error", "Database not connected. Cannot submit application.")
                return
                
            result = database.db['loans'].insert_one(loan_data)
            
            if result.inserted_id:
                messagebox.showinfo("Success", f"Application submitted successfully! Loan ID: {loan_data['loan_id']}")
                self.clear_form()
            else:
                messagebox.showerror("Submission Failed", "Failed to save application to the database.")

        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")


    def clear_form(self):
        """Clears all fields in the form."""
        self.name_entry.delete(0, END)
        self.amount_entry.delete(0, END)
        self.type_combo.set('')
        self.duration_combo.set('')
        self.repayment_method_var.set("Monthly")
        self.terms_var.set(0)
        self.loan_purpose_text.delete("1.0", END)
        self.collateral_entry.delete(0, END)
        self.update_return_amount() 


# --- SCREEN 2: LOAN MANAGEMENT DASHBOARD ---
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

        # Button to switch to Application Form
        Button(sidebar, text="Open New Application", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", width=18, command=lambda: controller.show_frame("ApplicationFrame")).pack(pady=(5, 10)) # Reduced width/font

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