import tkinter as tk
from tkinter import ttk, messagebox
import database
import datetime
import uuid
import subprocess
import sys
import os

# --- THEME & STYLE ---
PRIMARY_GREEN = "#2ecc71"
BG_LIGHT = "#f4f7f6"
DARK_TEXT = "#2c3e50"
BORDER_COLOR = "#dcdde1"
FONT_FAMILY = "Segoe UI" 

class LoanApplicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loan Application System")
        self.root.geometry("1100x750") 
        self.root.configure(bg=BG_LIGHT)

        self.repayment_method_var = tk.StringVar(value="Monthly")
        self.terms_var = tk.IntVar()
        
        self.setup_ui()

    def setup_ui(self):
        # 1. Header
        header = tk.Frame(self.root, bg=PRIMARY_GREEN, height=100)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="LOAN APPLICATION FORM", font=(FONT_FAMILY, 24, "bold"), 
                 bg=PRIMARY_GREEN, fg="white").pack(pady=(25, 0))

        # 2. Scrollable Canvas
        self.main_canvas = tk.Canvas(self.root, bg=BG_LIGHT, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        
        # We set a fixed width on this frame to ensure it stays wide
        self.scrollable_frame = tk.Frame(self.main_canvas, bg=BG_LIGHT)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        # Positioning the scrollable content
        self.main_canvas.create_window((550, 0), window=self.scrollable_frame, anchor="n")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 3. The Card (FIXED: Width handled via frame config, not pack)
        self.card = tk.Frame(self.scrollable_frame, bg="white", padx=50, pady=40, 
                             highlightthickness=1, highlightbackground=BORDER_COLOR,
                             width=900) # Defined width here
        self.card.pack(pady=30, padx=20)
        self.card.grid_propagate(True) # Allow internal widgets to define height

        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_columnconfigure(1, weight=1)

        self.build_form()

    def create_label(self, text, row, col, colspan=1):
        lbl = tk.Label(self.card, text=text, font=(FONT_FAMILY, 11, "bold"), bg="white", fg=DARK_TEXT)
        lbl.grid(row=row, column=col, columnspan=colspan, sticky="w", padx=15, pady=(15, 5))

    def create_entry(self, row, col, colspan=1):
        ent = tk.Entry(self.card, font=(FONT_FAMILY, 14), bd=0, highlightthickness=1, 
                       highlightbackground=BORDER_COLOR)
        ent.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=15, pady=(0, 20), ipady=12)
        return ent

    def build_form(self):
        # Name
        self.create_label("FULL NAME OF APPLICANT", 0, 0, colspan=2)
        self.name_entry = self.create_entry(1, 0, colspan=2)

        # Amount & Type
        self.create_label("LOAN AMOUNT (RWF)", 2, 0)
        self.create_label("LOAN CATEGORY", 2, 1)
        
        self.amount_entry = self.create_entry(3, 0)
        self.amount_entry.bind("<KeyRelease>", self.update_return_amount)
        
        self.type_combo = ttk.Combobox(self.card, values=["Personal", "Business", "Home", "Education", "Vehicle"], 
                                       font=(FONT_FAMILY, 13), state="readonly")
        self.type_combo.grid(row=3, column=1, sticky="ew", padx=15, pady=(0, 20))

        # Duration & Repayment
        self.create_label("REPAYMENT DURATION", 4, 0)
        self.create_label("PAYMENT FREQUENCY", 4, 1)

        self.duration_combo = ttk.Combobox(self.card, values=["6 months", "1 year", "2 years", "3 years", "5 years"], 
                                           font=(FONT_FAMILY, 13), state="readonly")
        self.duration_combo.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 20))
        self.duration_combo.bind("<<ComboboxSelected>>", self.update_return_amount)

        radio_frame = tk.Frame(self.card, bg="white")
        radio_frame.grid(row=5, column=1, sticky="w", padx=15)
        tk.Radiobutton(radio_frame, text="Monthly", variable=self.repayment_method_var, 
                       value="Monthly", bg="white", font=(FONT_FAMILY, 12)).pack(side="left")
        tk.Radiobutton(radio_frame, text="Weekly", variable=self.repayment_method_var, 
                       value="Weekly", bg="white", font=(FONT_FAMILY, 12)).pack(side="left", padx=20)

        # Purpose
        self.create_label("PURPOSE OF LOAN", 6, 0, colspan=2)
        self.purpose_text = tk.Text(self.card, height=4, font=(FONT_FAMILY, 12), bd=1, 
                                   relief="solid", padx=10, pady=10)
        self.purpose_text.grid(row=7, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 25))

        # Totals Display
        self.total_frame = tk.Frame(self.card, bg="#f1f2f6", padx=30, pady=25)
        self.total_frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        
        tk.Label(self.total_frame, text="ESTIMATED TOTAL REPAYMENT (12% Interest)", 
                 font=(FONT_FAMILY, 10, "bold"), bg="#f1f2f6", fg=DARK_TEXT).pack(anchor="w")
        
        self.return_amount_lbl = tk.Label(self.total_frame, text="0.00 RWF", 
                                          font=(FONT_FAMILY, 28, "bold"), bg="#f1f2f6", fg=PRIMARY_GREEN)
        self.return_amount_lbl.pack(anchor="w")

        # Terms & Buttons
        tk.Checkbutton(self.card, text="I accept the terms and conditions", 
                       variable=self.terms_var, bg="white", font=(FONT_FAMILY, 11)).grid(row=9, column=0, columnspan=2, sticky="w", padx=15, pady=20)

        btn_frame = tk.Frame(self.card, bg="white")
        btn_frame.grid(row=10, column=0, columnspan=2, pady=(10, 20))

        tk.Button(btn_frame, text="SUBMIT APPLICATION", bg=PRIMARY_GREEN, fg="white", font=(FONT_FAMILY, 13, "bold"), 
                  bd=0, width=22, height=2, cursor="hand2", command=self.submit_application).pack(side="left", padx=15)
        
        tk.Button(btn_frame, text="PRINT COPY", bg=DARK_TEXT, fg="white", font=(FONT_FAMILY, 13, "bold"), 
                  bd=0, width=18, height=2, cursor="hand2", command=self.print_application).pack(side="left", padx=15)

        tk.Button(self.scrollable_frame, text="Back to Dashboard", font=(FONT_FAMILY, 11, "underline"), 
                  bg=BG_LIGHT, fg=DARK_TEXT, bd=0, command=self.return_to_dashboard).pack(pady=20)

    # --- LOGIC FUNCTIONS ---
    def update_return_amount(self, event=None):
        try:
            amt_str = self.amount_entry.get().replace(',', '')
            loan_amount = float(amt_str) if amt_str else 0
            duration_text = self.duration_combo.get()
            
            if not duration_text:
                self.return_amount_lbl.config(text="0.00 RWF")
                return

            years = int(duration_text.split()[0]) if "year" in duration_text else int(duration_text.split()[0]) / 12.0
            total = loan_amount + (loan_amount * 0.12 * years)
            self.return_amount_lbl.config(text=f"{total:,.2f} RWF")
        except:
            self.return_amount_lbl.config(text="0.00 RWF")

    def print_application(self):
        if not self.name_entry.get():
            messagebox.showwarning("Incomplete", "Please enter the applicant's name.")
            return
        
        app_id = str(uuid.uuid4())[:8].upper()
        filename = f"Loan_App_{app_id}.txt"
        content = f"LOAN APPLICATION ID: {app_id}\nName: {self.name_entry.get()}\nTotal: {self.return_amount_lbl.cget('text')}\nDate: {datetime.datetime.now()}"
        
        with open(filename, "w") as f:
            f.write(content)
        os.startfile(filename)

    def submit_application(self):
        if self.terms_var.get() == 0:
            messagebox.showwarning("Terms", "Please accept the terms.")
            return
        messagebox.showinfo("Success", "Application Submitted!")
        self.return_to_dashboard()

    def return_to_dashboard(self):
        self.root.destroy()
        subprocess.Popen([sys.executable, "dashboard.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = LoanApplicationApp(root)
    root.mainloop()