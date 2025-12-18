import tkinter as tk
from tkinter import ttk, messagebox
import database  # Import your MongoDB connection file
import subprocess
import sys
import os

# --- IMPORT NECESSARY EXTERNAL WINDOWS ---
try:
    from view_loan_details import ViewLoanDetailsPage as LoanDetailsViewer 
except ImportError:
    LoanDetailsViewer = None 

# --- MAIN APPLICATION CLASS ---
class LoanApp(tk.Tk):
    """Main application window managing different screens/frames."""
    def __init__(self):
        super().__init__()
        self.title("Unified Loan Management System")
        self.geometry("1100x700") 
        self.config(bg="#ecf0f1")
        
        if not hasattr(database, 'db') or database.db is None:
            messagebox.showerror("Initialization Error", 
                                 "Database connection failed. Please check 'database.py'. Exiting.")
            self.destroy()
            sys.exit()
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DashboardFrame,):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "DashboardFrame":
            frame.filter_loans(None)

    def open_loan_application(self):
        try:
            loan_app_file = "loan application.py" 
            if not os.path.exists(loan_app_file):
                variations = ["loan_application.py", "loanapplication.py", "LoanApplication.py"]
                found_file = next((v for v in variations if os.path.exists(v)), None)
                if not found_file:
                    messagebox.showerror("File Not Found", f"Could not find '{loan_app_file}'")
                    return
                loan_app_file = found_file
            subprocess.Popen([sys.executable, loan_app_file])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open loan application: {str(e)}")

    def back_to_dashboard_file(self):
        try:
            target_file = "dashboard.py"
            if os.path.exists(target_file):
                subprocess.Popen([sys.executable, target_file])
                self.destroy() 
            else:
                messagebox.showerror("Error", "dashboard.py not found.")
        except Exception as e:
            messagebox.showerror("Navigation Error", f"Failed to return to dashboard: {e}")


# --- SCREEN 1: LOAN MANAGEMENT DASHBOARD ---
class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="#ecf0f1")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- SIDEBAR ---
        sidebar = tk.Frame(self, bg="#34495e", width=220, padx=15, pady=10)
        sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew") 

        tk.Label(sidebar, text="Loan Management", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=(10, 20))

        tk.Button(sidebar, text="← Return to Dashboard", font=("Arial", 10, "bold"),
                  bg="#3498db", fg="white", width=20, height=2,
                  command=controller.back_to_dashboard_file).pack(pady=(0, 20))

        tk.Button(sidebar, text="+ New Application", font=("Arial", 10, "bold"),
                  bg="#2ecc71", fg="white", width=20,
                  command=controller.open_loan_application).pack(pady=(5, 10))

        # Search Section
        tk.Label(sidebar, text="SEARCH RECORDS", font=("Arial", 9, "bold"), bg="#34495e", fg="#bdc3c7").pack(pady=(20, 5))
        self.search_entry = tk.Entry(sidebar, font=("Arial", 10), width=22)
        self.search_entry.pack(pady=5)
        tk.Button(sidebar, text="Run Search", font=("Arial", 10, "bold"), bg="#95a5a6", fg="white", width=20, command=self.search_loans).pack(pady=(0, 15))

        # Status Filters
        tk.Label(sidebar, text="FILTER BY STATUS", font=("Arial", 9, "bold"), bg="#34495e", fg="#bdc3c7").pack(pady=(15, 5))
        tk.Button(sidebar, text="All Loans", font=("Arial", 10), bg="#ecf0f1", width=20, command=lambda: self.filter_loans(None)).pack(pady=3)
        tk.Button(sidebar, text="Pending/New", font=("Arial", 10), bg="#f1c40f", width=20, command=lambda: self.filter_loans("Pending")).pack(pady=3)
        tk.Button(sidebar, text="Under Payment", font=("Arial", 10), bg="#3498db", fg="white", width=20, command=lambda: self.filter_loans("Active")).pack(pady=3)
        tk.Button(sidebar, text="Fully Paid", font=("Arial", 10), bg="#2ecc71", fg="white", width=20, command=lambda: self.filter_loans("Closed")).pack(pady=3)
        tk.Button(sidebar, text="Rejected Loans", font=("Arial", 10), bg="#e74c3c", fg="white", width=20, command=lambda: self.filter_loans("Rejected")).pack(pady=3)

        # --- MAIN HEADER ---
        header_frame = tk.Frame(self, bg="white", padx=20, pady=15)
        header_frame.grid(row=0, column=1, sticky="ew")

        tk.Label(header_frame, text="Current Loan Applications", font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT)
        self.current_status_label = tk.Label(header_frame, text="Displaying: All Loans", font=("Arial", 12), bg="white", fg="#7f8c8d")
        self.current_status_label.pack(side=tk.RIGHT)

        # --- TREEVIEW ---
        main_content_frame = tk.Frame(self, bg="#ecf0f1")
        main_content_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=5)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(0, weight=1)

        columns = ('#id', 'customer_name', 'loan_amount', 'duration', 'status', 'next_payment')
        self.tree = ttk.Treeview(main_content_frame, columns=columns, show='headings')

        self.tree.heading('#id', text='ID'); self.tree.heading('customer_name', text='Customer Full Name')
        self.tree.heading('loan_amount', text='Loan Amount'); self.tree.heading('duration', text='Term Duration')
        self.tree.heading('status', text='Status'); self.tree.heading('next_payment', text='Due Date')

        self.tree.column('#id', width=60, anchor='center'); self.tree.column('customer_name', width=250)
        self.tree.column('loan_amount', width=120, anchor='e'); self.tree.column('duration', width=100, anchor='center')
        self.tree.column('status', width=120, anchor='center'); self.tree.column('next_payment', width=150, anchor='center')

        self.tree.tag_configure('pending', background='#fcf8e3', foreground='#8a6d3b')
        self.tree.tag_configure('underpayment', background='#d9edf7', foreground='#31708f')
        self.tree.tag_configure('fullypaid', background='#dff0d8', foreground='#3c763d')
        self.tree.tag_configure('approved', background='#fae8ff', foreground='#9c27b0')
        self.tree.tag_configure('rejected', background='#fdecea', foreground='#d32f2f')

        scrollbar = ttk.Scrollbar(main_content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- ACTION BUTTONS ---
        action_frame = tk.Frame(self, bg="#ecf0f1", padx=20, pady=15)
        action_frame.grid(row=2, column=1, sticky="ew")

        tk.Button(action_frame, text="🔍 View/Edit Details", font=("Arial", 10), bg="#3498db", fg="white", padx=10, 
                  command=self.view_loan_details).pack(side=tk.LEFT, padx=5)

        tk.Button(action_frame, text="✅ Approve Loan", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", padx=10, 
                  command=self.approve_loan).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="❌ Reject Loan", font=("Arial", 10), bg="#e74c3c", fg="white", padx=10, 
                  command=self.reject_loan).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="💰 Record Repayment", font=("Arial", 10), bg="#9b59b6", fg="white", padx=10, 
                  command=self.record_repayment).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📥 Export CSV", font=("Arial", 10), bg="#95a5a6", fg="white", padx=10).pack(side=tk.RIGHT, padx=5)

    def _get_selected_loan_full_id(self):
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Selection Error", "Please select a loan from the list first.")
            return None
        return selected_item_iid 

    def _get_loan_data_from_db(self, loan_id):
        try:
            return database.get_loan_by_id(loan_id)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch data: {e}")
            return None

    # --- UPDATED LOGIC METHODS ---

    def approve_loan(self):
        loan_id = self._get_selected_loan_full_id()
        if not loan_id: return
        
        loan_data = self._get_loan_data_from_db(loan_id)
        if not loan_data: return
        
        current_status = loan_data.get('status', 'Pending')

        # Check if already processed
        if current_status in ["Approved", "Under Payment", "Active"]:
            messagebox.showinfo("Status Check", f"This loan is already {current_status}.")
            return
        
        if current_status == "Fully Paid":
            messagebox.showwarning("Action Denied", "This loan is already completed and closed.")
            return

        try:
            database.update_loan_status(loan_id, "Approved")
            messagebox.showinfo("Success", "Loan has been Approved.")
            self.filter_loans(None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve: {str(e)}")

    def reject_loan(self):
        loan_id = self._get_selected_loan_full_id()
        if not loan_id: return
        
        loan_data = self._get_loan_data_from_db(loan_id)
        if not loan_data: return
        
        current_status = loan_data.get('status', 'Pending')

        # BLOCK REJECTION IF ALREADY APPROVED OR ACTIVE
        if current_status in ["Approved", "Under Payment", "Active", "Fully Paid"]:
            messagebox.showerror("Action Denied", 
                                f"Cannot reject a loan that is currently '{current_status}'.\n"
                                "Only 'Pending' loans can be rejected.")
            return
        
        if current_status == "Rejected":
            messagebox.showinfo("Status Check", "This loan is already rejected.")
            return

        # Double check with user
        confirm = messagebox.askyesno("Confirm Rejection", "Are you sure you want to reject this loan?")
        if confirm:
            try:
                database.update_loan_status(loan_id, "Rejected")
                messagebox.showinfo("Success", "Loan Application Rejected.")
                self.filter_loans(None)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reject: {str(e)}")

    # --- END UPDATED LOGIC ---

    def view_loan_details(self):
        full_loan_id = self._get_selected_loan_full_id()
        if full_loan_id:
            loan_data = self._get_loan_data_from_db(full_loan_id)
            if not loan_data: return
            if LoanDetailsViewer is None:
                messagebox.showerror("Error", "view_loan_details.py not found.")
                return

            try:
                detail_window = tk.Toplevel(self.controller)
                detail_window.title(f"Loan Record: {loan_data.get('customer_name')}")
                detail_window.geometry("850x700")
                detail_window.grab_set() 
                
                def close_and_refresh():
                    detail_window.grab_release()
                    detail_window.destroy()
                    self.filter_loans(None) 

                LoanDetailsViewer(detail_window, full_loan_id, close_and_refresh)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open details: {e}")

    def fetch_loans(self, status_filter=None):
        try:
            query = {}
            if status_filter:
                if status_filter == "Active":
                    query["status"] = {"$in": ["Under Payment", "Approved"]}
                elif status_filter == "Closed":
                    query["status"] = "Fully Paid"
                else:
                    query["status"] = status_filter
            loans = database.db['loans'].find(query)
            return list(loans)
        except Exception as e:
            messagebox.showerror("Database Error", f"Retrieval failed: {e}")
            return []

    def update_treeview(self, loan_list):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for loan in loan_list:
            full_loan_id = str(loan.get('_id', 'N/A'))
            data = (
                full_loan_id[-4:],
                loan.get('customer_name', 'N/A'),
                f"RWF {loan.get('loan_amount', 0.00):,.2f}", 
                loan.get('duration', 'N/A'),
                loan.get('status', 'Unknown'),
                loan.get('next_payment', 'N/A')
            )
            tag = loan.get('status', '').replace(" ", "").lower()
            self.tree.insert('', tk.END, iid=full_loan_id, values=data, tags=(tag,))

    def filter_loans(self, status=None):
        loans = self.fetch_loans(status)
        self.update_treeview(loans)
        status_text = status if status else "All Loans"
        self.current_status_label.config(text=f"Displaying: {status_text}")

    def search_loans(self):
        search_term = self.search_entry.get().lower()
        all_loans = self.fetch_loans(None)
        filtered_loans = [
            loan for loan in all_loans
            if search_term in loan.get("customer_name", "").lower() or search_term in loan.get("status", "").lower()
        ]
        self.update_treeview(filtered_loans)

    def record_repayment(self):
        loan_id = self._get_selected_loan_full_id()
        if not loan_id: return
        loan_data = self._get_loan_data_from_db(loan_id)
        try:
            from repayment import RepaymentWindow
            RepaymentWindow(self, loan_data, self.filter_loans)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open repayment: {e}")

if __name__ == "__main__":
    app = LoanApp()
    app.mainloop()