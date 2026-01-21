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
from PIL import Image, ImageTk  # Ensure you have Pillow installed: pip install Pillow

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
        self.title(f"BIG ON GOLD - Analytics & Logs - {CURRENT_USER_NAME}")
        self.geometry("1250x850")
        self.config(bg="#f4f7f6")

        # --- WINDOW ICON SETUP (REPLACES THE LEAF) ---
        try:
            self.icon_img = Image.open("bu logo.png")
            self.icon_photo = ImageTk.PhotoImage(self.icon_img)
            self.iconphoto(False, self.icon_photo)
        except Exception as e:
            print(f"Window icon could not be loaded: {e}")

        # --- COMPANY COLOR PALETTE ---
        self.colors = {
            "primary": "#2ecc71",   # Your Company Green
            "dark_green": "#27ae60", # Darker Green for status bars
            "dark": "#2c3e50",      # Navy for text/headers
            "bg": "#f4f7f6",        # Light grey background
            "white": "#ffffff",
            "accent": "#3498db"     # Blue for User Management feel
        }

        self.create_header()
        
        # --- TABBED INTERFACE SETUP ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', self.colors["primary"])], 
                  foreground=[('selected', 'white')])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: Financial Overview
        self.tab_finance = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_finance, text="  📊  FINANCIAL ANALYTICS  ")

        # Tab 2: User Activities (Audit Logs)
        self.tab_audit = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_audit, text="  🔑  USER ACTIVITY LOGS  ")

        self.setup_finance_tab()
        self.setup_audit_tab()
        self.create_bottom_controls()

    def create_header(self):
        """Header with Logo and Company Branding"""
        header = tk.Frame(self, bg=self.colors["primary"], height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo Integration in Header
        try:
            logo_img = Image.open("bu logo.png")
            logo_img = logo_img.resize((60, 60), Image.LANCZOS)
            self.header_logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header, image=self.header_logo_photo, bg=self.colors["primary"])
            logo_label.pack(side="left", padx=(30, 10))
        except Exception:
            tk.Label(header, text="💰", font=("Segoe UI", 30), bg=self.colors["primary"], fg="white").pack(side="left", padx=30)

        title_frame = tk.Frame(header, bg=self.colors["primary"])
        title_frame.pack(side="left", pady=15)
        
        tk.Label(title_frame, text="BIG ON GOLD LOANS", font=("Segoe UI", 22, "bold"), 
                 bg=self.colors["primary"], fg="white").pack(anchor="w")
        tk.Label(title_frame, text="SYSTEM REPORTS & AUDIT TRAIL", font=("Segoe UI", 10, "bold"), 
                 bg=self.colors["primary"], fg="#e8f8f0").pack(anchor="w")

        # User Info
        user_info = tk.Frame(header, bg=self.colors["dark_green"], padx=15, pady=5)
        user_info.pack(side="right", padx=30)
        tk.Label(user_info, text=f"👤 {CURRENT_USER_NAME} ({CURRENT_USER_ROLE})", 
                 font=("Segoe UI", 10, "bold"), bg=self.colors["dark_green"], fg="white").pack()

    def setup_finance_tab(self):
        """Financial Summary with Cards and Charts"""
        try:
            loans = list(database.db['loans'].find())
            payments = list(database.db['payments'].find())
            total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
            total_rec = sum(float(p.get('payment_amount', 0)) for p in payments)
            active_count = len([l for l in loans if l.get('status') not in ['Fully Paid', 'Rejected']])
        except:
            total_lent, total_rec, active_count, loans = 0, 0, 0, []

        card_frame = tk.Frame(self.tab_finance, bg=self.colors["bg"])
        card_frame.pack(fill="x", pady=20, padx=10)
        
        self._build_card(card_frame, "TOTAL CAPITAL DISBURSED", f"RWF {total_lent:,.0f}", 0)
        self._build_card(card_frame, "TOTAL REVENUE RECOVERED", f"RWF {total_rec:,.0f}", 1)
        self._build_card(card_frame, "TOTAL ACTIVE LOAN FILES", str(active_count), 2)

        chart_container = tk.Frame(self.tab_finance, bg="white", highlightthickness=1, highlightbackground="#dcdde1")
        chart_container.pack(fill="both", expand=True, padx=20, pady=10)

        fig1, ax1 = plt.subplots(figsize=(4.5, 3.5), dpi=95)
        statuses = [l.get('status', 'Pending') for l in loans]
        status_counts = {s: statuses.count(s) for s in set(statuses)}
        if status_counts:
            ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', 
                    startangle=140, colors=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'])
            ax1.set_title("Loan Status Breakdown", fontdict={'weight':'bold'})

        canvas1 = FigureCanvasTkAgg(fig1, master=chart_container)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)

        fig2, ax2 = plt.subplots(figsize=(4.5, 3.5), dpi=95)
        ax2.bar(['Disbursed', 'Recovered'], [total_lent, total_rec], color=[self.colors["dark"], self.colors["primary"]])
        ax2.set_title("Capital Recovery Health", fontdict={'weight':'bold'})
        
        canvas2 = FigureCanvasTkAgg(fig2, master=chart_container)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=20, pady=20)

    def setup_audit_tab(self):
        """User Activity Logs Table"""
        tree_frame = tk.Frame(self.tab_audit, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("Time", "User", "Action", "Details")
        self.audit_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        tree_style = ttk.Style()
        tree_style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        
        for col in columns: 
            self.audit_tree.heading(col, text=col)
            self.audit_tree.column(col, width=150)
        
        try:
            logs = list(database.db['logs'].find().sort("timestamp", -1).limit(100))
            for log in logs:
                self.audit_tree.insert("", "end", values=(
                    log.get('timestamp', 'N/A'), 
                    log.get('user', 'N/A'), 
                    log.get('action', 'N/A'), 
                    log.get('details', 'N/A')
                ))
        except:
            self.audit_tree.insert("", "end", values=("N/A", "System", "No Logs", "Connect 'logs' collection"))

        self.audit_tree.pack(fill="both", expand=True)

    def _build_card(self, parent, title, value, col):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#dcdde1", padx=20, pady=15)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(5,0))

    def create_bottom_controls(self):
        """Navigation and Export Buttons"""
        ctrl_frame = tk.Frame(self, bg=self.colors["white"], pady=20, highlightthickness=1, highlightbackground="#dcdde1")
        ctrl_frame.pack(fill="x", side="bottom")
        
        tk.Button(ctrl_frame, text="⬅  BACK TO DASHBOARD", font=("Segoe UI", 10, "bold"), 
                  command=self.go_back, bg=self.colors["dark"], fg="white", 
                  relief="flat", width=25, height=2, cursor="hand2").pack(side="left", padx=40)

        tk.Button(ctrl_frame, text="📥  EXPORT FULL SYSTEM REPORT (PDF)", font=("Segoe UI", 10, "bold"), 
                  command=self.export_to_pdf, bg=self.colors["primary"], fg="white", 
                  relief="flat", width=35, height=2, cursor="hand2").pack(side="right", padx=40)

    def go_back(self):
        subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
        self.destroy()

    def export_to_pdf(self):
        """Save Report with File Dialog"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfilename=f"BIG_ON_GOLD_Report_{datetime.date.today()}"
        )
        if not file_path: return

        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 20)
            c.setFillColorRGB(0.18, 0.8, 0.44) 
            c.drawString(50, 750, "BIG ON GOLD LOANS - MASTER REPORT")
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0,0,0)
            c.drawString(50, 730, f"System User: {CURRENT_USER_NAME} | Date Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.line(50, 705, 550, 705)

            loans = list(database.db['loans'].find())
            total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 680, "1. FINANCIAL OVERVIEW")
            c.setFont("Helvetica", 12)
            c.drawString(70, 660, f"Total Disbursed: RWF {total_lent:,.2f}")

            c.save()
            messagebox.showinfo("Success", f"Report saved successfully at:\n{file_path}")
            if sys.platform == "win32": os.startfile(file_path)
            else: subprocess.run(["open", file_path] if sys.platform == "darwin" else ["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF: {e}")

if __name__ == "__main__":
    app = ReportsWindow()
    app.mainloop()