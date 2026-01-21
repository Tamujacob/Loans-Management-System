import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import sys
import subprocess
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# --- SESSION PERSISTENCE ---
try:
    if len(sys.argv) > 2:
        CURRENT_USER_ROLE = sys.argv[1]
        CURRENT_USER_NAME = sys.argv[2]
    else:
        CURRENT_USER_ROLE = "Admin"
        CURRENT_USER_NAME = "Guest"
except IndexError:
    CURRENT_USER_ROLE = "Admin"
    CURRENT_USER_NAME = "Guest"

class ReportsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Financial Analytics & Audit Logs - {CURRENT_USER_NAME}")
        self.geometry("1250x850")
        self.config(bg="#f1f2f6")

        self.colors = {
            "primary": "#2c3e50",
            "accent": "#16a085",
            "bg": "#f1f2f6",
            "white": "#ffffff"
        }

        self.create_header()
        
        # --- TABBED INTERFACE SETUP ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Financial Overview
        self.tab_finance = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_finance, text=" 📊 Financial Analytics ")

        # Tab 2: User Activities (Audit Logs)
        self.tab_audit = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_audit, text=" 🔑 User Activities ")

        self.setup_finance_tab()
        self.setup_audit_tab()
        self.create_bottom_controls()

    def create_header(self):
        header = tk.Frame(self, bg=self.colors["primary"], height=60)
        header.pack(fill="x")
        tk.Label(header, text="SYSTEM REPORTS & ACTIVITY LOGS", font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["primary"], fg="white", pady=15).pack(side="left", padx=20)
        tk.Label(header, text=f"User: {CURRENT_USER_NAME}", font=("Segoe UI", 10), 
                 bg=self.colors["primary"], fg="#bdc3c7").pack(side="right", padx=20)

    def setup_finance_tab(self):
        # Fetch Real Data
        loans = list(database.db['loans'].find())
        payments = list(database.db['payments'].find())
        total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
        total_rec = sum(float(p.get('payment_amount', 0)) for p in payments)

        # Summary Cards
        card_frame = tk.Frame(self.tab_finance, bg=self.colors["bg"])
        card_frame.pack(fill="x", pady=10)
        self._build_card(card_frame, "TOTAL DISBURSED", f"RWF {total_lent:,.0f}", 0)
        self._build_card(card_frame, "TOTAL RECOVERED", f"RWF {total_rec:,.0f}", 1)

        # Charts Area
        chart_frame = tk.Frame(self.tab_finance, bg="white")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Pie Chart (Status)
        statuses = [l.get('status', 'Pending') for l in loans]
        status_counts = {s: statuses.count(s) for s in set(statuses)}
        fig1, ax1 = plt.subplots(figsize=(4, 3), dpi=100)
        ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', startangle=140)
        ax1.set_title("Loan Status Distribution")
        
        canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

        # Bar Chart
        fig2, ax2 = plt.subplots(figsize=(4, 3), dpi=100)
        ax2.bar(['Lent', 'Recovered'], [total_lent, total_rec], color=['#2c3e50', '#16a085'])
        ax2.set_title("Financial Health")
        
        canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)

    def setup_audit_tab(self):
        # Activity Table
        tree_frame = tk.Frame(self.tab_audit, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("Time", "User", "Action", "Details")
        self.audit_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns: self.audit_tree.heading(col, text=col)
        
        # Load Logs (Assuming you have a 'logs' collection)
        try:
            logs = list(database.db['logs'].find().sort("timestamp", -1).limit(50))
            for log in logs:
                self.audit_tree.insert("", "end", values=(log.get('timestamp'), log.get('user'), log.get('action'), log.get('details')))
        except:
            self.audit_tree.insert("", "end", values=("N/A", "System", "No Logs Found", "Create a 'logs' collection in DB"))

        self.audit_tree.pack(fill="both", expand=True)

    def _build_card(self, parent, title, value, col):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#dcdde1", padx=20, pady=15)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg="white", fg=self.colors["primary"]).pack(anchor="w")

    def create_bottom_controls(self):
        ctrl_frame = tk.Frame(self, bg=self.colors["white"], pady=15)
        ctrl_frame.pack(fill="x", side="bottom")
        
        tk.Button(ctrl_frame, text="← BACK TO DASHBOARD", font=("Segoe UI", 10), 
                  command=self.go_back, bg="#95a5a6", fg="white", relief="flat", padx=20).pack(side="left", padx=20)

        tk.Button(ctrl_frame, text="📥 EXPORT FULL PDF REPORT", font=("Segoe UI", 10, "bold"), 
                  command=self.export_to_pdf, bg=self.colors["accent"], fg="white", relief="flat", padx=20).pack(side="right", padx=20)

    def go_back(self):
        subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
        self.destroy()

    def export_to_pdf(self):
        # ASK WHERE TO SAVE
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfilename=f"Full_System_Report_{datetime.date.today()}"
        )
        
        if not file_path:
            return

        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            # PDF Content
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, 750, "BIG ON GOLD LOANS - MASTER REPORT")
            c.setFont("Helvetica", 10)
            c.drawString(50, 730, f"Prepared By: {CURRENT_USER_NAME} | Date: {datetime.datetime.now()}")
            c.line(50, 720, 550, 720)

            # Data Summary
            loans = list(database.db['loans'].find())
            total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 690, "FINANCIAL SUMMARY")
            c.setFont("Helvetica", 11)
            c.drawString(50, 670, f"Total Capital Lent: RWF {total_lent:,.2f}")
            c.drawString(50, 650, f"Total Active Loans: {len(loans)}")

            # User Activity Section
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 610, "RECENT USER ACTIVITIES")
            y = 590
            c.setFont("Helvetica", 9)
            logs = list(database.db['logs'].find().sort("timestamp", -1).limit(10))
            for log in logs:
                c.drawString(50, y, f"[{log.get('timestamp')}] {log.get('user')}: {log.get('action')}")
                y -= 15

            c.save()
            messagebox.showinfo("Success", "Report Exported Successfully!")
            os.startfile(file_path) if sys.platform == "win32" else subprocess.run(["open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"PDF Export Failed: {e}")

if __name__ == "__main__":
    app = ReportsWindow()
    app.mainloop()