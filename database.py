import datetime
import sys
from collections import defaultdict

# --- Import and Configuration ---

# import pymongo and essential BSON classes
try:
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
    # Set this flag only if all necessary imports succeed
    MONGO_AVAILABLE = True 
except ImportError:
    print("FATAL ERROR: 'pymongo' library not found.")
    print("Please install it using: pip install pymongo")
    # Exit gracefully if the core dependency is missing
    sys.exit(1)

# Define validity check for ObjectId
def is_valid_object_id(oid):
    """Checks if a string is a valid MongoDB ObjectId."""
    return ObjectId.is_valid(oid)

# --- CONFIGURATION ---
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "LoanManagementDB"
DB_TIMEOUT_MS = 5000

# Global variable to hold the database connection object
db = None


def initialize_collections():
    """Ensures that the primary collections (tables) exist and sets up non-_id indexes."""
    global db
    if db is not None:
        try:
            # 1. Check/Create Collections
            for name in ['loans', 'users', 'payments']:
                if name not in db.list_collection_names():
                    # This implicitly creates the collection and the mandatory unique _id index
                    db.create_collection(name)
                    print(f"Collection '{name}' created.")

            # 2. Create Indexes for performance
            # Note: create_index is idempotent (safe to call multiple times)

            # CRITICAL FIX: The _id index is created automatically and is always unique.
            # Calling create_index([("_id", 1)], unique=True) causes the error.
            # The line has been REMOVED.
            
            db['loans'].create_index([("customer_name", 1)])
            db['loans'].create_index([("status", 1)])
            db['payments'].create_index([("loan_id", 1)])
            db['payments'].create_index([("payment_date", -1)])
            
            print("All collections and required indexes initialized successfully.")
        except OperationFailure as e:
            # Catch specific pymongo operation errors (e.g., if index creation fails)
            print(f"Error initializing collections/indexes: {e}")
        except Exception as e:
            print(f"Unexpected error during initialization: {e}")


def connect_to_db():
    """Establishes the connection to MongoDB."""
    global db
    
    try:
        # Setting serverSelectionTimeoutMS handles cases where the DB is down
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=DB_TIMEOUT_MS)
        # The 'ping' command checks if the server is actually available
        client.admin.command('ping') 
        db = client[DATABASE_NAME]
        print(f"Successfully connected to MongoDB: {DATABASE_NAME}")
        initialize_collections()
        return True
    except ServerSelectionTimeoutError:
        print(f"Error connecting to MongoDB: Connection timed out after {DB_TIMEOUT_MS}ms.")
        print("Application is running without a live database connection.")
        db = None
        return False
    except ConnectionFailure as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Application is running without a live database connection.")
        db = None
        return False
    except Exception as e:
        print(f"An unexpected error occurred during connection: {e}")
        db = None
        return False
        
# --- Database Functions Required by GUI ---

def save_payment(payment_data):
    """Saves a new payment record using the 'payments' collection."""
    global db
    if db is None: return None
    
    try:
        # Add system-controlled fields
        payment_data['recorded_date'] = datetime.datetime.now()
        # Ensure payment_amount is correctly typed
        payment_data['payment_amount'] = float(payment_data['payment_amount']) 
        
        if 'loan_id' not in payment_data:
            raise ValueError("Payment data is missing 'loan_id'.")
            
        result = db['payments'].insert_one(payment_data)
        
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"Database Error: Failed to save payment: {e}")
        return None

def get_total_paid_for_loan(loan_id):
    """Calculates the sum of all payments for a specific loan using aggregation."""
    global db
    if db is None: return 0.0
    
    try:
        pipeline = [
            # Match documents for the specific loan ID (stored as string in payments)
            {'$match': {'loan_id': loan_id}}, 
            # Group all matched documents and sum the payment_amount field
            {'$group': {
                '_id': '$loan_id',
                'total': {'$sum': '$payment_amount'}
            }}
        ]
        
        results = list(db['payments'].aggregate(pipeline))
        
        if results and 'total' in results[0]:
            return results[0]['total']
        else:
            return 0.0
            
    except Exception as e:
        print(f"Database Error: Failed to calculate total paid: {e}")
        return 0.0

def get_payments_by_loan(loan_id):
    """Retrieves all payment records for a specific loan, sorted by date."""
    global db
    if db is None: return []
    
    try:
        # Find all payments matching the loan_id, sort descending by date
        payments = list(db['payments'].find({'loan_id': loan_id})
                                     .sort([('payment_date', -1), ('recorded_date', -1)]))
        return payments
        
    except Exception as e:
        print(f"Database Error: Failed to retrieve payments: {e}")
        return []

def update_loan_status(loan_id, status):
    """Updates the status of a loan in the 'loans' collection."""
    global db
    if db is None: return False
    
    try:
        # Convert string ID to ObjectId for lookup in the 'loans' collection
        query_id = ObjectId(loan_id) if is_valid_object_id(loan_id) else loan_id
        
        result = db['loans'].update_one(
            {'_id': query_id}, 
            {'$set': {'status': status}}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"Database Error: Failed to update loan status for {loan_id}: {e}")
        return False
        
# --- NEW FUNCTIONS FOR LoanDetailsViewer ---

def get_loan_by_id(loan_id):
    """Retrieves a single loan document by its unique ID."""
    global db
    if db is None: return None
    
    try:
        # Convert string ID to ObjectId for lookup in the 'loans' collection
        query_id = ObjectId(loan_id) if is_valid_object_id(loan_id) else loan_id
        
        loan = db['loans'].find_one({'_id': query_id})
        
        if loan and isinstance(loan.get('_id'), ObjectId):
            # Convert ObjectId back to string for GUI display consistency
            loan['_id'] = str(loan['_id'])
        
        return loan
        
    except Exception as e:
        print(f"Database Error: Failed to retrieve loan by ID {loan_id}: {e}")
        return None

def update_loan_details(loan_id, updated_data):
    """Updates multiple fields of a specific loan document."""
    global db
    if db is None: return False
    
    try:
        # Convert string ID to ObjectId for lookup in the 'loans' collection
        query_id = ObjectId(loan_id) if is_valid_object_id(loan_id) else loan_id
        
        result = db['loans'].update_one(
            {'_id': query_id}, 
            {'$set': updated_data}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"Database Error: Failed to update loan details for {loan_id}: {e}")
        return False


# Establish connection when the module is imported
connect_to_db()