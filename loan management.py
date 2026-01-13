import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database  # MongoDB connection
import subprocess
import sys
import os
import pandas as pd 
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# --- SESSION PERSISTENCE ---
try:
    CURRENT_USER_ROLE = sys.argv[1]
    CURRENT_USER_NAME = sys.argv[2]
except IndexError:
    CURRENT_USER_ROLE = "Staff"
    CURRENT_USER_NAME = "Guest"

# relativedelta is best for accurate month jumps (e.g., Jan 31 to Feb 28)
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
        # Geometry optimized for 15.4 inch laptop (High Resolution)
        self.geometry("1500x850") 
        self.config(bg="#ecf0f1")
        
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
            subprocess.Popen([sys.executable, "loan application.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open loan application: {str(e)}")

    def back_to_dashboard_file(self):
        try:
            subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
            self.destroy() 
        except Exception as e:
            messagebox.showerror("Navigation Error", f"Failed to return to dashboard: {e}")

    def logout_system(self):
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
        tk.Button(sidebar, text="⚠️ Overdue Loans", font=("Arial", 10, "bold"), bg="#e74c3c", fg="white", width=20, command=lambda: self.filter_loans("Overdue")).pack(pady=3)
        tk.Button(sidebar, text="Pending/New", font=("Arial", 10), bg="#f1c40f", width=20, command=lambda: self.filter_loans("Pending")).pack(pady=3)
        tk.Button(sidebar, text="Under Payment", font=("Arial", 10), bg="#3498db", fg="white", width=20, command=lambda: self.filter_loans("Active")).pack(pady=3)
        tk.Button(sidebar, text="Fully Paid", font=("Arial", 10), bg="#2ecc71", fg="white", width=20, command=lambda: self.filter_loans("Closed")).pack(pady=3)
        tk.Button(sidebar, text="Rejected Loans", font=("Arial", 10), bg="#7f8c8d", fg="white", width=20, command=lambda: self.filter_loans("Rejected")).pack(pady=3)
        
        tk.Button(sidebar, text="♻️ Recycle Bin", font=("Arial", 10, "italic"), bg="#bdc3c7", width=20, command=lambda: self.filter_loans("Recycle")).pack(pady=(20, 3))

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

        # Added Next Payment Date and Days Remaining Columns
        columns = ('#id', 'customer_name', 'loan_amount', 'duration', 'status', 'next_payment', 'days_remaining')
        self.tree = ttk.Treeview(main_content_frame, columns=columns, show='headings')

        self.tree.heading('#id', text='ID')
        self.tree.heading('customer_name', text='Customer Full Name')
        self.tree.heading('loan_amount', text='Loan Amount')
        self.tree.heading('duration', text='Term Duration')
        self.tree.heading('status', text='Status')
        self.tree.heading('next_payment', text='Next Payment Date')
        self.tree.heading('days_remaining', text='Days Remaining')

        self.tree.column('#id', width=60, anchor='center')
        self.tree.column('customer_name', width=250)
        self.tree.column('loan_amount', width=130, anchor='e')
        self.tree.column('duration', width=100, anchor='center')
        self.tree.column('status', width=120, anchor='center')
        self.tree.column('next_payment', width=140, anchor='center')
        self.tree.column('days_remaining', width=140, anchor='center')

        # Status Tags
        self.tree.tag_configure('overdue', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('pending', background='#fcf8e3', foreground='#8a6d3b')
        self.tree.tag_configure('approved', background='#fae8ff', foreground='#9c27b0')
        self.tree.tag_configure('underpayment', background='#d9edf7', foreground='#31708f')
        self.tree.tag_configure('fullypaid', background='#dff0d8', foreground='#3c763d')
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

        tk.Button(action_frame, text="🔍 View/Edit Details", font=("Arial", 10), bg="#3498db", fg="white", padx=15, 
                  command=self.view_loan_details).pack(side=tk.LEFT, padx=5)

        tk.Button(action_frame, text="✅ Approve Loan", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", padx=15, 
                  command=self.approve_loan).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="❌ Reject Loan", font=("Arial", 10), bg="#e67e22", fg="white", padx=15, 
                  command=self.reject_loan).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="🗑️ Delete Loan", font=("Arial", 10), bg="#c0392b", fg="white", padx=15, 
                  command=self.delete_loan).pack(side=tk.LEFT, padx=5)
        
        self.btn_repayment = tk.Button(action_frame, text="💰 Record Repayment", font=("Arial", 10, "bold"), bg="#9b59b6", fg="white", padx=15, 
                  command=self.record_repayment)
        self.btn_repayment.pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📥 Export Excel", font=("Arial", 10, "bold"), bg="#27ae60", fg="white", padx=15,
                  command=self.open_export_options).pack(side=tk.RIGHT, padx=5)

    def approve_loan(self):
        loan_id = self.tree.focus()
        if not loan_id: 
            messagebox.showwarning("Selection", "Please select a loan to approve.")
            return
        
        loan_data = database.get_loan_by_id(loan_id)
        if loan_data.get("is_deleted"): return
        
        # --- LOGIC: SET INITIAL DUE DATE BASED ON PLAN ---
        plan = str(loan_data.get('payment_plan', 'Monthly')).strip().lower()
        today = datetime.now()
        
        if "weekly" in plan:
            next_due = today + timedelta(days=7)
        else:
            # Defaults to Monthly
            if relativedelta:
                next_due = today + relativedelta(months=1)
            else:
                next_due = today + timedelta(days=30)
        
        next_due_str = next_due.strftime("%Y-%m-%d")

        # Update database
        database.update_loan_status(loan_id, "Approved")
        database.db['loans'].update_one(
            {"_id": ObjectId(loan_id)}, 
            {"$set": {"next_payment": next_due_str}}
        )
        
        messagebox.showinfo("Success", f"Loan Approved!\nPayment Plan: {plan.title()}\nNext Due Date: {next_due_str}")
        self.filter_loans(self.current_filter)

    def update_treeview(self, loan_list):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        today = datetime.now().date()

        for loan in loan_list:
            full_id = str(loan.get('_id', ''))
            status = loan.get('status', 'Unknown')
            next_pay_str = loan.get('next_payment', 'To be set')
            
            # --- REAL-TIME DAYS REMAINING CALCULATION ---
            days_txt = "N/A"
            tag = status.replace(" ", "").lower()
            
            if status in ["Approved", "Under Payment"] and next_pay_str not in ["To be set", "N/A", ""]:
                try:
                    due_date = datetime.strptime(next_pay_str, "%Y-%m-%d").date()
                    delta = (due_date - today).days
                    
                    if delta > 0:
                        days_txt = f"{delta} Days left"
                    elif delta == 0:
                        days_txt = "Due Today"
                    else:
                        days_txt = f"{abs(delta)} Days Overdue"
                        tag = "overdue" # Override tag for overdue
                except Exception as e:
                    days_txt = "Error"
            elif status == "Fully Paid":
                days_txt = "Completed"
                next_pay_str = "None"
            
            if loan.get('is_deleted'): tag = 'deleted'

            data = (
                full_id[-4:], 
                loan.get('customer_name', 'N/A'), 
                f"RWF {loan.get('loan_amount', 0.00):,.2f}", 
                loan.get('duration', 'N/A'), 
                status, 
                next_pay_str, 
                days_txt
            )
            
            self.tree.insert('', tk.END, iid=full_id, values=data, tags=(tag,))

    def filter_loans(self, status=None):
        self.current_filter = status
        loans = self.fetch_loans(status)
        self.update_treeview(loans)
        self.current_status_label.config(text=f"Displaying: {status if status else 'All Loans'}")

    def fetch_loans(self, status_filter=None):
        query = {"is_deleted": True} if status_filter == "Recycle" else {"is_deleted": {"$ne": True}}
        if status_filter and status_filter not in ["Recycle", "Overdue"]:
            if status_filter == "Active": query["status"] = {"$in": ["Under Payment", "Approved"]}
            elif status_filter == "Closed": query["status"] = "Fully Paid"
            else: query["status"] = status_filter
        
        loans = list(database.db['loans'].find(query))
        
        # Post-fetch filter for Overdue (since it's calculated)
        if status_filter == "Overdue":
            today = datetime.now().date()
            overdue_list = []
            for l in loans:
                dp = l.get('next_payment', '')
                if dp and dp not in ["To be set", "N/A"] and l.get('status') != "Fully Paid":
                    if datetime.strptime(dp, "%Y-%m-%d").date() < today:
                        overdue_list.append(l)
            return overdue_list
            
        return loans

    def search_loans(self):
        term = self.search_entry.get().lower()
        all_l = self.fetch_loans(None)
        filtered = [l for l in all_l if term in l.get("customer_name", "").lower()]
        self.update_treeview(filtered)

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

    def view_loan_details(self):
        loan_id = self.tree.focus()
        if loan_id and LoanDetailsViewer:
            detail_window = tk.Toplevel(self.controller)
            LoanDetailsViewer(detail_window, loan_id, lambda: [detail_window.destroy(), self.filter_loans(self.current_filter)])

    def record_repayment(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        loan_data = database.get_loan_by_id(loan_id)
        try:
            from repayment import RepaymentWindow
            # Passing filter_loans as callback so dashboard refreshes and recalculates dates after payment
            RepaymentWindow(self, loan_data, lambda: self.filter_loans(self.current_filter))
        except Exception as e:
            messagebox.showerror("Error", f"Repayment module error: {e}")

    def open_export_options(self):
        self.export_win = tk.Toplevel(self)
        self.export_win.title("Export Range Selection")
        self.export_win.geometry("400x320")
        self.export_win.configure(bg="white")
        self.export_win.grab_set()
        # ... (rest of export logic remains the same)
        tk.Label(self.export_win, text="EXCEL EXPORT", font=("Arial", 14, "bold"), bg="white", fg="#27ae60").pack(pady=10)
        tk.Label(self.export_win, text="Start Date (YYYY-MM-DD):", bg="white").pack(pady=(15, 0))
        self.start_date_ent = tk.Entry(self.export_win, font=("Arial", 12), justify="center")
        self.start_date_ent.insert(0, datetime.now().strftime("%Y-01-01"))
        self.start_date_ent.pack(pady=5)
        tk.Label(self.export_win, text="End Date (YYYY-MM-DD):", bg="white").pack(pady=(5, 0))
        self.end_date_ent = tk.Entry(self.export_win, font=("Arial", 12), justify="center")
        self.end_date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_ent.pack(pady=5)
        tk.Button(self.export_win, text="SAVE EXCEL", bg="#2ecc71", fg="white", 
                  font=("Arial", 11, "bold"), width=25, height=2, bd=0, command=self.process_export).pack(pady=20)

    def process_export(self):
        try:
            start_dt = datetime.strptime(self.start_date_ent.get(), "%Y-%m-%d")
            end_dt = datetime.strptime(self.end_date_ent.get(), "%Y-%m-%d").replace(hour=23, minute=59)
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if not file_path: return
            data = list(database.db['loans'].find({"application_date": {"$gte": start_dt, "$lte": end_dt}}))
            pd.DataFrame(data).to_excel(file_path)
            self.export_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = LoanApp()
    app.mainloop()