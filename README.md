💰My Loan Management System
A robust desktop application built using Python and Tkinter for efficiently managing, tracking, and calculating interest on loan records with MongoDB integration.

✨ Features
Core Functionality
🔐 User Authentication: Secure login system with password hashing (bcrypt).

📝 Smart Loan Applications: Official loan application form with automated NIN-based customer lookup to prevent duplicate identities and streamline data entry.

🖼️ Collateral Evidence Management: Ability to attach, preview, and delete up to 5 security photos for collateral verification.

📄 Official Documentation: Generate professional, print-ready Word (.docx) documents for loan agreements, complete with company branding and embedded security photos.

💰 Loan Management: Comprehensive loan lifecycle management.

💳 Payment Tracking: Record payments and track outstanding balances.

📊 Interest Calculation: Automatic interest calculation based on terms.

📈 Advanced Analytics: Real-time visual dashboards including "Loan Status Distribution" (Pie Chart) and "Financial Health" (Bar Chart) powered by Matplotlib.

📑 Professional Reporting: Export filtered financial data and visual charts into professional PDF reports using ReportLab.

🔍 Search & Filter: Advanced capabilities to find records by name, status, or specific dates.

♻️ Recycle Bin: A safety feature for keeping and restoring deleted loan records.

Technical Features
🛡️ Secure Password Storage: Bcrypt hashing for enhanced security.

🗄️ MongoDB Integration: NoSQL database for flexible data storage.

📱 Responsive GUI: User-friendly Tkinter interface with scrollable forms and modern styling.

📤 Data Export: Support for Excel and Word document formats.

📊 Real-time Updates: Live data updates across modules.

🏗️ Project Structure
Plaintext

Loan-Management-System/
├── login.py              # Entry point: User authentication & account creation
├── dashboard.py          # Main navigation hub for the application
├── loan_application.py   # NEW: Official loan application form & photo handling
├── reports.py            # Financial analytics, charts, and PDF export logic
├── loan_management.py    # Loan CRUD operations and status tracking
├── database.py           # MongoDB connection settings and activity logs
├── repayment.py          # Payment processing and balance calculation
├── view_loan_details.py  # Expanded view for individual loan files
├── bu logo.png           # Application branding and assets

🚀 Getting Started
Prerequisites
Python 3.8 or higher

MongoDB instance (local or Atlas)

Git (for version control)

Installation
Clone the Repository

Bash

git clone https://github.com/Tamujaco/Loan-Management-System.git
cd Loan-Management-System
Installing dependencies

Bash

pip install -r requirements.txt
Database Setup

Install MongoDB locally or use MongoDB Atlas.

Update database connection in config.py or .env:

Python

MONGO_URI = "mongodb://localhost:27017"  # Local MongoDB
DATABASE_NAME = "LoanManagementDB"
Run System

Bash

# Start with login screen
python login.py
📦 Dependencies
Create a requirements.txt file:

Plaintext

tkinter==0.1.0
pymongo==4.5.0
bcrypt==4.0.1
pandas==2.0.3
python-dotenv==1.0.0
openpyxl==3.1.2
python-docx==1.1.0    # For Word Document generation
Pillow==10.2.0         # For image processing and previews
matplotlib==3.7.2      # For analytics charts
reportlab==4.0.4       # For PDF reporting
🔧 Configuration
Create a config.py file:

Python

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
ACTIVITY_LOGS = "logs"

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

loan_id, customer_name, nin_number, loan_amount, loan_type, duration, collateral, security_photos, payment_plan, status, application_date

Payments Collection (payments)

payment_id, loan_id, amount, payment_date, payment_method, notes

💻 Usage
Authentication: Launch login.py to access the system. New users can create accounts via create_account.py.

Main Dashboard: Navigate between modules: Customers, Loans, Payments, Reports.

Loan Application:

Select customer via NIN Lookup.

Enter details and attach collateral photos.

Preview and manage images.

Submit to Database and generate a signable Word Document.

Payment Processing: Select loan, click on the record repayment button on loan management page which will take you to the repayement page, enter payment amount, and update balance automatically.

🧪 Testing
Run the test suite:

Bash

# Run all tests
python -m pytest tests/
🔄 Workflow
Plaintext

Login → Dashboard → Select Module → 
(Choose Customer → Create/Manage Loans → Process Payments → Generate Reports)
🚧 Future Enhancements
Email notifications for due payments.

Web version using Flask/Django.

Automated payment reminders via SMS.

AI-based risk assessment for new loans.

🤝 Contributing
Fork the repository.

Create a feature branch (git checkout -b feature/AmazingFeature).

Commit changes (git commit -m 'Add AmazingFeature').

Push to branch (git push origin feature/AmazingFeature).

Open a Pull Request.
s.

🙏 Acknowledgments
Tkinter Documentation

PyMongo Documentation

MongoDB University

📞 Support
For issues and questions:

Check the Issues page.

Email: jacobtamukedde@gmail.com
+256 787022284

Note: This is a development project. Always backup your data before production use.
