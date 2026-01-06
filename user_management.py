from tkinter import *
from tkinter import ttk, messagebox
import subprocess
import sys
import database  
from bson.objectid import ObjectId

# --- NAVIGATION FUNCTIONS ---
def back_to_dashboard():
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "dashboard.py"])
    except Exception:
        messagebox.showerror("Error", "Could not find 'dashboard.py'.")

def open_create_account():
    try:
        subprocess.Popen([sys.executable, "create account.py"])
    except Exception:
        messagebox.showerror("Error", "Could not find 'create account.py'.")

# --- DATABASE LOGIC ---
def fetch_users():
    if database.db is None:
        return []
    try:
        return list(database.db['users'].find({}, {"password_hash": 0})) 
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def delete_user():
    selected_item = user_tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Required", "Please select a user to delete.")
        return

    user_data = user_tree.item(selected_item)['values']
    user_id = user_data[0]
    full_name = user_data[1] 

    confirm = messagebox.askyesno("Confirm Delete", f"Delete user: {full_name}?")
    if confirm:
        try:
            database.db['users'].delete_one({"_id": ObjectId(user_id)})
            messagebox.showinfo("Success", "User deleted successfully.")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete user: {e}")

def refresh_table():
    for item in user_tree.get_children():
        user_tree.delete(item)
    
    users = fetch_users()
    for user in users:
        u_id = str(user['_id'])
        u_full_name = user.get('full_name', 'N/A') # New Field
        u_email = user.get('email', 'N/A')
        u_name = user.get('username', 'Unknown')
        u_role = user.get('role', 'Staff')
        
        user_tree.insert("", "end", values=(u_id, u_full_name, u_email, u_name, u_role))

# --- THEME COLORS ---
PRIMARY_GREEN = "#2ecc71"
PRIMARY_BLUE = "#3498db"  
BG_LIGHT = "#f4f7f6"
DARK_TEXT = "#2c3e50"
WHITE = "#ffffff"
DANGER_RED = "#e74c3c"

window = Tk()
window.title("Loans Management System - User Management")
window.geometry("1250x700") # Wider to accommodate Full Name
window.configure(bg=BG_LIGHT)

# --- HEADER ---
header = Frame(window, bg=PRIMARY_GREEN, height=100)
header.pack(fill="x", side="top")
header.pack_propagate(False)

Label(header, text="USER MANAGEMENT", font=("Segoe UI", 24, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack(pady=(25, 0))

# --- MAIN CONTENT ---
main_frame = Frame(window, bg=BG_LIGHT, padx=40, pady=20)
main_frame.pack(fill="both", expand=True)

actions_bar = Frame(main_frame, bg=BG_LIGHT)
actions_bar.pack(fill="x", pady=(0, 20))

Button(actions_bar, text="+ Add New User", bg=PRIMARY_GREEN, fg=WHITE,
       font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, 
       cursor="hand2", command=open_create_account).pack(side="left", padx=5)

Button(actions_bar, text="↻ Refresh List", bg=DARK_TEXT, fg=WHITE,
       font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, 
       cursor="hand2", command=refresh_table).pack(side="left", padx=5)

Button(actions_bar, text="🗑 Delete User", bg=DANGER_RED, fg=WHITE,
       font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, 
       cursor="hand2", command=delete_user).pack(side="right", padx=5)

# --- TREEVIEW TABLE ---
tree_frame = Frame(main_frame, bg=WHITE)
tree_frame.pack(fill="both", expand=True)

tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

# Columns now include "Full Name"
user_tree = ttk.Treeview(tree_frame, columns=("ID", "FullName", "Email", "Username", "Role"), 
                        show="headings", yscrollcommand=tree_scroll.set)
tree_scroll.config(command=user_tree.yview)

user_tree.heading("ID", text="User ID")
user_tree.heading("FullName", text="Full Name")
user_tree.heading("Email", text="Email Address")
user_tree.heading("Username", text="Username")
user_tree.heading("Role", text="Access Level")

user_tree.column("ID", width=180, anchor="center")
user_tree.column("FullName", width=200, anchor="w")
user_tree.column("Email", width=220, anchor="w")
user_tree.column("Username", width=150, anchor="w")
user_tree.column("Role", width=120, anchor="center")

user_tree.pack(fill="both", expand=True)

# --- FOOTER ---
footer = Frame(window, bg=BG_LIGHT)
footer.pack(side="bottom", fill="x", pady=20)

Button(footer, text="Back to Dashboard", font=("Segoe UI", 11, "bold"), 
       bg=PRIMARY_BLUE, fg=WHITE, activebackground="#2980b9", 
       activeforeground=WHITE, bd=0, padx=25, pady=10, 
       cursor="hand2", command=back_to_dashboard).pack()

if database.db is not None:
    refresh_table()
else:
    messagebox.showerror("Database Error", "Not connected to database.")

window.mainloop()