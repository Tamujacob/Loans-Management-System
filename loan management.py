import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database  # MongoDB connection
import subprocess
import sys
import os
import pandas as pd # Required: pip install pandas openpyxl
from datetime import datetime
from bson.objectid import ObjectId

# --- SESSION PERSISTENCE ---
try:
    CURRENT_USER_ROLE = sys.argv[1]
    CURRENT_USER_NAME = sys.argv[2]
except IndexError:
    CURRENT_USER_ROLE = "Staff"
    CURRENT_USER_NAME = "Guest"

# --- SAFE IMPORT FOR DATEUTIL ---
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    relativedelta = None

# --- IMPORT EXTERNAL WINDOWS ---
try:
    from view_loan_details import ViewLoanDetailsPage as LoanDetailsViewer 
except ImportError:
    LoanDetailsViewer = None 

# --- MAIN APPLICATION CLASS ---
class LoanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Loan Management System - User: {CURRENT_USER_NAME}")
        self.geometry("1100x750") 
        self.config(bg="#ecf0f1")
        
        # Set Window Icon
        try:
            self.iconphoto(True, tk.PhotoImage(file="bu logo.png"))
        except:
            pass

        if not hasattr(database, 'db') or database.db is None:
            messagebox.showerror("Initialization Error", "Database connection failed.")
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
            # Pass role logic to application
            subprocess.Popen([sys.executable, "loan application.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open loan application: {str(e)}")

    def back_to_dashboard_file(self):
        """Returns to main dashboard while maintaining role/session."""
        try:
            subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
            self.destroy() 
        except Exception as e:
            messagebox.showerror("Navigation Error", f"Failed: {e}")

    def logout_system(self):
        """Standard logout logic to clear session and return to login screen."""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out?"):
            try:
                subprocess.Popen([sys.executable, "login.py"])
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Logout failed: {e}")

# --- LOAN MANAGEMENT DASHBOARD ---
class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="#ecf0f1")
        self.current_filter = None 
        
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

        tk.Label(sidebar, text="SEARCH RECORDS", font=("Arial", 9, "bold"), bg="#34495e", fg="#bdc3c7").pack(pady=(20, 5))
        self.search_entry = tk.Entry(sidebar, font=("Arial", 10), width=22)
        self.search_entry.pack(pady=5)
        tk.Button(sidebar, text="Run Search", font=("Arial", 10, "bold"), bg="#95a5a6", fg="white", width=20, command=self.search_loans).pack(pady=(0, 15))

        tk.Label(sidebar, text="FILTER BY STATUS", font=("Arial", 9, "bold"), bg="#34495e", fg="#bdc3c7").pack(pady=(15, 5))
        tk.Button(sidebar, text="All Loans", font=("Arial", 10), bg="#ecf0f1", width=20, command=lambda: self.filter_loans(None)).pack(pady=3)
        tk.Button(sidebar, text="Pending/New", font=("Arial", 10), bg="#f1c40f", width=20, command=lambda: self.filter_loans("Pending")).pack(pady=3)
        tk.Button(sidebar, text="Under Payment", font=("Arial", 10), bg="#3498db", fg="white", width=20, command=lambda: self.filter_loans("Active")).pack(pady=3)
        tk.Button(sidebar, text="Fully Paid", font=("Arial", 10), bg="#2ecc71", fg="white", width=20, command=lambda: self.filter_loans("Closed")).pack(pady=3)
        tk.Button(sidebar, text="Rejected Loans", font=("Arial", 10), bg="#e74c3c", fg="white", width=20, command=lambda: self.filter_loans("Rejected")).pack(pady=3)
        
        tk.Button(sidebar, text="♻️ Recycle Bin", font=("Arial", 10, "italic"), bg="#7f8c8d", fg="white", width=20, command=lambda: self.filter_loans("Recycle")).pack(pady=(20, 3))

        # --- LOGOUT BUTTON (ORANGE - BELOW RECYCLE BIN) ---
        tk.Button(sidebar, text="🛑 Sign Out System", font=("Arial", 10, "bold"), 
                  bg="#e67e22", fg="white", width=20, height=2,
                  command=controller.logout_system).pack(pady=(20, 10))

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

        # Status Tags
        self.tree.tag_configure('pending', background='#fcf8e3', foreground='#8a6d3b')
        self.tree.tag_configure('underpayment', background='#d9edf7', foreground='#31708f')
        self.tree.tag_configure('fullypaid', background='#dff0d8', foreground='#3c763d')
        self.tree.tag_configure('approved', background='#fae8ff', foreground='#9c27b0')
        self.tree.tag_configure('rejected', background='#fdecea', foreground='#d32f2f')
        self.tree.tag_configure('deleted', background='#f2f2f2', foreground='#95a5a6')

        self.tree.bind("<<TreeviewSelect>>", self.on_loan_select)

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
        
        tk.Button(action_frame, text="❌ Reject Loan", font=("Arial", 10), bg="#e67e22", fg="white", padx=10, 
                  command=self.reject_loan).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="🗑️ Delete Loan", font=("Arial", 10), bg="#c0392b", fg="white", padx=10, 
                  command=self.delete_loan).pack(side=tk.LEFT, padx=5)
        
        self.btn_repayment = tk.Button(action_frame, text="💰 Record Repayment", font=("Arial", 10), bg="#9b59b6", fg="white", padx=10, 
                  command=self.record_repayment)
        self.btn_repayment.pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📥 Export Excel", font=("Arial", 10, "bold"), bg="#27ae60", fg="white", padx=10,
                  command=self.open_export_options).pack(side=tk.RIGHT, padx=5)

    # --- UPDATED EXPORT LOGIC WITH SAVE-AS DIALOG ---
    def open_export_options(self):
        self.export_win = tk.Toplevel(self)
        self.export_win.title("Export Range Selection")
        self.export_win.geometry("400x320")
        self.export_win.configure(bg="white")
        self.export_win.grab_set()

        tk.Label(self.export_win, text="EXCEL EXPORT", font=("Arial", 14, "bold"), bg="white", fg="#27ae60").pack(pady=10)
        tk.Label(self.export_win, text=f"Active Filter: {self.current_status_label.cget('text')}", font=("Arial", 9), bg="white").pack()

        tk.Label(self.export_win, text="Start Date (YYYY-MM-DD):", bg="white").pack(pady=(15, 0))
        self.start_date_ent = tk.Entry(self.export_win, font=("Arial", 12), justify="center")
        self.start_date_ent.insert(0, datetime.now().strftime("%Y-01-01"))
        self.start_date_ent.pack(pady=5)

        tk.Label(self.export_win, text="End Date (YYYY-MM-DD):", bg="white").pack(pady=(5, 0))
        self.end_date_ent = tk.Entry(self.export_win, font=("Arial", 12), justify="center")
        self.end_date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_ent.pack(pady=5)

        tk.Button(self.export_win, text="SELECT LOCATION & SAVE", bg="#2ecc71", fg="white", 
                  font=("Arial", 11, "bold"), width=25, height=2, bd=0, command=self.process_export).pack(pady=20)

    def process_export(self):
        try:
            start_dt = datetime.strptime(self.start_date_ent.get(), "%Y-%m-%d")
            end_dt = datetime.strptime(self.end_date_ent.get(), "%Y-%m-%d").replace(hour=23, minute=59)
            
            default_fn = f"Loan_Report_{self.start_date_ent.get()}_to_{self.end_date_ent.get()}.xlsx"
            file_path = filedialog.asksaveasfilename(
                initialfile=default_fn,
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Choose where to save your report"
            )

            if not file_path: 
                return

            query = {
                "application_date": {"$gte": start_dt, "$lte": end_dt},
                "is_deleted": {"$ne": True} if self.current_filter != "Recycle" else True
            }

            if self.current_filter and self.current_filter != "Recycle":
                if self.current_filter == "Active":
                    query["status"] = {"$in": ["Under Payment", "Approved"]}
                else:
                    query["status"] = self.current_filter

            data = list(database.db['loans'].find(query))

            if not data:
                messagebox.showwarning("No Results", "No loans found for this date range/status.")
                return

            cleaned = []
            for loan in data:
                row = loan.copy()
                row['_id'] = str(row['_id'])
                cleaned.append(row)

            df = pd.DataFrame(cleaned)
            df.to_excel(file_path, index=False)

            self.export_win.destroy()
            if messagebox.askyesno("Success", f"Exported {len(cleaned)} records.\nOpen file now?"):
                os.startfile(file_path)

        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def on_loan_select(self, event):
        selected_id = self.tree.focus()
        if not selected_id: return
        loan_data = database.get_loan_by_id(selected_id)
        if loan_data:
            status = loan_data.get("status", "Pending")
            is_deleted = loan_data.get("is_deleted", False)
            if status in ["Pending", "Rejected"] or is_deleted:
                self.btn_repayment.config(state=tk.DISABLED, bg="#bdc3c7")
            else:
                self.btn_repayment.config(state=tk.NORMAL, bg="#9b59b6")

    def approve_loan(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        loan_data = database.get_loan_by_id(loan_id)
        if loan_data.get("is_deleted"): return
        
        duration = loan_data.get('duration', '0 months')
        due_date = "N/A"
        if relativedelta:
            try:
                val = int(duration.split()[0])
                due_date = (datetime.now() + relativedelta(months=val)).strftime("%Y-%m-%d")
            except: pass

        database.update_loan_status(loan_id, "Approved")
        database.db['loans'].update_one({"_id": ObjectId(loan_id)}, {"$set": {"next_payment": due_date}})
        messagebox.showinfo("Success", "Loan Approved")
        self.filter_loans(self.current_filter)

    def fetch_loans(self, status_filter=None):
        query = {"is_deleted": True} if status_filter == "Recycle" else {"is_deleted": {"$ne": True}}

        if status_filter and status_filter != "Recycle":
            if status_filter == "Active":
                query["status"] = {"$in": ["Under Payment", "Approved"]}
            elif status_filter == "Closed":
                query["status"] = "Fully Paid"
            else:
                query["status"] = status_filter
        
        return list(database.db['loans'].find(query))

    def update_treeview(self, loan_list):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for loan in loan_list:
            full_id = str(loan.get('_id', ''))
            status = loan.get('status', 'Unknown')
            data = (full_id[-4:], loan.get('customer_name', 'N/A'), 
                    f"RWF {loan.get('loan_amount', 0.00):,.2f}", 
                    loan.get('duration', 'N/A'), status, loan.get('next_payment', 'N/A'))
            tag = 'deleted' if loan.get('is_deleted') else status.replace(" ", "").lower()
            self.tree.insert('', tk.END, iid=full_id, values=data, tags=(tag,))

    def filter_loans(self, status=None):
        self.current_filter = status
        loans = self.fetch_loans(status)
        self.update_treeview(loans)
        self.current_status_label.config(text=f"Displaying: {status if status else 'All Loans'}")

    def delete_loan(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        loan_data = database.get_loan_by_id(loan_id)
        new_state = not loan_data.get("is_deleted", False)
        database.db['loans'].update_one({"_id": ObjectId(loan_id)}, {"$set": {"is_deleted": new_state}})
        self.filter_loans(self.current_filter)

    def reject_loan(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        database.update_loan_status(loan_id, "Rejected")
        self.filter_loans(self.current_filter)

    def search_loans(self):
        term = self.search_entry.get().lower()
        all_l = self.fetch_loans(None)
        filtered = [l for l in all_l if term in l.get("customer_name", "").lower()]
        self.update_treeview(filtered)

    def view_loan_details(self):
        loan_id = self.tree.focus()
        if loan_id and LoanDetailsViewer:
            detail_window = tk.Toplevel(self.controller)
            LoanDetailsViewer(detail_window, loan_id, lambda: [detail_window.destroy(), self.filter_loans(None)])

    def record_repayment(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        loan_data = database.get_loan_by_id(loan_id)
        try:
            from repayment import RepaymentWindow
            RepaymentWindow(self, loan_data, self.filter_loans)
        except Exception as e:
            messagebox.showerror("Error", f"Repayment module error: {e}")

if __name__ == "__main__":
    app = LoanApp()
    app.mainloop()