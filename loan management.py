from tkinter import *
from tkinter import messagebox

# Create the main window
window = Tk()
window.title("Loan Management System")
window.geometry("700x500")
window.config(bg="#f0f0f0")

# Simulated list of loans (as you would typically get from a database)
loan_data = [
    {"loan_id": 1, "amount": 5000, "interest_rate": 5, "term": 2, "status": "Active"},
    {"loan_id": 2, "amount": 10000, "interest_rate": 6, "term": 5, "status": "Closed"},
    {"loan_id": 3, "amount": 2000, "interest_rate": 3, "term": 1, "status": "Active"},
]

# Function to display loans
def display_loans(loan_list):
    loan_listbox.delete(0, END)
    for loan in loan_list:
        loan_info = f"Loan ID: {loan['loan_id']}, Amount: ${loan['amount']}, Interest: {loan['interest_rate']}%, Term: {loan['term']} years, Status: {loan['status']}"
        loan_listbox.insert(END, loan_info)

# Function to search loans by loan amount or other criteria
def search_loans():
    search_term = search_entry.get().lower()
    filtered_loans = [
        loan for loan in loan_data if search_term in str(loan["amount"]).lower() or search_term in loan["status"].lower()
    ]
    display_loans(filtered_loans)

# Function to show selected loan details (view/edit)
def view_loan_details(event):
    selected_loan_index = loan_listbox.curselection()
    if selected_loan_index:
        loan_info = loan_data[selected_loan_index[0]]
        loan_details_text.delete(1.0, END)
        loan_details_text.insert(INSERT, f"Loan ID: {loan_info['loan_id']}\n")
        loan_details_text.insert(INSERT, f"Amount: ${loan_info['amount']}\n")
        loan_details_text.insert(INSERT, f"Interest Rate: {loan_info['interest_rate']}%\n")
        loan_details_text.insert(INSERT, f"Loan Term: {loan_info['term']} years\n")
        loan_details_text.insert(INSERT, f"Status: {loan_info['status']}\n")

# Create a 3D frame with shadow effect for the form
def create_3d_frame(parent):
    frame = Frame(parent, bg="#d0d0d0", bd=10, relief=RAISED)
    frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    return frame

# Create the search section
frame = create_3d_frame(window)

# Search bar and button
search_label = Label(frame, text="Search Loan by Amount or Status:", bg="#d0d0d0", font=("Helvetica", 12))
search_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
search_entry = Entry(frame, font=("Helvetica", 12))
search_entry.grid(row=0, column=1, padx=10, pady=5)

search_button = Button(frame, text="Search", font=("Helvetica", 12), bg="#4CAF50", fg="white", command=search_loans)
search_button.grid(row=0, column=2, padx=10, pady=5)

# Create listbox to display loans
loan_listbox = Listbox(window, height=10, width=70, font=("Helvetica", 12))
loan_listbox.grid(row=2, column=0, padx=20, pady=20)
loan_listbox.bind("<ButtonRelease-1>", view_loan_details)  # View loan details when clicked

# Loan details text area (view/edit loan details)
loan_details_label = Label(window, text="Loan Details:", font=("Helvetica", 12))
loan_details_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")

loan_details_text = Text(window, height=10, width=70, font=("Helvetica", 12), wrap=WORD)
loan_details_text.grid(row=4, column=0, padx=20, pady=10)

# Display all loans by default
display_loans(loan_data)

# Run the application
window.mainloop()

