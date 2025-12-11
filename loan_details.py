import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from tkcalendar import DateEntry # Essential for Next Repayment Date selection
import database # Import your actual database module

class LoanDetailsWindow(tk.Toplevel):
    def __init__(self, master, loan_data, refresh_callback):
        """
        Initializes the Loan Details and Edit window.

        Args:
            master (tk.Tk/tk.Toplevel): The parent window (usually the Dashboard).
            loan_data (dict): The complete dictionary of loan data, fetched from the DB.
            refresh_callback (function): The function to call on the Dashboard after saving changes.
        """
        super().__init__(master)
        self.loan_data = loan_data
        self.loan_id = loan_data['_id']
        self.refresh_callback = refresh_callback
        
        self.title(f"Details & Edit: {self.loan_data['customer_name']}")
        self.geometry("750x650")
        self.resizable(True, True)
        self.configure(bg='#f0f0f0') # Light background
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1) # Main frame takes up space
        
        self.entries = {} # Dictionary to hold references to all editable widgets
        
        self.create_widgets()
        self.load_fields()
        
        # Make the window modal
        self.transient(master)
        self.grab_set() 
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """Builds the scrollable layout for displaying and editing loan details."""
        
        # --- 1. Scrollable Main Frame Setup ---
        main_frame = ttk.Frame(self, padding="15", style='Card.TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Create Canvas and Scrollbar
        canvas = tk.Canvas(main_frame, borderwidth=0, bg='#f0f0f0')
        canvas.grid(row=0, column=0, sticky="nsew")
        
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Frame inside the canvas where all content will go
        self.details_content = ttk.Frame(canvas, padding="5")
        canvas.create_window((0, 0), window=self.details_content, anchor="nw")
        
        # Configure the grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        self.details_content.columnconfigure((1, 3), weight=1) # Make data columns flexible
        
        self.details_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # --- 2. Header ---
        ttk.Label(self.details_content, text="Loan ID:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        ttk.Label(self.details_content, text=self.loan_id).grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        ttk.Separator(self.details_content, orient='horizontal').grid(row=1, column=0, columnspan=4, sticky="ew", pady=(5, 15))

        # --- 3. Input Fields Definitions (Label, DB_Key, Widget_Type, Row, Column, Values) ---
        
        # Using a list of tuples for structured field creation
        field_definitions = [
            ("Customer Name", 'customer_name', 'entry', 2, 0),
            ("Loan Amount (€)", 'loan_amount', 'entry', 2, 2),
            ("Loan Type", 'loan_type', 'combo', 3, 0, ['Personal', 'Business', 'Housing', 'Education']),
            ("Duration (Months)", 'duration', 'entry', 3, 2), # Assuming duration is editable as text, e.g., "12 Months"
            ("Application Date", 'application_date', 'label', 4, 0), # Non-editable label
            ("Status", 'status', 'combo', 4, 2, ['Pending', 'Approved', 'Under Payment', 'Fully Paid', 'Rejected']),
            
            ("--- Repayment Details ---", None, 'separator', 5, 0),
            
            # This is the key planning field
            ("Next Repayment Date", 'next_payment', 'date', 6, 0), 
            ("Interest Rate (%)", 'interest_rate', 'entry', 6, 2),
            ("Collateral Provided", 'collateral_details', 'entry', 7, 0),
            ("Officer Assigned", 'officer_assigned', 'entry', 7, 2),

            ("--- Notes ---", None, 'separator', 8, 0),
            ("Notes/Comments", 'notes', 'entry_long', 9, 0),
        ]
        
        current_row = 2
        
        for label_text, key, widget_type, grid_row, grid_col, *options in field_definitions:
            if key is None:
                 # Separator row
                ttk.Label(self.details_content, text=label_text, font=("Arial", 10, "italic")).grid(row=grid_row, column=0, columnspan=4, sticky="w", pady=(10, 5))
                continue
                
            col_span = 1
            if widget_type == 'entry_long':
                col_span = 3
                
            # Create Label
            ttk.Label(self.details_content, text=f"{label_text}:").grid(row=grid_row, column=grid_col, sticky="w", padx=5, pady=5)
            
            # Determine placement for the widget
            widget_col = grid_col + 1
            
            # Create Widget
            if widget_type == 'entry':
                widget = ttk.Entry(self.details_content, width=25)
                widget.grid(row=grid_row, column=widget_col, sticky="ew", padx=5, pady=5)
                self.entries[key] = widget
            elif widget_type == 'combo':
                values = options[0] if options else []
                widget = ttk.Combobox(self.details_content, values=values, state='readonly', width=25)
                widget.grid(row=grid_row, column=widget_col, sticky="ew", padx=5, pady=5)
                self.entries[key] = widget
            elif widget_type == 'date':
                # tkcalendar DateEntry for date selection
                widget = DateEntry(self.details_content, width=22, background='darkblue', 
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                widget.grid(row=grid_row, column=widget_col, sticky="ew", padx=5, pady=5)
                self.entries[key] = widget
            elif widget_type == 'label':
                # Non-editable details
                widget = ttk.Label(self.details_content, text="N/A", font=("Arial", 10))
                widget.grid(row=grid_row, column=widget_col, sticky="w", padx=5, pady=5)
                self.entries[key] = widget
            elif widget_type == 'entry_long':
                widget = ttk.Entry(self.details_content, width=60)
                widget.grid(row=grid_row, column=grid_col + 1, columnspan=col_span, sticky="ew", padx=5, pady=5)
                self.entries[key] = widget

        # --- 4. Action Buttons ---
        action_frame = ttk.Frame(self, padding="10")
        action_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        action_frame.columnconfigure((0, 1), weight=1)

        ttk.Button(action_frame, text="Save Changes", command=self.save_changes, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Close Window", command=self.on_close).pack(side=tk.RIGHT, padx=5)
        
    def load_fields(self):
        """Populates the created widgets with current loan data."""
        data = self.loan_data
        
        for key, widget in self.entries.items():
            value = data.get(key)
            
            if value is None:
                value = 'N/A'

            # 1. Formatting for Display
            if key == 'loan_amount' and isinstance(value, (int, float)):
                 value = f"{value:,.2f}"
            
            # 2. Set Widget Value
            if isinstance(widget, ttk.Entry) or isinstance(widget, ttk.Combobox):
                widget.set(str(value))
            elif isinstance(widget, DateEntry):
                # Handle dates for tkcalendar
                try:
                    # Convert string date to datetime object for DateEntry
                    if isinstance(value, str):
                        date_obj = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                        widget.set_date(date_obj)
                    elif isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
                        widget.set_date(value)
                except:
                    # If date is invalid or 'N/A', set to today's date as a default
                    widget.set_date(datetime.date.today())
            elif isinstance(widget, ttk.Label):
                widget.config(text=str(value))


    def save_changes(self):
        """Validates inputs and saves updated loan data to the database."""
        updated_data = {}
        
        try:
            # 1. Gather Data and Validate
            for key, widget in self.entries.items():
                value = None
                
                if isinstance(widget, ttk.Entry):
                    value = widget.get().strip()
                elif isinstance(widget, ttk.Combobox):
                    value = widget.get().strip()
                elif isinstance(widget, DateEntry):
                    # Get date as a string in 'YYYY-MM-DD' format
                    value = widget.get_date().strftime("%Y-%m-%d")
                else: # Labels are not editable
                    continue
                    
                # Basic Type Conversion/Validation
                if key in ['loan_amount', 'interest_rate']:
                    if not value or value == 'N/A':
                        value = 0.0 # Save as 0 if empty
                    else:
                        value = float(value.replace('€', '').replace(',', ''))
                
                updated_data[key] = value
                
            # 2. Call the Database Update function
            # **ASSUMES** database.py has an update_loan_details(loan_id, data_dict) method
            result = database.update_loan_details(self.loan_id, updated_data)
            
            if result:
                messagebox.showinfo("Success", f"Loan ID {str(self.loan_id)[-4:]} details saved successfully.")
                self.loan_data.update(updated_data) # Update local data
                self.refresh_callback() # Refresh the main dashboard view
                
                # Close if the loan status is terminal
                if updated_data.get('status') in ['Fully Paid', 'Rejected']:
                    self.on_close()
            else:
                 messagebox.showerror("Error", "Database update failed.")

        except ValueError as ve:
             messagebox.showerror("Validation Error", f"Please check numeric fields (Amount, Rate): {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def on_close(self):
        """Closes the window and releases focus."""
        self.grab_release()
        self.destroy()


