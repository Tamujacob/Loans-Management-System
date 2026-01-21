import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import database
import sys
import subprocess
import os
import datetime
import matplotlib
# Use the TkAgg backend explicitly to prevent startup crashes
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from PIL import Image, ImageTk
import io

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
        self.geometry("1250x750")
        self.config(bg="#f4f7f6")

        try:
            self.icon_img = Image.open("bu logo.png")
            self.icon_photo = ImageTk.PhotoImage(self.icon_img)
            self.iconphoto(False, self.icon_photo)
        except Exception:
            pass

        self.colors = {
            "primary": "#2ecc71",
            "dark_green": "#27ae60",
            "dark": "#2c3e50",
            "bg": "#f4f7f6",
            "white": "#ffffff",
            "accent": "#3498db"
        }

        self.create_header()
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', font=('Segoe UI', 9, 'bold'), padding=[15, 5])
        style.map('TNotebook.Tab', background=[('selected', self.colors["primary"])], 
                  foreground=[('selected', 'white')])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=5)

        self.tab_finance = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_finance, text="  📊  FINANCIAL ANALYTICS  ")

        self.tab_audit = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_audit, text="  🔑  USER ACTIVITY LOGS  ")

        self.setup_finance_tab()
        self.setup_audit_tab()
        self.create_bottom_controls()

    def create_header(self):
        header = tk.Frame(self, bg=self.colors["primary"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            logo_img = Image.open("bu logo.png")
            logo_img = logo_img.resize((45, 45), Image.LANCZOS)
            self.header_logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header, image=self.header_logo_photo, bg=self.colors["primary"])
            logo_label.pack(side="left", padx=(20, 10))
        except Exception:
            tk.Label(header, text="💰", font=("Segoe UI", 20), bg=self.colors["primary"], fg="white").pack(side="left", padx=20)

        title_frame = tk.Frame(header, bg=self.colors["primary"])
        title_frame.pack(side="left", pady=5)
        
        tk.Label(title_frame, text="BIG ON GOLD LOANS", font=("Segoe UI", 16, "bold"), 
                  bg=self.colors["primary"], fg="white").pack(anchor="w")

    def _get_filtered_data(self, start_date=None):
        try:
            query = {}
            if start_date:
                query = {"date": {"$regex": f"^{start_date}"}}
            
            loans = list(database.db['loans'].find(query))
            payments = list(database.db['payments'].find()) 
            
            total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
            total_rec = sum(float(p.get('payment_amount', 0)) for p in payments if any(str(l['_id']) == str(p.get('loan_id')) for l in loans))
            debt = total_lent - total_rec
            active_count = len([l for l in loans if l.get('status') not in ['Fully Paid', 'Rejected']])
            
            return total_lent, total_rec, debt, active_count, loans
        except Exception:
            return 0, 0, 0, 0, []

    def setup_finance_tab(self):
        filter_frame = tk.Frame(self.tab_finance, bg=self.colors["bg"])
        filter_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(filter_frame, text="Whole Business Analysis", command=lambda: self.refresh_finance(None), 
                  bg=self.colors["dark"], fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        
        tk.Button(filter_frame, text="Filter by Date (YYYY-MM-DD)", command=self.ask_date_filter, 
                  bg=self.colors["accent"], fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)

        self.card_container = tk.Frame(self.tab_finance, bg=self.colors["bg"])
        self.card_container.pack(fill="x", padx=10)
        
        self.chart_area = tk.Frame(self.tab_finance, bg="white", highlightthickness=1, highlightbackground="#dcdde1")
        self.chart_area.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.refresh_finance()

    def ask_date_filter(self):
        date_str = simpledialog.askstring("Filter", "Enter date (YYYY-MM-DD):")
        if date_str:
            self.refresh_finance(date_str)

    def refresh_finance(self, date_filter=None):
        for widget in self.card_container.winfo_children(): widget.destroy()
        for widget in self.chart_area.winfo_children(): widget.destroy()

        self.current_data = self._get_filtered_data(date_filter)
        lent, rec, debt, count, loans = self.current_data

        self._build_card(self.card_container, "TOTAL CASH GIVEN OUT", f"RWF {lent:,.0f}", 0)
        self._build_card(self.card_container, "TOTAL RECOVERY", f"RWF {rec:,.0f}", 1)
        self._build_card(self.card_container, "MONEY NOT YET RECOVERED", f"RWF {debt:,.0f}", 2)

        plt.close('all') 
        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3), dpi=90)
        
        statuses = [l.get('status', 'Pending') for l in loans]
        status_counts = {s: statuses.count(s) for s in set(statuses)}
        
        if status_counts:
            ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', colors=['#3498db', '#2ecc71', '#e74c3c'])
        else:
            ax1.text(0.5, 0.5, 'No Data', ha='center')
        ax1.set_title("Status Breakdown")

        ax2.bar(['Given Out', 'Recovered', 'In Debt'], [lent, rec, debt], color=[self.colors["dark"], self.colors["primary"], "#e74c3c"])
        ax2.set_title("Financial Health")

        canvas_plot = FigureCanvasTkAgg(self.fig, master=self.chart_area)
        canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    def setup_audit_tab(self):
        filter_frame = tk.Frame(self.tab_audit, bg=self.colors["bg"])
        filter_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(filter_frame, text="Show All Logs", command=lambda: self.load_logs(None), 
                  bg=self.colors["dark"], fg="white").pack(side="left", padx=5)
        
        tree_frame = tk.Frame(self.tab_audit, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=5)

        columns = ("Time", "User", "Action", "Details")
        self.audit_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        for col in columns: self.audit_tree.heading(col, text=col)
        self.audit_tree.pack(fill="both", expand=True)
        self.load_logs()

    def load_logs(self, date_filter=None):
        for i in self.audit_tree.get_children(): self.audit_tree.delete(i)
        query = {}
        if date_filter: query = {"timestamp": {"$regex": f"^{date_filter}"}}
        try:
            self.logs_data = list(database.db['logs'].find(query).sort("timestamp", -1).limit(100))
            for log in self.logs_data:
                self.audit_tree.insert("", "end", values=(log.get('timestamp'), log.get('user'), log.get('action'), log.get('details')))
        except Exception: pass

    def _build_card(self, parent, title, value, col):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#dcdde1", padx=15, pady=10)
        card.grid(row=0, column=col, padx=5, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 14, "bold"), bg="white", fg=self.colors["dark"]).pack(anchor="w")

    def create_bottom_controls(self):
        ctrl_frame = tk.Frame(self, bg=self.colors["white"], pady=10, highlightthickness=1, highlightbackground="#dcdde1")
        ctrl_frame.pack(fill="x", side="bottom")
        
        tk.Button(ctrl_frame, text="⬅  BACK", command=self.go_back, bg=self.colors["dark"], fg="white", 
                  relief="flat", width=15, height=1).pack(side="left", padx=20)

        tk.Button(ctrl_frame, text="📥  DOWNLOAD PDF", command=self.export_to_pdf, bg=self.colors["primary"], fg="white", 
                  relief="flat", width=20, height=1).pack(side="right", padx=20)

    def go_back(self):
        subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
        self.destroy()

    def export_to_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path: return
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            # 1. Header
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkgreen)
            c.drawString(50, height - 50, "BIG ON GOLD LOANS - ANALYTICS REPORT")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(50, height - 65, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.line(50, height - 75, width - 50, height - 75)

            # 2. Financial Summary Table
            lent, rec, debt, count, _ = self.current_data
            data = [
                ["Description", "Amount (RWF)"],
                ["Total Capital Disbursed", f"{lent:,.0f}"],
                ["Total Revenue Recovered", f"{rec:,.0f}"],
                ["Money Outstanding", f"{debt:,.0f}"],
                ["Active Loan Files", str(count)]
            ]
            t = Table(data, colWidths=[200, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            t.wrapOn(c, width, height)
            t.drawOn(c, 50, height - 180)

            # 3. Capture and Save Matplotlib Chart
            imgdata = io.BytesIO()
            self.fig.savefig(imgdata, format='png', bbox_inches='tight')
            imgdata.seek(0)
            
            # Use drawInlineImage with the PIL object directly to fix the PhotoImage error
            chart_img = Image.open(imgdata)
            c.drawInlineImage(chart_img, 50, height - 480, width=500, height=250)

            # 4. User Audit Logs (New Page)
            c.showPage()
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 50, "USER ACTIVITY LOGS")
            c.line(50, height - 60, width - 50, height - 60)

            log_table_data = [["Timestamp", "User", "Action"]]
            # Safety check for logs_data existence
            logs_to_print = getattr(self, 'logs_data', [])
            for log in logs_to_print[:25]: # Limit to first 25 for space
                log_table_data.append([log.get('timestamp', '')[:19], log.get('user', ''), log.get('action', '')])
            
            lt = Table(log_table_data, colWidths=[120, 100, 300])
            lt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8)
            ]))
            lt.wrapOn(c, width, height)
            lt.drawOn(c, 50, height - (70 + (len(log_table_data)*15)))

            c.save()
            messagebox.showinfo("Success", "Report exported successfully with Charts and Logs.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")

if __name__ == "__main__":
    app = ReportsWindow()
    app.mainloop()