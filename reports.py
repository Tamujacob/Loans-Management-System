import tkinter as tk
from tkinter import ttk, messagebox
import database
import sys
import subprocess
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- SESSION PERSISTENCE ---
# This ensures the window knows WHO is logged in based on arguments passed from login.py
try:
    if len(sys.argv) > 2:
        CURRENT_USER_ROLE = sys.argv[1]
        CURRENT_USER_NAME = sys.argv[2]
    else:
        # Fallback if launched directly for testing
        CURRENT_USER_ROLE = "Admin"
        CURRENT_USER_NAME = "Jacob"
except IndexError:
    CURRENT_USER_ROLE = "Admin"
    CURRENT_USER_NAME = "Jacob"

class ReportsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Financial Reports & Analytics - {CURRENT_USER_NAME} ({CURRENT_USER_ROLE})")
        self.geometry("1250x850")
        self.config(bg="#f1f2f6")

        self.colors = {
            "primary": "#2c3e50",
            "accent": "#16a085",
            "secondary": "#3498db",
            "danger": "#e74c3c",
            "bg": "#f1f2f6",
            "card": "#ffffff"
        }

        # Main Layout Container
        self.main_container = tk.Frame(self, bg=self.colors["bg"])
        self.main_container.pack(fill="both", expand=True)

        self.create_header()
        
        # Scrollable area for the report content
        self.content_canvas = tk.Canvas(self.main_container, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.content_canvas.yview)
        self.scrollable_frame = tk.Frame(self.content_canvas, bg=self.colors["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )

        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=1230)
        self.content_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Load dynamic data and build UI
        self.refresh_data()

    def create_header(self):
        header = tk.Frame(self.main_container, bg=self.colors["primary"], height=70)
        header.pack(fill="x")
        
        tk.Label(header, text=f"SYSTEM ANALYTICS & FINANCIAL REPORTS", 
                 font=("Segoe UI", 18, "bold"), 
                 bg=self.colors["primary"], fg="white", pady=15).pack(side="left", padx=20)
        
        tk.Label(header, text=f"Active User: {CURRENT_USER_NAME} | Role: {CURRENT_USER_ROLE}", 
                 font=("Segoe UI", 10), bg=self.colors["primary"], fg="#bdc3c7").pack(side="right", padx=20)

    def refresh_data(self):
        """Fetches REAL data from the database and updates UI"""
        try:
            # 1. Fetch Real Database Data
            self.loans = list(database.db['loans'].find())
            self.payments = list(database.db['payments'].find())
            
            # Calculations
            self.total_lent = sum(float(l.get('loan_amount', 0)) for l in self.loans)
            self.total_collected = sum(float(p.get('payment_amount', 0)) for p in self.payments)
            self.active_count = len([l for l in self.loans if l.get('status') not in ['Fully Paid', 'Rejected']])
            
            # Build sections
            self.create_summary_cards()
            self.create_charts_area()
            self.create_action_buttons()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch real-time data: {e}")

    def create_summary_cards(self):
        card_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg"])
        card_frame.pack(fill="x", padx=20, pady=20)

        self._build_card(card_frame, "TOTAL PRINCIPAL LENT", f"RWF {self.total_lent:,.0f}", 0)
        self._build_card(card_frame, "TOTAL RECOVERED", f"RWF {self.total_collected:,.0f}", 1)
        self._build_card(card_frame, "ACTIVE LOAN FILES", str(self.active_count), 2)

    def _build_card(self, parent, title, value, col):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#dcdde1", padx=20, pady=15)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 20, "bold"), bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(5,0))

    def create_charts_area(self):
        chart_container = tk.Frame(self.scrollable_frame, bg=self.colors["bg"])
        chart_container.pack(fill="x", padx=20, pady=10)
        
        # --- Chart 1: Status (Pie) ---
        statuses = [l.get('status', 'Pending') for l in self.loans]
        status_counts = {s: statuses.count(s) for s in set(statuses)}

        fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=90)
        if status_counts:
            ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', 
                    startangle=140, colors=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'])
            ax1.set_title("Loan Status Distribution")
        
        canvas1 = FigureCanvasTkAgg(fig1, master=chart_container)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

        # --- Chart 2: Capital Recovery (Bar) ---
        fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=90)
        categories = ['Principal', 'Recovered', 'Outstanding']
        values = [self.total_lent, self.total_collected, max(0, self.total_lent - self.total_collected)]
        
        ax2.bar(categories, values, color=['#2c3e50', '#27ae60', '#e74c3c'])
        ax2.set_title("Capital Recovery Overview")
        
        canvas2 = FigureCanvasTkAgg(fig2, master=chart_container)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)

    def create_action_buttons(self):
        btn_frame = tk.Frame(self.scrollable_frame, bg="white", pady=30)
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Button(btn_frame, text="← BACK TO DASHBOARD", font=("Segoe UI", 10, "bold"), 
                  bg="#95a5a6", fg="white", relief="flat", padx=25, pady=10,
                  command=self.go_back, cursor="hand2").pack(side="left", padx=20)

        tk.Button(btn_frame, text="📥 DOWNLOAD PDF REPORT", 
                  font=("Segoe UI", 10, "bold"), bg=self.colors["accent"], 
                  fg="white", padx=25, pady=10, relief="flat", cursor="hand2",
                  command=self.export_to_pdf).pack(side="right", padx=20)

    def go_back(self):
        try:
            # Check if dashboard.py exists, otherwise it will error
            subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to dashboard: {e}")

    def export_to_pdf(self):
        try:
            filename = f"Loan_Report_{datetime.date.today()}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            c.setFont("Helvetica-Bold", 22)
            c.drawString(50, 750, "BIG ON GOLD LOANS - FINANCIAL REPORT")
            c.setFont("Helvetica", 10)
            c.drawString(50, 730, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            c.drawString(50, 715, f"Admin: {CURRENT_USER_NAME}")
            c.line(50, 705, 550, 705)

            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 680, "EXECUTIVE SUMMARY")
            c.setFont("Helvetica", 12)
            c.drawString(70, 660, f"Total Lent: RWF {self.total_lent:,.2f}")
            c.drawString(70, 640, f"Total Recovered: RWF {self.total_collected:,.2f}")
            c.drawString(70, 620, f"Outstanding Risk: RWF {max(0, self.total_lent - self.total_collected):,.2f}")

            c.save()
            messagebox.showinfo("Export Success", f"Report saved as {filename}")
            os.startfile(filename) if sys.platform == "win32" else subprocess.run(["open", filename])
        except Exception as e:
            messagebox.showerror("Export Error", f"PDF Failed: {e}")

if __name__ == "__main__":
    app = ReportsWindow()
    app.mainloop()