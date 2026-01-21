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
try:
    if len(sys.argv) > 2:
        CURRENT_USER_ROLE = sys.argv[1]
        CURRENT_USER_NAME = sys.argv[2]
    else:
        CURRENT_USER_ROLE = "Admin"
        CURRENT_USER_NAME = "Jacob"
except IndexError:
    CURRENT_USER_ROLE = "Admin"
    CURRENT_USER_NAME = "Jacob"

class ReportsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Financial Reports & Analytics - {CURRENT_USER_NAME}")
        self.geometry("1200x850")
        self.config(bg="#f1f2f6")

        self.colors = {
            "primary": "#2c3e50",
            "accent": "#16a085",
            "secondary": "#3498db",
            "danger": "#e74c3c",
            "bg": "#f1f2f6",
            "card": "#ffffff"
        }

        self.create_header()
        self.create_summary_cards()
        self.create_charts_area()
        self.create_action_buttons()

    def create_header(self):
        """Creates the top branding header"""
        header = tk.Frame(self, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        
        tk.Label(header, text="SYSTEM ANALYTICS & FINANCIAL REPORTS", 
                 font=("Segoe UI", 18, "bold"), 
                 bg=self.colors["primary"], fg="white", pady=20).pack()

    def create_summary_cards(self):
        """Displays high-level KPIs in card format"""
        card_frame = tk.Frame(self, bg=self.colors["bg"])
        card_frame.pack(fill="x", padx=20, pady=20)

        # Fetch Financial Data from MongoDB
        loans = list(database.db['loans'].find())
        payments = list(database.db['payments'].find())
        
        total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
        total_collected = sum(float(p.get('payment_amount', 0)) for p in payments)
        active_loans = len([l for l in loans if l.get('status') not in ['Fully Paid', 'Rejected']])

        # Build UI Cards
        self._build_card(card_frame, "TOTAL PRINCIPAL LENT", f"RWF {total_lent:,.0f}", 0)
        self._build_card(card_frame, "TOTAL RECOVERED", f"RWF {total_collected:,.0f}", 1)
        self._build_card(card_frame, "ACTIVE LOAN FILES", str(active_loans), 2)

    def _build_card(self, parent, title, value, col):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#dcdde1", padx=20, pady=15)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(5,0))

    def create_charts_area(self):
        """Integrates Matplotlib charts into the Tkinter window"""
        chart_container = tk.Frame(self, bg=self.colors["bg"])
        chart_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 1. PIE CHART: Loan Status Distribution
        loans = list(database.db['loans'].find())
        statuses = [l.get('status', 'Pending') for l in loans]
        status_counts = {s: statuses.count(s) for s in set(statuses)}

        fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        if status_counts:
            ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', 
                    startangle=140, colors=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'])
            ax1.set_title("Loan Status Distribution")

        canvas1 = FigureCanvasTkAgg(fig1, master=chart_container)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 2. BAR CHART: Principal vs Recovered
        fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=100)
        total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
        total_rec = sum(float(p.get('payment_amount', 0)) for p in list(database.db['payments'].find()))
        
        categories = ['Principal', 'Recovered', 'Outstanding']
        values = [total_lent, total_rec, max(0, total_lent - total_rec)]
        
        ax2.bar(categories, values, color=['#2c3e50', '#27ae60', '#e74c3c'])
        ax2.set_title("Capital Recovery Overview")
        ax2.set_ylabel("Amount (RWF)")

        canvas2 = FigureCanvasTkAgg(fig2, master=chart_container)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        chart_container.columnconfigure((0, 1), weight=1)

    def create_action_buttons(self):
        """Adds navigation and PDF export buttons"""
        btn_frame = tk.Frame(self, bg=self.colors["bg"], pady=20)
        btn_frame.pack(fill="x", padx=30)
        
        tk.Button(btn_frame, text="← BACK TO DASHBOARD", font=("Segoe UI", 10), 
                  bg="#95a5a6", fg="white", relief="flat", padx=20,
                  command=self.go_back).pack(side="left")

        tk.Button(btn_frame, text="📥 DOWNLOAD PDF REPORT", 
                  font=("Segoe UI", 10, "bold"), bg=self.colors["accent"], 
                  fg="white", padx=20, pady=10, relief="flat", cursor="hand2",
                  command=self.export_to_pdf).pack(side="right")

    def go_back(self):
        try:
            filename = "dashboard.py" # Ensure this matches your dashboard filename
            subprocess.Popen([sys.executable, filename, CURRENT_USER_ROLE, CURRENT_USER_NAME])
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to dashboard: {e}")

    def export_to_pdf(self):
        """Generates and opens a PDF financial report"""
        try:
            loans = list(database.db['loans'].find())
            payments = list(database.db['payments'].find())
            total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
            total_rec = sum(float(p.get('payment_amount', 0)) for p in payments)
            
            filename = f"Loan_Report_{datetime.date.today()}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            # PDF Styling & Header
            c.setFont("Helvetica-Bold", 22)
            c.setStrokeColor("#2c3e50")
            c.drawString(50, 750, "BIG ON GOLD LOANS")
            
            c.setFont("Helvetica", 10)
            c.drawString(50, 735, f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            c.drawString(50, 720, f"System Administrator: {CURRENT_USER_NAME}")
            c.line(50, 710, 550, 710)

            # Executive Summary
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 680, "EXECUTIVE FINANCIAL SUMMARY")
            
            c.setFont("Helvetica", 12)
            c.drawString(70, 655, f"Total Capital Disbursed:    RWF {total_lent:,.2f}")
            c.drawString(70, 635, f"Total Revenue Recovered:    RWF {total_rec:,.2f}")
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, 615, f"Current Net Risk:           RWF {(total_lent - total_rec):,.2f}")

            # Recent Transactions Table
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 570, "RECENT LOAN APPLICATIONS")
            
            # Table Header
            c.setFont("Helvetica-Bold", 10)
            y = 545
            c.drawString(50, y, "Customer Name")
            c.drawString(220, y, "Principal (RWF)")
            c.drawString(350, y, "Status")
            c.drawString(450, y, "Date")
            c.line(50, y-5, 550, y-5)

            # Table Rows (Last 15 entries)
            c.setFont("Helvetica", 9)
            y -= 25
            for loan in loans[-15:]:
                if y < 50: break # Simple page break check
                c.drawString(50, y, str(loan.get('customer_name'))[:25])
                c.drawString(220, y, f"{float(loan.get('loan_amount', 0)):,.0f}")
                c.drawString(350, y, str(loan.get('status')))
                c.drawString(450, y, str(loan.get('application_date', 'N/A')))
                y -= 20

            c.save()
            messagebox.showinfo("Export Success", f"Report generated successfully: {filename}")
            
            # Auto-open the PDF
            if sys.platform == "win32":
                os.startfile(filename)
            else:
                subprocess.run(["open", filename] if sys.platform == "darwin" else ["xdg-open", filename])

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF: {str(e)}")

if __name__ == "__main__":
    app = ReportsWindow()
    app.mainloop()