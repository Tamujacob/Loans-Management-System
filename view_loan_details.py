import tkinter as tk
from tkinter import ttk, messagebox
import sys
import subprocess
from datetime import datetime
from bson.objectid import ObjectId
import os

# --- Import Database Functions ---
# Added log_activity to tracking changes
from database import get_loan_by_id, get_payments_by_loan, get_total_paid_for_loan, db, log_activity

# --- SESSION PERSISTENCE ---
try:
    LOAN_ID_ARG = sys.argv[1]
    CURRENT_USER_ROLE = sys.argv[2]
    CURRENT_USER_NAME = sys.argv[3]
except IndexError:
    # Fallback for manual testing
    LOAN_ID_ARG = None
    CURRENT_USER_ROLE = "Staff"
    CURRENT_USER_NAME = "Guest"

class ViewLoanDetailsPage:
    def __init__(self, master, loan_id):
        self.master = master
        self.loan_id = loan_id
        
        # New State Variables
        self.is_edit_mode = False
        self.edit_entries = {} 

        self.master.title(f"Loan Details - {loan_id}")
        self.master.geometry("1000x700")
        self.master.configure(bg="#f7f9fa")

        # --- ICON UPDATE (Replacing the leaf) ---
        try:
            icon_path = "bu logo.png"
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.master.iconphoto(False, img)
        except Exception as e:
            print(f"Icon could not be loaded: {e}")

        self.frame = ttk.Frame(self.master, padding="20 20 20 5")
        self.frame.pack(fill='both', expand=True)

        # 1. Fetch Data
        self.loan_data = self._fetch_loan_details(self.loan_id)
        
        if not self.loan_data:
            self._show_not_found()
            return
            
        self._refresh_calculations()

        # 2. Build UI
        self._create_styles()
        self._create_header_and_back_button() 
        self._create_summary_panel()
        self._create_notebook()

    def _refresh_calculations(self):
        """Calculates current financial standing based on database data."""
        self.payment_history = self._fetch_payment_history(self.loan_id)
        self.loan_amount = float(self.loan_data.get('loan_amount', 0.00))
        self.total_paid = get_total_paid_for_loan(self.loan_id)
        self.remaining_balance = self.loan_amount - self.total_paid

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure('TFrame', background='#f7f9fa')
        style.configure('Header.TLabel', font=('Arial', 24, 'bold'), foreground='#2c3e50', background='#f7f9fa')
        style.configure('InfoKey.TLabel', font=('Arial', 11, 'bold'), foreground='#555555', background='#ffffff')
        
        style.configure('Dashboard.TButton', font=('Arial', 11, 'bold'), background='#3498db', foreground='white')
        style.map('Dashboard.TButton', background=[('active', '#2980b9')])

        style.configure('Action.TButton', font=('Arial', 11, 'bold'), background='#f39c12', foreground='white')
        style.map('Action.TButton', background=[('active', '#e67e22')])

    def _fetch_loan_details(self, loan_id):
        try:
            return get_loan_by_id(loan_id)
        except:
            return None

    def _fetch_payment_history(self, loan_id):
        return get_payments_by_loan(loan_id)

    def _create_header_and_back_button(self):
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Button(header_frame, text="← Back to Management", 
                   command=self.back_to_management,
                   style='Dashboard.TButton').pack(side=tk.LEFT, padx=(0, 20))
        
        customer_name = self.loan_data.get('customer_name', 'N/A')
        ttk.Label(header_frame, text=f"Loan File: {customer_name}", 
                  style='Header.TLabel').pack(side=tk.LEFT)

        self.edit_toggle_btn = ttk.Button(header_frame, text="✎ Edit Details", 
                                          style='Action.TButton', command=self._toggle_edit_mode)
        self.edit_toggle_btn.pack(side=tk.RIGHT)
        
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=(0, 15))

    def _toggle_edit_mode(self):
        if not self.is_edit_mode:
            self.is_edit_mode = True
            self.edit_toggle_btn.config(text="💾 Save Changes")
        else:
            self._save_loan_updates()
            self.is_edit_mode = False
            self.edit_toggle_btn.config(text="✎ Edit Details")

        self._populate_loan_info_tab(self.loan_info_tab)

    def _save_loan_updates(self):
        try:
            customer_name = self.loan_data.get('customer_name', 'Unknown')
            updated_data = {
                "loan_type": self.edit_entries['loan_type'].get(),
                "loan_amount": float(self.edit_entries['loan_amount'].get()),
                "duration": self.edit_entries['duration'].get(),
                "interest_rate": float(self.edit_entries['interest_rate'].get()),
                "next_payment": self.edit_entries['next_payment'].get()
            }

            db.loans.update_one({"_id": ObjectId(self.loan_id)}, {"$set": updated_data})
            
            # LOG THE ACTIVITY
            log_activity(
                CURRENT_USER_NAME, 
                "Update Loan", 
                f"Updated details for {customer_name}'s loan (ID: {self.loan_id})"
            )
            
            self.loan_data.update(updated_data)
            self._refresh_calculations()
            self._create_summary_panel() 
            
            messagebox.showinfo("Success", "Loan details updated successfully.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for Amount and Interest.")
        except Exception as e:
            messagebox.showerror("System Error", f"Could not update: {e}")

    def _create_summary_panel(self):
        if hasattr(self, 'summary_container'):
            self.summary_container.destroy()

        self.summary_container = ttk.Frame(self.frame, padding="15", relief='groove', borderwidth=1)
        self.summary_container.pack(fill='x', pady=10)
        
        cols = [
            ("Borrowed Amount", f"RWF {self.loan_amount:,.2f}", None),
            ("Total Paid", f"RWF {self.total_paid:,.2f}", "#2ecc71"),
            ("Remaining Balance", f"RWF {self.remaining_balance:,.2f}", "#e74c3c")
        ]

        for i, (title, val, color) in enumerate(cols):
            f = ttk.Frame(self.summary_container)
            f.grid(row=0, column=i, sticky='nsew', padx=20)
            ttk.Label(f, text=title, font=('Arial', 10), foreground='#777', background='#ffffff').pack(anchor='w')
            lbl = ttk.Label(f, text=val, font=('Arial', 16, 'bold'), background='#ffffff')
            if color: lbl.config(foreground=color)
            lbl.pack(anchor='w')
            self.summary_container.columnconfigure(i, weight=1)

    def _create_notebook(self):
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill='both', expand=True, pady=10)

        self.loan_info_tab = ttk.Frame(notebook, padding="15")
        notebook.add(self.loan_info_tab, text="📄 Loan Details")
        self._populate_loan_info_tab(self.loan_info_tab)

        payment_history_tab = ttk.Frame(notebook, padding="15")
        notebook.add(payment_history_tab, text="💳 Payment History")
        self._populate_payment_history_tab(payment_history_tab)

    def _populate_loan_info_tab(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        fields = [
            ("Full Loan ID", "_id", False),
            ("Loan Type", "loan_type", True),
            ("Loan Amount", "loan_amount", True),
            ("Interest Rate (%)", "interest_rate", True),
            ("Duration", "duration", True),
            ("Next Payment Date", "next_payment", True)
        ]

        for i, (label_text, db_key, can_edit) in enumerate(fields):
            ttk.Label(parent_frame, text=f"{label_text}:", style='InfoKey.TLabel').grid(row=i, column=0, sticky='w', padx=10, pady=8)
            
            value = self.loan_data.get(db_key, "N/A")
            
            if self.is_edit_mode and can_edit:
                ent = ttk.Entry(parent_frame, font=('Arial', 11), width=40)
                ent.insert(0, str(value))
                ent.grid(row=i, column=1, sticky='w', padx=10)
                self.edit_entries[db_key] = ent
            else:
                ttk.Label(parent_frame, text=str(value), font=('Arial', 11), background='#ffffff').grid(row=i, column=1, sticky='w', padx=10)

    def _populate_payment_history_tab(self, parent_frame):
        self.payment_tree = ttk.Treeview(parent_frame, columns=('Date', 'Amount', 'Recorded'), show='headings')
        self.payment_tree.heading('Date', text='Payment Date')
        self.payment_tree.heading('Amount', text='Amount Paid (RWF)', anchor='e')
        self.payment_tree.heading('Recorded', text='Record Date/Time')
        
        if self.payment_history:
            for payment in self.payment_history:
                rec_date = payment.get('recorded_date')
                rec_str = rec_date.strftime('%Y-%m-%d %H:%M') if isinstance(rec_date, datetime) else 'N/A'
                self.payment_tree.insert('', 'end', values=(
                    payment.get('payment_date', 'N/A'),
                    f"{payment.get('payment_amount', 0):,.2f}",
                    rec_str
                ))
        self.payment_tree.pack(fill='both', expand=True)

    def _show_not_found(self):
        ttk.Label(self.frame, text="🛑 Loan Not Found", font=('Arial', 14, 'bold'), foreground='red').pack(pady=50)
        ttk.Button(self.frame, text="Back", command=self.back_to_management).pack()

    def back_to_management(self):
        try:
            # Restart the management script
            subprocess.Popen([sys.executable, "loan_management.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
            self.master.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return: {e}")

if __name__ == "__main__":
    if not LOAN_ID_ARG:
        root = tk.Tk()
        messagebox.showerror("Error", "No Loan ID provided.")
        root.destroy()
        sys.exit()

    root = tk.Tk()
    app = ViewLoanDetailsPage(root, LOAN_ID_ARG)
    root.mainloop()