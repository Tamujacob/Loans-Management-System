from tkinter import *
from tkinter import ttk, messagebox
import subprocess
import sys
import database  
from bson.objectid import ObjectId

# --- NAVIGATION FUNCTIONS ---
def back_to_dashboard():
    """Destroys current window and returns to dashboard."""
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "dashboard.py"])
    except Exception:
        messagebox.showerror("Error", "Could not find 'dashboard.py'.")

def open_create_account():
    """Opens the account creation script."""
    try:
        subprocess.Popen([sys.executable, "create account.py"])
    except Exception:
        messagebox.showerror("Error", "Could not find 'create account.py'.")

# --- DATABASE LOGIC ---
def fetch_users():
    """Retrieves all users from MongoDB including email."""
    if database.db is None:
        return []
    try:
        # We fetch all fields except the sensitive password hash
        return list(database.db['users'].find({}, {"password_hash": 0})) 
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def delete_user():
    """Deletes the selected user from the database."""
    selected_item = user_tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Required", "Please select a user to delete.")
        return

    # values[0] = ID, values[1] = Email, values[2] = Username
    user_data = user_tree.item(selected_item)['values']
    user_id = user_data[0]
    username = user_data[2] 

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user: {username}?")
    if confirm:
        try:
            database.db['users'].delete_one({"_id": ObjectId(user_id)})
            messagebox.showinfo("Success", "User deleted successfully.")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete user: {e}")

def refresh_table():
    """Clears and reloads the user table with the new Email field."""
    for item in user_tree.get_children():
        user_tree.delete(item)
    
    users = fetch_users()
    for user in users:
        # Extract fields with .get() to avoid errors if a field is missing in old records
        u_id = str(user['_id'])
        u_email = user.get('email', 'N/A')
        u_name = user.get('username', 'Unknown')
        u_role = user.get('role', 'Staff')
        
        user_tree.insert("", "end", values=(u_id, u_email, u_name, u_role))

# --- THEME COLORS ---
PRIMARY_GREEN = "#2ecc71"
PRIMARY_BLUE = "#3498db"  
BG_LIGHT = "#f4f7f6"
DARK_TEXT = "#2c3e50"
WHITE = "#ffffff"
DANGER_RED = "#e74c3c"

# --- MAIN WINDOW SETUP ---
window = Tk()
window.title("Loans Management System - User Management")
window.geometry("1150x700") # Slightly wider for the extra column
window.configure(bg=BG_LIGHT)

# --- SET WINDOW TITLE BAR ICON ---
try:
    title_icon = PhotoImage(file="bu logo.png")
    window.iconphoto(True, title_icon)
except Exception:
    pass

# --- HEADER SECTION ---
header = Frame(window, bg=PRIMARY_GREEN, height=100)
header.pack(fill="x", side="top")
header.pack_propagate(False)

Label(header, text="USER MANAGEMENT", font=("Segoe UI", 24, "bold"), 
      fg=WHITE, bg=PRIMARY_GREEN).pack(pady=(25, 0))

# --- MAIN CONTENT ---
main_frame = Frame(window, bg=BG_LIGHT, padx=40, pady=20)
main_frame.pack(fill="both", expand=True)

# Action Buttons Bar
actions_bar = Frame(main_frame, bg=BG_LIGHT)
actions_bar.pack(fill="x", pady=(0, 20))

add_btn = Button(actions_bar, text="+ Add New User", bg=PRIMARY_GREEN, fg=WHITE,
                font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, 
                cursor="hand2", command=open_create_account)
add_btn.pack(side="left", padx=5)

refresh_btn = Button(actions_bar, text="↻ Refresh List", bg=DARK_TEXT, fg=WHITE,
                    font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, 
                    cursor="hand2", command=refresh_table)
refresh_btn.pack(side="left", padx=5)

delete_btn = Button(actions_bar, text="🗑 Delete User", bg=DANGER_RED, fg=WHITE,
                   font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, 
                   cursor="hand2", command=delete_user)
delete_btn.pack(side="right", padx=5)

# --- USER TABLE (TREEVIEW) ---
table_style = ttk.Style()
table_style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
table_style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)

tree_frame = Frame(main_frame, bg=WHITE)
tree_frame.pack(fill="both", expand=True)

tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

# Added "Email" to the columns list
user_tree = ttk.Treeview(tree_frame, columns=("ID", "Email", "Username", "Role"), 
                        show="headings", yscrollcommand=tree_scroll.set)
tree_scroll.config(command=user_tree.yview)

user_tree.heading("ID", text="User ID")
user_tree.heading("Email", text="Email Address")
user_tree.heading("Username", text="Username")
user_tree.heading("Role", text="Access Level")

user_tree.column("ID", width=200, anchor="center")
user_tree.column("Email", width=250, anchor="w")
user_tree.column("Username", width=200, anchor="w")
user_tree.column("Role", width=150, anchor="center")

user_tree.pack(fill="both", expand=True)

# --- FOOTER ---
footer = Frame(window, bg=BG_LIGHT)
footer.pack(side="bottom", fill="x", pady=20)

back_btn = Button(footer, text="Back to Dashboard", font=("Segoe UI", 11, "bold"), 
                  bg=PRIMARY_BLUE, fg=WHITE, activebackground="#2980b9", 
                  activeforeground=WHITE, bd=0, padx=25, pady=10, 
                  cursor="hand2", command=back_to_dashboard)
back_btn.pack()

# Initial Data Load
if database.db is not None:
    refresh_table()
else:
    messagebox.showerror("Database Error", "Not connected to database.")

window.mainloop()