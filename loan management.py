from tkinter import *
from tkinter import ttk, messagebox
import database # Import MongoDB connection

# --- MOCK DATA (Updated to match MongoDB structure and statuses) ---
# In a real app, this data would be fetched directly from database.db['loans'].find()
MOCK_LOAN_DATA = [
    {"_id": "65b4c1a5", "customer_name": "Alice Smith", "loan_amount": 5000.00, "duration": "2 years", "status": "Approved", "next_payment": "2025-12-15"},
    {"_id": "65b4c1a6", "customer_name": "Bob Johnson", "loan_amount": 12000.00, "duration": "5 years", "status": "Under Payment", "next_payment": "2025-12-20"},
    {"_id": "65b4c1a7", "customer_name": "Charlie Brown", "loan_amount": 1500.00, "duration": "6 months", "status": "Fully Paid", "next_payment": "N/A"},
    {"_id": "65b4c1a8", "customer_name": "Diana Prince", "loan_amount": 8500.00, "duration": "3 years", "status": "Pending", "next_payment": "N/A"},
    {"_id": "65b4c1a9", "customer_name": "Ethan Hunt", "loan_amount": 25000.00, "duration": "5 years", "status": "Under Payment", "next_payment": "2025-12-25"},
]

# --- DATABASE FETCH FUNCTION ---
def fetch_loans(status_filter=None):
    """Fetches loan data from MongoDB, applying an optional status filter."""
    if database.db is None:
        messagebox.showerror("DB Error", "Database connection failed. Using mock data.")
        return MOCK_LOAN_DATA # Fallback to mock data if connection fails

    try:
        query = {}
        if status_filter:
            # Map simplified status to database status
            if status_filter == "Active": # Loans Under Payment
                 query["status"] = {"$in": ["Under Payment", "Approved"]}
            elif status_filter == "Closed": # Fully Paid Loans
                 query["status"] = "Fully Paid"
            elif status_filter == "Pending": # New Applications
                 query["status"] = "Pending"
            
        # Fetch data from the 'loans' collection
        loans = list(database.db['loans'].find(query).sort("application_date", -1))
        
        # NOTE: If your MongoDB doesn't have any data yet, the list will be empty.
        # Returning the actual data if available.
        return loans
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        messagebox.showwarning("DB Query Warning", "Could not fetch live data. Using mock data as a fallback.")
        return MOCK_LOAN_DATA


# --- TREEVIEW DISPLAY FUNCTIONS ---
def update_treeview(loan_list):
    """Clears and repopulates the Treeview with loan data."""
    # Clear existing data
    for i in tree.get_children():
        tree.delete(i)
        
    # Populate with new data
    for loan in loan_list:
        # Prepare data tuple for insertion
        data = (
            str(loan.get('_id'))[-4:], # Show last 4 chars of MongoDB ID for brevity
            loan.get('customer_name', 'N/A'),
            f"${loan.get('loan_amount', 0.00):,.2f}",
            loan.get('duration', 'N/A'),
            loan.get('status', 'Unknown'),
            loan.get('next_payment', 'N/A')
        )
        # Use status for tag to color the row
        tag = loan.get('status').replace(" ", "").lower()
        tree.insert('', END, values=data, tags=(tag,))

def filter_loans(status=None):
    """Filters data based on status and updates the Treeview."""
    # This function uses the new fetch_loans to get data based on the filter
    loans = fetch_loans(status)
    update_treeview(loans)
    if status == "Active":
        current_status_label.config(text="Status: Under Payment/Approved")
    elif status == "Closed":
        current_status_label.config(text="Status: Fully Paid")
    elif status == "Pending":
        current_status_label.config(text="Status: Pending Applications")
    else:
        current_status_label.config(text="Status: All Loans")


# --- SEARCH FUNCTION ---
def search_loans():
    """Searches current Treeview data by name or status."""
    search_term = search_entry.get().lower()
    
    # Fetch all data (or the current filtered data, depending on design)
    all_loans = fetch_loans() 
    
    filtered_loans = [
        loan for loan in all_loans 
        if search_term in loan.get("customer_name", "").lower() or search_term in loan.get("status", "").lower()
    ]
    update_treeview(filtered_loans)
    current_status_label.config(text=f"Search Results for: '{search_term}'")


# --- UI ACTIONS ---
def approve_loan():
    """Placeholder function to simulate approving a loan in the database."""
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a loan to approve.")
        return
        
    loan_id_last_4 = tree.item(selected_item, 'values')[0]
    
    # In a real app, you would look up the full ID using loan_id_last_4 and then:
    # database.db['loans'].update_one({"_id": full_id}, {"$set": {"status": "Under Payment"}})
    
    messagebox.showinfo("Success", f"Loan ending in '{loan_id_last_4}' approved and status set to 'Under Payment'.")
    filter_loans() # Refresh the view


def reject_loan():
    """Placeholder function to simulate rejecting a loan in the database."""
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a loan to reject.")
        return
        
    loan_id_last_4 = tree.item(selected_item, 'values')[0]
    
    # database.db['loans'].update_one({"_id": full_id}, {"$set": {"status": "Rejected"}})
    
    messagebox.showinfo("Success", f"Loan ending in '{loan_id_last_4}' rejected.")
    filter_loans() # Refresh the view
    
    
# --- GUI SETUP ---
window = Tk()
window.title("Loan Management Dashboard")
window.geometry("1100x750")
window.config(bg="#ecf0f1") # Light gray/blue background

# Make window resizable
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(1, weight=1)

# --- 1. SIDEBAR FRAME (Search and Filters) ---
sidebar = Frame(window, bg="#34495e", width=250, padx=10, pady=10) # Dark sidebar
sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew") 

Label(sidebar, text="Loan Filter & Search", font=("Arial", 16, "bold"), bg="#34495e", fg="white").pack(pady=(10, 20))

# Search Section
Label(sidebar, text="SEARCH LOANS", font=("Arial", 12), bg="#34495e", fg="#bdc3c7").pack(pady=(10, 5))
search_entry = Entry(sidebar, font=("Arial", 12), width=25)
search_entry.pack(pady=5)
search_button = Button(sidebar, text="Search", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", width=20, command=search_loans)
search_button.pack(pady=(0, 20))

# Status Filter Buttons
Label(sidebar, text="FILTER BY STATUS", font=("Arial", 12), bg="#34495e", fg="#bdc3c7").pack(pady=(10, 5))

Button(sidebar, text="All Loans", font=("Arial", 12), bg="#ecf0f1", width=20, command=lambda: filter_loans(None)).pack(pady=5)
Button(sidebar, text="Pending/New", font=("Arial", 12), bg="#f1c40f", width=20, command=lambda: filter_loans("Pending")).pack(pady=5)
Button(sidebar, text="Under Payment", font=("Arial", 12), bg="#3498db", fg="white", width=20, command=lambda: filter_loans("Active")).pack(pady=5)
Button(sidebar, text="Fully Paid", font=("Arial", 12), bg="#2ecc71", fg="white", width=20, command=lambda: filter_loans("Closed")).pack(pady=5)


# --- 2. MAIN HEADER & STATUS (Top Row) ---
header_frame = Frame(window, bg="white", padx=10, pady=10)
header_frame.grid(row=0, column=1, sticky="ew")

Label(header_frame, text="Current Loan Applications", font=("Arial", 22, "bold"), bg="white", fg="#2c3e50").pack(side=LEFT)
current_status_label = Label(header_frame, text="Status: All Loans", font=("Arial", 14), bg="white", fg="#2c3e50")
current_status_label.pack(side=RIGHT)


# --- 3. TREEVIEW (Main Data Table) ---
main_content_frame = Frame(window, bg="#ecf0f1")
main_content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

# Treeview Columns
columns = ('#id', 'customer_name', 'loan_amount', 'duration', 'status', 'next_payment')
tree = ttk.Treeview(main_content_frame, columns=columns, show='headings')

# Define Headings
tree.heading('#id', text='Loan ID')
tree.heading('customer_name', text='Customer Name')
tree.heading('loan_amount', text='Amount')
tree.heading('duration', text='Term')
tree.heading('status', text='Status')
tree.heading('next_payment', text='Next Payment Due')

# Define Column Widths
tree.column('#id', width=60, anchor='center')
tree.column('customer_name', width=150)
tree.column('loan_amount', width=100, anchor='e')
tree.column('duration', width=80, anchor='center')
tree.column('status', width=100, anchor='center')
tree.column('next_payment', width=120, anchor='center')

# Treeview Styling for Status Coloring (Optional, but adds visual clarity)
tree.tag_configure('pending', background='#fcf8e3', foreground='#8a6d3b') # Light Yellow
tree.tag_configure('underpayment', background='#d9edf7', foreground='#31708f') # Light Blue
tree.tag_configure('fullypaid', background='#dff0d8', foreground='#3c763d') # Light Green
tree.tag_configure('approved', background='#fae8ff', foreground='#9c27b0') # Light Purple

# Add Scrollbar
scrollbar = ttk.Scrollbar(main_content_frame, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)
tree.pack(fill=BOTH, expand=True)


# --- 4. ACTION BUTTONS (Bottom Row) ---
action_frame = Frame(window, bg="#ecf0f1", padx=10, pady=10)
action_frame.grid(row=2, column=1, sticky="ew")

Button(action_frame, text="View/Edit Details", font=("Arial", 12), bg="#3498db", fg="white", padx=10).pack(side=LEFT, padx=10)
Button(action_frame, text="Approve Loan", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", padx=10, command=approve_loan).pack(side=LEFT, padx=10)
Button(action_frame, text="Reject Loan", font=("Arial", 12), bg="#e74c3c", fg="white", padx=10, command=reject_loan).pack(side=LEFT, padx=10)
Button(action_frame, text="Export Data (CSV)", font=("Arial", 12), bg="#95a5a6", fg="white", padx=10).pack(side=RIGHT, padx=10)


# Initialize and display all loans on startup
filter_loans(None) 

window.mainloop()