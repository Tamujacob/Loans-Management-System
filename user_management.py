from tkinter import *
from tkinter import ttk, messagebox
import subprocess
import sys
import database  
from bson.objectid import ObjectId
import os

# --- 1. SESSION PERSISTENCE ---
try:
    CURRENT_USER_ROLE = sys.argv[1]
    CURRENT_USER_NAME = sys.argv[2]
except IndexError:
    # Defaulting to Admin for management purposes if not provided
    CURRENT_USER_ROLE = "Admin"
    CURRENT_USER_NAME = "Administrator"

# --- NAVIGATION FUNCTIONS ---
def back_to_dashboard():
    window.destroy()
    try:
        subprocess.Popen([sys.executable, "dashboard.py", CURRENT_USER_ROLE, CURRENT_USER_NAME])
    except Exception:
        messagebox.showerror("Error", "Could not find 'dashboard.py'.")

def handle_logout():
    confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out?")
    if confirm:
        # LOG THE ACTIVITY
        database.log_activity(CURRENT_USER_NAME, "Logout", "User signed out from User Management")
        window.destroy()
        try:
            subprocess.Popen([sys.executable, "login.py"])
        except Exception:
            messagebox.showerror("Error", "Could not return to login screen.")

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
    username_to_del = user_data[3]

    confirm = messagebox.askyesno("Confirm Delete", f"Delete user: {full_name}?")
    if confirm:
        try:
            database.db['users'].delete_one({"_id": ObjectId(user_id)})
            
            # LOG THE ACTIVITY
            database.log_activity(CURRENT_USER_NAME, "Delete User", f"Deleted account for {full_name} ({username_to_del})")
            
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
        u_full_name = user.get('full_name', 'N/A')
        u_email = user.get('email', 'N/A')
        u_name = user.get('username', 'Unknown')
        u_role = user.get('role', 'Staff')
        
        user_tree.insert("", "end", values=(u_id, u_full_name, u_email, u_name, u_role))
    
    # LOG THE ACTIVITY
    database.log_activity(CURRENT_USER_NAME, "Refresh User List", "Admin refreshed the user database table")

# --- THEME COLORS ---
PRIMARY_GREEN = "#2ecc71"
PRIMARY_BLUE = "#2980b9"  # Deep blue for "Back"
BG_LIGHT = "#f4f7f6"
DARK_TEXT = "#2c3e50"
WHITE = "#ffffff"
DANGER_RED = "#c0392b"    # Matches dashboard logout red
HOVER_RED = "#e74c3c"

window = Tk()
window.title(f"User Management - Logged in as: {CURRENT_USER_NAME}")
window.geometry("1250x800") 
window.configure(bg=BG_LIGHT)

# --- ICON UPDATE (Replacing the leaf) ---
try:
    icon_path = "bu logo.png"
    if os.path.exists(icon_path):
        img = PhotoImage(file=icon_path)
        window.iconphoto(False, img)
except Exception as e:
    print(f"Icon could not be loaded: {e}")

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

# --- FOOTER SECTION ---
footer = Frame(window, bg=BG_LIGHT)
footer.pack(side="bottom", fill="x", pady=(20, 40)) 

btn_container = Frame(footer, bg=BG_LIGHT)
btn_container.pack()

back_btn = Button(
    btn_container, 
    text="🔙 BACK TO DASHBOARD", 
    font=("Segoe UI", 13, "bold"),
    bg=PRIMARY_BLUE, 
    fg=WHITE,
    activebackground="#3498db",
    activeforeground=WHITE,
    width=25,
    height=2,
    bd=0,
    cursor="hand2",
    command=back_to_dashboard
)
back_btn.pack(side="left", padx=20)

logout_btn = Button(
    btn_container, 
    text="🛑 LOGOUT SYSTEM", 
    font=("Segoe UI", 13, "bold"),
    bg=DANGER_RED, 
    fg=WHITE,
    activebackground=HOVER_RED,
    activeforeground=WHITE,
    width=25,
    height=2,
    bd=0,
    cursor="hand2",
    command=handle_logout
)
logout_btn.pack(side="left", padx=20)

def on_enter_logout(e): logout_btn['background'] = HOVER_RED
def on_leave_logout(e): logout_btn['background'] = DANGER_RED
logout_btn.bind("<Enter>", on_enter_logout)
logout_btn.bind("<Leave>", on_leave_logout)

if database.db is not None:
    refresh_table()
else:
    messagebox.showerror("Database Error", "Not connected to database.")

window.mainloop()