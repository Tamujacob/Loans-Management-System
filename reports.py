import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import database
import sys
import subprocess
import os
import datetime
import matplotlib
# Use the TkAgg backend explicitly to prevent startup crashes in some environments
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
# This block handles passing user login information (Role and Name) between different 
# script files using command-line arguments (sys.argv). This ensures that the 
# application knows who is logged in even when opening new windows.
try:
    if len(sys.argv) > 2:
        CURRENT_USER_ROLE = sys.argv[1]
        CURRENT_USER_NAME = sys.argv[2]
    else:
        # Defaults if the script is run directly without arguments
        CURRENT_USER_ROLE = "Admin"
        CURRENT_USER_NAME = "Guest"
except IndexError:
    CURRENT_USER_ROLE = "Admin"
    CURRENT_USER_NAME = "Guest"

# --- MAIN WINDOW CLASS ---
# Inherits from tk.Tk to create the primary window for reports and analytics.
class ReportsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # BASIC WINDOW CONFIGURATION
        
        self.title(f"BIG ON GOLD - Analytics & Logs - {CURRENT_USER_NAME}")
        self.geometry("1250x750")
        self.config(bg="#f4f7f6")

        # APPLICATION ICON SETUP
        # Display the company logo as the window icon.
        try:
            self.icon_img = Image.open("bu logo.png")
            self.icon_photo = ImageTk.PhotoImage(self.icon_img)
            self.iconphoto(False, self.icon_photo)
        except Exception:
            pass # Silently fail if image is missing

        # THEME COLOR PALETTE
        # Defines a consistent set of hex colors used throughout the UI components.
        self.colors = {
            "primary": "#2ecc71",   # Green
            "dark_green": "#27ae60",
            "dark": "#2c3e50",      # Deep Blue/Grey
            "bg": "#f4f7f6",        # Light Grey
            "white": "#ffffff",
            "accent": "#3498db"     # Light Blue
        }

        # UI COMPONENT INITIALIZATION
        self.create_header()
        
        # TABBED INTERFACE (NOTEBOOK) STYLING
        # Configures how the tabs look, including font, padding, and colors when selected.
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', font=('Segoe UI', 9, 'bold'), padding=[15, 5])
        style.map('TNotebook.Tab', background=[('selected', self.colors["primary"])], 
                  foreground=[('selected', 'white')])

        # TAB LAYOUT SETUP
        # Creates a container for multiple tabs (Notebook) and packs it into the window.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=5)

        # TAB 1: FINANCIAL ANALYTICS
        # Initializes the frame for the first tab.
        self.tab_finance = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_finance, text="  📊  FINANCIAL ANALYTICS  ")

        # TAB 2: USER ACTIVITY LOGS
        # Initializes the frame for the second tab.
        self.tab_audit = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_audit, text="  🔑  USER ACTIVITY LOGS  ")

        # CONTENT POPULATION
        # Calls methods to build the interior UI of each tab and the bottom control bar.
        self.setup_finance_tab()
        self.setup_audit_tab()
        self.create_bottom_controls()

    def create_header(self):
        """Creates the top branding bar containing the logo and system title."""
        header = tk.Frame(self, bg=self.colors["primary"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Header Logo Logic
        try:
            logo_img = Image.open("bu logo.png")
            logo_img = logo_img.resize((45, 45), Image.LANCZOS)
            self.header_logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header, image=self.header_logo_photo, bg=self.colors["primary"])
            logo_label.pack(side="left", padx=(20, 10))
        except Exception:
            # Fallback icon if the image file isn't found
            tk.Label(header, text="💰", font=("Segoe UI", 20), bg=self.colors["primary"], fg="white").pack(side="left", padx=20)

        # Header Title Logic
        title_frame = tk.Frame(header, bg=self.colors["primary"])
        title_frame.pack(side="left", pady=5)
        
        tk.Label(title_frame, text="BIG ON GOLD LOANS", font=("Segoe UI", 16, "bold"), 
                  bg=self.colors["primary"], fg="white").pack(anchor="w")

    def _get_filtered_data(self, start_date=None):
        """Fetches loan and payment data from the database and calculates financial metrics."""
        try:
            query = {}
            if start_date:
                # Uses a regex to match the beginning of the date string (YYYY-MM-DD)
                query = {"date": {"$regex": f"^{start_date}"}} 
            
            # Retrieve documents from MongoDB collections
            loans = list(database.db['loans'].find(query))
            payments = list(database.db['payments'].find()) 
            
            # Calculate financial totals
            total_lent = sum(float(l.get('loan_amount', 0)) for l in loans)
            
            # Calculate recovery by matching payment loan_ids with currently filtered loans
            total_rec = sum(float(p.get('payment_amount', 0)) for p in payments if any(str(l['_id']) == str(p.get('loan_id')) for l in loans))
            
            debt = total_lent - total_rec
            active_count = len([l for l in loans if l.get('status') not in ['Fully Paid', 'Rejected']])
            
            return total_lent, total_rec, debt, active_count, loans
        except Exception:
            return 0, 0, 0, 0, []

    def setup_finance_tab(self):
        """Builds the UI elements for the Financial Analytics tab."""
        # Action Bar (Filters)
        filter_frame = tk.Frame(self.tab_finance, bg=self.colors["bg"])
        filter_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(filter_frame, text="Whole Business Analysis", command=lambda: self.refresh_finance(None), 
                  bg=self.colors["dark"], fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        
        tk.Button(filter_frame, text="Filter by Date (YYYY-MM-DD)", command=self.ask_date_filter, 
                  bg=self.colors["accent"], fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)

        # Container for Summary Statistic Cards
        self.card_container = tk.Frame(self.tab_finance, bg=self.colors["bg"])
        self.card_container.pack(fill="x", padx=10)
        
        # Container for Matplotlib Graphical Displays
        self.chart_area = tk.Frame(self.tab_finance, bg="white", highlightthickness=1, highlightbackground="#dcdde1")
        self.chart_area.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.refresh_finance()

    def ask_date_filter(self):
        """Invokes a simple dialog box to collect a filter date from the user."""
        date_str = simpledialog.askstring("Filter", "Enter date (YYYY-MM-DD):")
        if date_str:
            self.refresh_finance(date_str)

    def refresh_finance(self, date_filter=None):
        """Re-fetches database data and redraws both the summary cards and the charts."""
        # Clear existing widgets to avoid duplication
        for widget in self.card_container.winfo_children(): widget.destroy()
        for widget in self.chart_area.winfo_children(): widget.destroy()

        # Fetch new data based on current filter
        self.current_data = self._get_filtered_data(date_filter)
        lent, rec, debt, count, loans = self.current_data

        # Re-build summary metric cards
        self._build_card(self.card_container, "TOTAL CASH GIVEN OUT", f"RWF {lent:,.0f}", 0)
        self._build_card(self.card_container, "TOTAL RECOVERY", f"RWF {rec:,.0f}", 1)
        self._build_card(self.card_container, "MONEY NOT YET RECOVERED", f"RWF {debt:,.0f}", 2)

        # MATPLOTLIB CHART GENERATION
        # Clears previous figures to prevent memory leaks and performance lag.
        plt.close('all') 
        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3), dpi=90)
        
        # CHART 1: Pie chart of Loan Status Distribution
        statuses = [l.get('status', 'Pending') for l in loans]
        status_counts = {s: statuses.count(s) for s in set(statuses)}
        
        if status_counts:
            ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', colors=['#3498db', '#2ecc71', '#e74c3c'])
        else:
            ax1.text(0.5, 0.5, 'No Data', ha='center')
        ax1.set_title("Status Breakdown")

        # CHART 2: Bar chart comparing Lent vs Recovered vs Debt
        ax2.bar(['Given Out', 'Recovered', 'In Debt'], [lent, rec, debt], color=[self.colors["dark"], self.colors["primary"], "#e74c3c"])
        ax2.set_title("Financial Health")

        # Integrate the Matplotlib canvas into the Tkinter frame
        canvas_plot = FigureCanvasTkAgg(self.fig, master=self.chart_area)
        canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    def setup_audit_tab(self):
        """Builds the UI elements for the Activity Logs tab including the scrollable table."""
        filter_frame = tk.Frame(self.tab_audit, bg=self.colors["bg"])
        filter_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(filter_frame, text="Show All Logs", command=lambda: self.load_logs(None), 
                  bg=self.colors["dark"], fg="white").pack(side="left", padx=5)
        
        tree_frame = tk.Frame(self.tab_audit, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # TABLE (TREEVIEW) CONFIGURATION
        columns = ("Time", "User", "Action", "Details")
        self.audit_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        for col in columns: self.audit_tree.heading(col, text=col)
        self.audit_tree.pack(fill="both", expand=True)
        self.load_logs()

    def load_logs(self, date_filter=None):
        """Fetches the latest 100 activity logs from the database and inserts them into the table."""
        for i in self.audit_tree.get_children(): self.audit_tree.delete(i)
        query = {}
        if date_filter: query = {"timestamp": {"$regex": f"^{date_filter}"}}
        try:
            # Sort by timestamp descending so the newest logs appear first
            self.logs_data = list(database.db['logs'].find(query).sort("timestamp", -1).limit(100))
            for log in self.logs_data:
                self.audit_tree.insert("", "end", values=(log.get('timestamp'), log.get('user'), log.get('action'), log.get('details')))
        except Exception: pass

    def _build_card(self, parent, title, value, col):
        """Helper utility to construct a visually appealing 'Card' for summary metrics."""
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#dcdde1", padx=15, pady=10)
        card.grid(row=0, column=col, padx=5, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 14, "bold"), bg="white", fg=self.colors["dark"]).pack(anchor="w")

    def create_bottom_controls(self):
        """Initializes the sticky navigation bar at the bottom of the window."""
        ctrl_frame = tk.Frame(self, bg=self.colors["white"], pady=10, highlightthickness=1, highlightbackground="#dcdde1")
        ctrl_frame.pack(fill="x", side="bottom")
        
        tk.Button(ctrl_frame, text="⬅  BACK", command=self.go_back, bg=self.colors["dark"], fg="white", 
                  relief="flat", width=15, height=1).pack(side="left", padx=20)

        tk.Button(ctrl_frame, text="📥  DOWNLOAD PDF", command=self.export_to_pdf, bg=self.colors["primary"], fg="white", 
                  relief="flat", width=20, height=1).pack(side="right", padx=20)

    def go_back(self):
        """Closes current window and re-launches the main dashboard script."""
        subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
        self.destroy()

    def export_to_pdf(self):
        """Handles the complex logic of converting UI data, tables, and charts into a multi-page PDF report."""
        # Collect desired save path from user
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path: return
        try:
            # Setup PDF canvas
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            # --- PART 1: PAGE HEADER ---
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkgreen)
            c.drawString(50, height - 50, "BIG ON GOLD LOANS - ANALYTICS REPORT")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(50, height - 65, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.line(50, height - 75, width - 50, height - 75)

            # --- PART 2: FINANCIAL SUMMARY TABLE ---
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

            # --- PART 3: CAPTURING THE MATPLOTLIB CHART ---
            # Save the active plot to an in-memory byte stream instead of a physical file.
            imgdata = io.BytesIO()
            self.fig.savefig(imgdata, format='png', bbox_inches='tight')
            imgdata.seek(0)
            
            # Use PIL to open the byte stream and draw it into the PDF report.
            chart_img = Image.open(imgdata)
            c.drawInlineImage(chart_img, 50, height - 480, width=500, height=250)

            # --- PART 4: AUDIT LOGS (ON NEW PAGE) ---
            c.showPage()
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 50, "USER ACTIVITY LOGS")
            c.line(50, height - 60, width - 50, height - 60)

            log_table_data = [["Timestamp", "User", "Action"]]
            # Safety check: print only the first 25 logs to ensure they fit on one page.
            logs_to_print = getattr(self, 'logs_data', [])
            for log in logs_to_print[:25]: 
                log_table_data.append([log.get('timestamp', '')[:19], log.get('user', ''), log.get('action', '')])
            
            # Apply styling to the audit log table
            lt = Table(log_table_data, colWidths=[120, 100, 300])
            lt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8)
            ]))
            lt.wrapOn(c, width, height)
            lt.drawOn(c, 50, height - (70 + (len(log_table_data)*15)))

            # Save the file and notify the user
            c.save()
            messagebox.showinfo("Success", "Report exported successfully with Charts and Logs.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    app = ReportsWindow()
    app.mainloop()