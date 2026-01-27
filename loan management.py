import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import database  # MongoDB connection
import subprocess
import sys
import os
import pandas as pd 
import bcrypt  # For secure password verification
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# --- SESSION PERSISTENCE ---
try:
    CURRENT_USER_ROLE = sys.argv[1]
    CURRENT_USER_NAME = sys.argv[2]
except IndexError:
    CURRENT_USER_ROLE = "Staff"
    CURRENT_USER_NAME = "Guest"

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
        self.geometry("1550x850") 
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
                # Log the logout action
                database.log_activity(CURRENT_USER_NAME, "Logout", "User signed out of the system")
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

        columns = ('#id', 'customer_name', 'loan_amount', 'duration', 'status', 'next_payment', 'days_remaining', 'final_due_date')
        self.tree = ttk.Treeview(main_content_frame, columns=columns, show='headings')

        self.tree.heading('#id', text='ID')
        self.tree.heading('customer_name', text='Customer Name')
        self.tree.heading('loan_amount', text='Loan Amount')
        self.tree.heading('duration', text='Term')
        self.tree.heading('status', text='Status')
        self.tree.heading('next_payment', text='Next Payment')
        self.tree.heading('days_remaining', text='Days Left')
        self.tree.heading('final_due_date', text='Loan Completion Date')

        self.tree.column('#id', width=50, anchor='center')
        self.tree.column('customer_name', width=200)
        self.tree.column('loan_amount', width=120, anchor='e')
        self.tree.column('duration', width=80, anchor='center')
        self.tree.column('status', width=100, anchor='center')
        self.tree.column('next_payment', width=110, anchor='center')
        self.tree.column('days_remaining', width=110, anchor='center')
        self.tree.column('final_due_date', width=140, anchor='center')

        self.tree.tag_configure('overdue', background='#f8d7da', foreground='#721c24')
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

        if CURRENT_USER_ROLE == "Admin":
            tk.Button(action_frame, text="🧨 PERMANENT DELETE", font=("Arial", 10, "bold"), 
                      bg="black", fg="white", padx=10, 
                      command=self.permanently_delete_loan).pack(side=tk.LEFT, padx=5)
        
        self.btn_repayment = tk.Button(action_frame, text="💰 Record Repayment", font=("Arial", 10), bg="#9b59b6", fg="white", padx=10, 
                  command=self.record_repayment)
        self.btn_repayment.pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📥 Export Excel", font=("Arial", 10, "bold"), bg="#27ae60", fg="white", padx=10,
                  command=self.open_export_options).pack(side=tk.RIGHT, padx=5)

    def permanently_delete_loan(self):
        loan_id = self.tree.focus()
        if not loan_id:
            messagebox.showwarning("Selection Required", "Please select a loan record to delete forever.")
            return

        pwd = simpledialog.askstring("Security Verification", "Enter your Login Password to confirm permanent deletion:", show='*')
        if pwd:
            try:
                user_doc = database.db['users'].find_one({"full_name": CURRENT_USER_NAME})
                if not user_doc:
                    user_doc = database.db['users'].find_one({"username": CURRENT_USER_NAME})

                if user_doc:
                    stored_hash = user_doc.get('password_hash', '').encode('utf-8')
                    if bcrypt.checkpw(pwd.encode('utf-8'), stored_hash):
                        loan_data = database.get_loan_by_id(loan_id)
                        name = loan_data.get("customer_name", "Unknown")
                        confirm = messagebox.askyesno("Final Confirmation", f"Are you sure you want to PERMANENTLY delete the loan for {name}?")
                        if confirm:
                            database.db['loans'].delete_one({"_id": ObjectId(loan_id)})
                            # LOG THE ACTIVITY
                            database.log_activity(CURRENT_USER_NAME, "Permanent Delete", f"Wiped loan record for {name} (ID: {loan_id})")
                            messagebox.showinfo("Deleted", "Record wiped from database.")
                            self.filter_loans(self.current_filter)
                    else:
                        messagebox.showerror("Access Denied", "Invalid Password.")
                else:
                    messagebox.showerror("Error", "User record not found.")
            except Exception as e:
                messagebox.showerror("Error", f"Verification error: {e}")

    def approve_loan(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        loan_data = database.get_loan_by_id(loan_id)
        if loan_data.get("is_deleted"): return
        
        plan = str(loan_data.get('payment_plan', 'Monthly')).lower()
        duration_val = 1
        try:
            duration_val = int(''.join(filter(str.isdigit, str(loan_data.get('duration', '1')))))
        except: duration_val = 1

        today = datetime.now()
        if "weekly" in plan:
            next_due = today + timedelta(days=7)
        else:
            next_due = (today + relativedelta(months=1)) if relativedelta else (today + timedelta(days=30))
            
        if relativedelta:
            final_due = today + relativedelta(months=duration_val)
        else:
            final_due = today + timedelta(days=30 * duration_val)

        database.update_loan_status(loan_id, "Approved")
        database.db['loans'].update_one({"_id": ObjectId(loan_id)}, {
            "$set": {
                "next_payment": next_due.strftime("%Y-%m-%d"),
                "final_completion_date": final_due.strftime("%Y-%m-%d")
            }
        })
        
        # LOG THE ACTIVITY
        database.log_activity(CURRENT_USER_NAME, "Approve Loan", f"Approved loan for {loan_data.get('customer_name')}")
        
        messagebox.showinfo("Approved", f"Loan Approved!\nNext Pay: {next_due.strftime('%Y-%m-%d')}")
        self.filter_loans(self.current_filter)

    def update_treeview(self, loan_list):
        for i in self.tree.get_children(): self.tree.delete(i)
        today = datetime.now().date()
        for loan in loan_list:
            full_id = str(loan.get('_id', ''))
            status = loan.get('status', 'Unknown')
            next_pay_str = loan.get('next_payment', 'N/A')
            final_due_str = loan.get('final_completion_date', 'N/A')
            days_txt = "N/A"
            tag = status.replace(" ", "").lower()
            
            if status not in ["Fully Paid", "Rejected", "Pending"] and next_pay_str != "N/A":
                try:
                    due_date = datetime.strptime(next_pay_str, "%Y-%m-%d").date()
                    diff = (due_date - today).days
                    if diff > 0: days_txt = f"{diff} Days left"
                    elif diff == 0: days_txt = "Due Today"
                    else: 
                        days_txt = f"{abs(diff)} Days Overdue"
                        tag = 'overdue'
                except: days_txt = "Error"
            
            if loan.get('is_deleted'): tag = 'deleted'
            data = (full_id[-4:], loan.get('customer_name', 'N/A'), f"RWF {loan.get('loan_amount', 0.00):,.2f}", 
                    loan.get('duration', 'N/A'), status, next_pay_str, days_txt, final_due_str)
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
        if status_filter == "Overdue":
            today_str = datetime.now().strftime("%Y-%m-%d")
            loans = [l for l in loans if l.get('next_payment', 'N/A') != 'N/A' and l.get('next_payment') < today_str and l.get('status') != "Fully Paid"]
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
        
        # LOG THE ACTIVITY
        action_name = "Move to Recycle" if new_state else "Restore Loan"
        database.log_activity(CURRENT_USER_NAME, action_name, f"Changed deletion state for {loan_data.get('customer_name')}")
        
        self.filter_loans(self.current_filter)

    def reject_loan(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        loan_data = database.get_loan_by_id(loan_id)
        database.update_loan_status(loan_id, "Rejected")
        
        # LOG THE ACTIVITY
        database.log_activity(CURRENT_USER_NAME, "Reject Loan", f"Rejected loan application for {loan_data.get('customer_name')}")
        
        self.filter_loans(self.current_filter)

    # --- UPDATED VIEW DETAILS LOGIC ---
    def view_loan_details(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        try:
            # Launch view_loan_details script as a new process
            subprocess.Popen([sys.executable, "view_loan_details.py", loan_id, CURRENT_USER_ROLE, CURRENT_USER_NAME])
            # Kill the current Management window
            self.controller.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch loan details: {e}")

    # --- UPDATED RECORD REPAYMENT LOGIC ---
    def record_repayment(self):
        loan_id = self.tree.focus()
        if not loan_id: return
        try:
            # Launch repayment script as a new process
            subprocess.Popen([sys.executable, "repayment.py", loan_id, CURRENT_USER_ROLE, CURRENT_USER_NAME])
            # Kill the current Management window
            self.controller.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch repayment: {e}")

    def open_export_options(self):
        self.export_win = tk.Toplevel(self)
        self.export_win.title("Export Range Selection")
        self.export_win.geometry("400x320")
        self.export_win.configure(bg="white")
        self.export_win.grab_set()
        tk.Label(self.export_win, text="EXCEL EXPORT", font=("Arial", 14, "bold"), bg="white", fg="#27ae60").pack(pady=10)
        tk.Label(self.export_win, text="Start Date (YYYY-MM-DD):", bg="white").pack(pady=(15, 0))
        self.start_date_ent = tk.Entry(self.export_win, font=("Arial", 12), justify="center")
        self.start_date_ent.insert(0, datetime.now().strftime("%Y-01-01"))
        self.start_date_ent.pack(pady=5)
        tk.Label(self.export_win, text="End Date (YYYY-MM-DD):", bg="white").pack(pady=(5, 0))
        self.end_date_ent = tk.Entry(self.export_win, font=("Arial", 12), justify="center")
        self.end_date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_ent.pack(pady=5)
        tk.Button(self.export_win, text="PROCESS EXCEL", bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), width=25, height=2, bd=0, command=self.process_export).pack(pady=20)

    def process_export(self):
        try:
            start_dt = datetime.strptime(self.start_date_ent.get(), "%Y-%m-%d")
            end_dt = datetime.strptime(self.end_date_ent.get(), "%Y-%m-%d").replace(hour=23, minute=59)
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if not file_path: return
            query = {"application_date": {"$gte": start_dt, "$lte": end_dt}}
            data = list(database.db['loans'].find(query))
            for d in data: d['_id'] = str(d['_id'])
            pd.DataFrame(data).to_excel(file_path, index=False)
            
            # LOG THE ACTIVITY
            database.log_activity(CURRENT_USER_NAME, "Export Excel", f"Exported loan report to {os.path.basename(file_path)}")
            
            self.export_win.destroy()
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = LoanApp()
    app.mainloop()