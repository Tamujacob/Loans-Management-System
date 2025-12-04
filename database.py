from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "LoanManagementDB"

# Global variable to hold the database connection object
db = None

def connect_to_db():
    """
    Establishes the connection to MongoDB and sets up the global database object.
    """
    global db
    try:
        # 1. Create a MongoClient
        # Added serverSelectionTimeoutMS to prevent indefinite waiting
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # The client will not throw an error until an operation is attempted, 
        # so we attempt a small operation to verify connection
        client.admin.command('ping') 
        
        # 2. Access the specific database and ASSIGN THE GLOBAL VARIABLE
        db = client[DATABASE_NAME]
        
        print(f"Successfully connected to MongoDB: {DATABASE_NAME}")
        
        # Optionally, ensure basic collections (tables) exist
        initialize_collections()
        
    except Exception as e:
        # If connection fails, db remains None, and the error is printed.
        print(f"Error connecting to MongoDB. The server might not be running or the URI is incorrect: {e}")
        # Note: If 'db' fails to be assigned, it remains None, which is why login.py struggles.

def initialize_collections():
    """
    Ensures that the primary collections (equivalent to SQL tables) exist.
    
    PROBLEM FIX: Changed 'if db:' to 'if db is not None:' to avoid the 
    'Database objects do not implement truth value testing' error.
    """
    global db
    # --- FIX APPLIED HERE ---
    if db is not None: 
    # --- END OF FIX ---
        # Collection for customer details and loan applications
        if 'loans' not in db.list_collection_names():
            db.create_collection("loans")
            print("Collection 'loans' created.")

        # Collection for user login credentials
        if 'users' not in db.list_collection_names():
            db.create_collection("users")
            print("Collection 'users' created.")
            
        # You can add indexes here for faster lookups
        db['loans'].create_index([("loan_id", 1)], unique=True)
        db['loans'].create_index([("customer_name", 1)])
        
# Call the connection function when the file is imported
connect_to_db()

# Example usage function (for later integration)
def save_loan_application(data):
    """Inserts a new loan record into the 'loans' collection."""
    global db
    if db is not None:
        try:
            result = db['loans'].insert_one(data)
            return result.inserted_id
        except Exception as e:
            print(f"Error saving data: {e}")
            return None
    return None