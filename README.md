# 💰 Loan Management System

A robust desktop application built using **Python** and **Tkinter** for efficiently managing, tracking, and calculating interest on loan records with **MongoDB** integration.

## ✨ Features

### Core Functionality
- **🔐 User Authentication**: Secure login system with password hashing (bcrypt)
- **💰 Loan Management**: Comprehensive loan lifecycle management
- **💳 Payment Tracking**: Record payments and track outstanding balances
- **📊 Interest Calculation**: Automatic interest calculation based on terms
- **🔍 Search & Filter**: Advanced search capabilities across loans and customers
- **♻️ Recycle bin**: For keeping deleted loans 
- ** Prints receipt for loan repayments**
- ** Asess roles and what they access i.e  staff and admin

### Technical Features
- **🛡️ Secure Password Storage**: Bcrypt hashing for enhanced security
- **🗄️ MongoDB Integration**: NoSQL database for flexible data storage
- **📱 Responsive GUI**: User-friendly Tkinter interface
- **📤 Data Export**: Excel formats
- **📊 Real-time Updates**: Live data updates across modules

## 🏗️ Project Structure

Loan-Management-System/
├── src/ # Source code
│ ├── login.py # User authentication
│ ├── dashboard.py # Main application dashboard
│ ├── loan_management.py # Loan CRUD operations
│ └── utils/ # Helper functions
├── database/ # Database connection & models
├── assets/ # Icons and images
└── tests/ # Test files


## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- MongoDB instance (local or Atlas)
- Git (for version control)

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/Loan-Management-System.git
cd Loan-Management-System

### Installing dependencies
pip install -r requirements.txt

Database Setup

Install MongoDB locally or use MongoDB Atlas

Update database connection in config.py:

MONGO_URI = "mongodb://localhost:27017"  # Local MongoDB
DATABASE_NAME = "LoanManagementDB"

# Start with login screen
python src/login.py

# Or directly to dashboard (if authenticated)
python src/main.py

📦 Dependencies
Create a requirements.txt file

tkinter==0.1.0
pymongo==4.5.0
bcrypt==4.0.1
pandas==2.0.3
python-dotenv==1.0.0
openpyxl==3.1.2  # For Excel export

🔧 Configuration
Create a config.py file

import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "LoanManagementDB"

# Collections
USER_COLLECTION = "users"
CUSTOMER_COLLECTION = "customers"
LOAN_COLLECTION = "loans"
PAYMENT_COLLECTION = "payments"

# Application Settings
APP_TITLE = "Loan Management System"
APP_GEOMETRY = "1200x700"s
📦 Dependencies
Create a requirements.txt file:

txt
tkinter==0.1.0
pymongo==4.5.0
bcrypt==4.0.1
pandas==2.0.3
python-dotenv==1.0.0
openpyxl==3.1.2  # For Excel export
🔧 Configuration
Create a config.py file:

python
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "LoanManagementDB"

# Collections
USER_COLLECTION = "users"
CUSTOMER_COLLECTION = "customers"
LOAN_COLLECTION = "loans"
PAYMENT_COLLECTION = "payments"

# Application Settings
APP_TITLE = "Loan Management System"
APP_GEOMETRY = "1200x700"
🗄️ Database Schema
Collections Structure:
Users Collection (users)

username, password_hash, email, created_at, role

Customers Collection (customers)

customer_id, name, email, phone, address, created_date

Loans Collection (loans)

loan_id, customer_id, amount, interest_rate, term_months,
start_date, end_date, status, remaining_balance

Payments Collection (payments)

payment_id, loan_id, amount, payment_date, payment_method, notes

💻 Usage
1. Authentication
Launch login.py to access the system

New users can create accounts via create_account.py

2. Main Dashboard
Navigate between modules: Customers, Loans, Payments, Reports

Quick access to recent activities and statistics

3. Loan Management
python
# Sample loan creation flow
1. Select customer from database
2. Enter loan details (amount, interest, term)
3. Calculate automatic installment plan
4. Save to database with unique loan_id
4. Payment Processing
Select loan from active loans list

Enter payment amount and method

System automatically updates loan balance

Generate payment receipt

🧪 Testing
Run the test suite:

bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_loan_operations.py
🔄 Workflow
text
Login → Dashboard → Select Module → 
(Choose Customer → Create/Manage Loans → Process Payments → Generate Reports)
🚧 Future Enhancements
Short-term Goals (Next 1-2 Months)
Email notifications for due payments

Advanced reporting with charts (Matplotlib/Seaborn)

Multi-user role management (Admin/Staff)

Data backup and restore functionality

Audit trail for all transactions

Long-term Goals
Web version using Flask/Django

Mobile app companion

API for third-party integrations

Automated payment reminders via SMS

AI-based risk assessment for new loans

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open a Pull Request

Code Style
Follow PEP 8 guidelines

Use meaningful variable names

Add docstrings for functions

Write unit tests for new features

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Tkinter Documentation

PyMongo Documentation

MongoDB University

📞 Support
For issues and questions:

Check the Issues page

Create a new issue with detailed description

Email: your.email@example.com

Note: This is a development project. Always backup your data before production use.

text

**Additional files to create:**

**requirements.txt:**
```txt
tkinter==0.1.0
pymongo==4.5.0
bcrypt==4.0.1
pandas==2.0.3
python-dotenv==1.0.0
openpyxl==3.1.2
config.py:
