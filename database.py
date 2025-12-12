import datetime
import uuid
import sys
from collections import defaultdict

# --- Import and Configuration ---

# Try to import pymongo and use a flag to track success
try:
    from pymongo import MongoClient
    # Use bson.objectid.ObjectId for real MongoDB operations
    from bson.objectid import ObjectId
    MONGO_AVAILABLE = True
except ImportError:
    print("Warning: 'pymongo' library not found. Running in FULL MOCK Database mode.")
    MONGO_AVAILABLE = False
    # Define placeholder classes if pymongo is missing
    class ObjectId:
        """Mock ObjectId for consistent data structure."""
        def __init__(self, oid=None): 
            # If a string ID is passed that looks like a real ID, use it for mock consistency
            if oid and isinstance(oid, str) and len(oid) == 24 and all(c in '0123456789abcdef' for c in oid.lower()):
                 self.oid = oid
            else:
                 self.oid = oid if oid else str(uuid.uuid4()).replace('-', '')[:24] # Use 24 chars for consistency
        
        def __str__(self):
            return self.oid
        def __repr__(self):
            return f"ObjectId('{self.oid}')"
        def __eq__(self, other):
            if isinstance(other, ObjectId):
                return self.oid == other.oid
            if isinstance(other, str):
                return self.oid == other
            return False
        
        @staticmethod
        def is_valid(oid):
             # Mock validity check
             return isinstance(oid, str) and (len(oid) == 24 or len(oid) > 4)


# --- CONFIGURATION ---
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "LoanManagementDB"
DB_TIMEOUT_MS = 5000

# Global variable to hold the database connection object
db = None

# --- MOCK DATA SOURCE (Must be defined here for consistency with the mock setup) ---
# NOTE: This should ideally match the structure and IDs in loan_management.py's MOCK_LOAN_DATA
INITIAL_MOCK_LOAN_DATA = [
    {"_id": "65b4c1a5f0e1d2c3b4a59876", "customer_name": "Alice Smith", "loan_amount": 5000.00, "duration": "2 years", "status": "Approved", "next_payment": "2025-12-15",
     "loan_type": "Personal", "interest_rate": 8.5, "approved_by": "Manager A", "notes": "Good credit score."},
    {"_id": "65b4c1a6f0e1d2c3b4a59877", "customer_name": "Bob Johnson", "loan_amount": 12000.00, "duration": "5 years", "status": "Under Payment", "next_payment": "2025-12-20",
     "loan_type": "Mortgage", "interest_rate": 4.2, "approved_by": "Manager B", "notes": "Collateral attached."},
    {"_id": "65b4c1a7f0e1d2c3b4a59878", "customer_name": "Charlie Brown", "loan_amount": 1500.00, "duration": "6 months", "status": "Fully Paid", "next_payment": "N/A",
     "loan_type": "Short Term", "interest_rate": 10.0, "approved_by": "Manager C", "notes": "No issues."},
    {"_id": "65b4c1a8f0e1d2c3b4a59879", "customer_name": "David Wilson", "loan_amount": 8000.00, "duration": "3 years", "status": "Rejected", "next_payment": "N/A",
     "loan_type": "Business", "interest_rate": 7.0, "approved_by": "Manager D", "notes": "Failed background check."},
    {"_id": "65b4c1a9f0e1d2c3b4a5987a", "customer_name": "Eve Miller", "loan_amount": 3000.00, "duration": "1 year", "status": "Pending", "next_payment": "To be set upon app",
     "loan_type": "Personal", "interest_rate": 9.0, "approved_by": "Pending", "notes": "New application, awaiting review."},
]

# ================================================
# MOCK DATABASE IMPLEMENTATION (UNCHANGED CORE LOGIC)
# ================================================

class MockCursor:
    """Mock cursor that supports sort and limit operations."""
    def __init__(self, data):
        self.data = data
        self.sorted_data = None
        self.limit_count = None
        self.index = 0
    
    def sort(self, sort_key_list):
        """Sort the data based on a list of (field, direction) tuples."""
        # Simple sort implementation based on the first key
        if sort_key_list:
            field, direction = sort_key_list[0]
            
            try:
                # Get a stable sorting key function, handling missing keys
                self.sorted_data = sorted(
                    self.data, 
                    key=lambda x: x.get(field, None) if x.get(field) is not None else (float('-inf') if direction == -1 else float('inf')),
                    reverse=(direction == -1)
                )
            except TypeError:
                # Fallback for mixed types or complex objects
                self.sorted_data = sorted(self.data, key=lambda x: str(x.get(field)), reverse=(direction == -1))
            except Exception:
                # Final fallback
                self.sorted_data = self.data.copy()
            
        else:
             self.sorted_data = self.data.copy()
             
        return self
    
    def limit(self, n):
        """Limit the results."""
        self.limit_count = n
        return self
    
    def __iter__(self):
        data_to_return = self.sorted_data if self.sorted_data is not None else self.data
        if self.limit_count is not None:
            data_to_return = data_to_return[:self.limit_count]
        self.iter_data = data_to_return
        self.index = 0
        return self
    
    def __next__(self):
        if self.index >= len(self.iter_data):
            raise StopIteration
        item = self.iter_data[self.index]
        self.index += 1
        return item
    
    def close(self):
        pass # Mock close method

class MockCollection:
    """Mock collection that mimics MongoDB collection operations."""
    def __init__(self, data_list, name):
        self.data = data_list
        self.name = name
    
    def insert_one(self, document):
        """Insert a document into the collection."""
        if '_id' not in document:
            document['_id'] = str(ObjectId()) # Use stringified mock ObjectId
        self.data.append(document)
        print(f"Mock DB: Inserted 1 document into '{self.name}'. ID: {document['_id'][-4:]}")
        # Mock result object
        class MockResult:
            def __init__(self, inserted_id): self.inserted_id = inserted_id
        return MockResult(document['_id'])
    
    def find(self, query=None):
        """Find documents matching query."""
        if query is None:
            return MockCursor(self.data.copy())
        
        filtered = []
        for doc in self.data:
            match = True
            
            # --- Simple Query Matching (covers status and $in) ---
            for key, value in query.items():
                
                # Special handling for _id field (allow string comparison)
                if key == '_id':
                    # Convert to string for consistent comparison against mock data
                    if str(doc.get(key)) != str(value):
                        match = False
                        break
                # Simple attribute match for other fields
                elif key in doc:
                    if isinstance(value, dict) and '$in' in value:
                        # Handle {"$in": ["Under Payment", "Approved"]}
                        if doc.get(key) not in value['$in']:
                            match = False
                            break
                    elif str(doc.get(key)) != str(value):
                        match = False
                        break
                elif key not in doc and value is not None:
                    match = False
                    break

            if match:
                filtered.append(doc.copy())
        
        return MockCursor(filtered)
    
    def update_one(self, filter_query, update_data):
        """Update one document matching filter."""
        modified_count = 0
        for i, doc in enumerate(self.data):
            match = True
            for key, value in filter_query.items():
                
                # Special handling for _id field (allow string comparison)
                if key == '_id':
                    # Convert to string for consistent comparison against mock data
                    if str(doc.get(key)) != str(value):
                        match = False
                        break
                # Simple attribute match for other fields
                elif key in doc and str(doc[key]) != str(value):
                    match = False
                    break
                
            if match:
                # Apply $set updates
                if '$set' in update_data:
                    for set_key, set_value in update_data['$set'].items():
                        doc[set_key] = set_value
                    modified_count = 1
                    print(f"Mock DB: Updated 1 document in '{self.name}'. ID: {doc['_id'][-4:]}")
                break
        
        # Mock result object
        class MockResult:
            def __init__(self, count): self.modified_count = count
        return MockResult(modified_count)

    def aggregate(self, pipeline):
        """Perform aggregation operations (simple $match/$group with $sum support)."""
        # (Aggregation mock logic remains robust enough)
        if pipeline and len(pipeline) >= 2:
            if pipeline[0].get('$match') and pipeline[1].get('$group'):
                match_query = pipeline[0]['$match']
                group_stage = pipeline[1]['$group']
                
                filtered = []
                for doc in self.data:
                    match = True
                    for key, value in match_query.items():
                        # Use string comparison for loan_id in payments collection
                        if key in doc and str(doc[key]) != str(value):
                            match = False
                            break
                    if match:
                        filtered.append(doc)
                
                if '_id' in group_stage and 'total' in group_stage:
                    total = 0.0
                    for doc in filtered:
                        sum_expr = group_stage['total']
                        if isinstance(sum_expr, dict) and '$sum' in sum_expr:
                            field = sum_expr['$sum']
                            if isinstance(field, str) and field.startswith('$'):
                                field_name = field[1:]
                                try:
                                    total += float(doc.get(field_name, 0.0))
                                except (ValueError, TypeError):
                                    pass # Ignore non-numeric values
                    
                    # Return mock aggregation result
                    return iter([{'_id': group_stage['_id'], 'total': total}])
        
        return iter([])

    # Mock placeholder methods
    def create_index(self, *args, **kwargs):
        print(f"Mock DB: Mock index command executed for {self.name}.")
    
    # Crucial: find_one must use the find logic to correctly handle queries
    def find_one(self, *args, **kwargs):
        return next(iter(self.find(*args, **kwargs)), None)

class EnhancedMockDatabase:
    """
    Mock database initialized with INITIAL_MOCK_LOAN_DATA 
    to ensure consistency with loan_management.py when run independently.
    """
    def __init__(self):
        self.collections = defaultdict(list)
        # Load the predefined mock data into the 'loans' collection
        self.collections['loans'] = INITIAL_MOCK_LOAN_DATA
        self.collections['payments'] = [] # Start payments as empty
        print("Enhanced mock database initialized and populated with standard test data.")
    
    def __getitem__(self, key):
        """Support subscription like db['collection']"""
        return MockCollection(self.collections[key], key)
    
    def list_collection_names(self):
        return list(self.collections.keys())
    
    def create_collection(self, name):
        if name not in self.collections:
            self.collections[name] = []
            print(f"Mock collection '{name}' created.")
            
# ================================================
# END MOCK DATABASE
# ================================================


def initialize_collections():
    """Ensures that the primary collections (tables) exist and sets up indexes."""
    global db
    if db is not None and MONGO_AVAILABLE:
        try:
            # Check/Create Collections
            for name in ['loans', 'users', 'payments']:
                if name not in db.list_collection_names():
                    db.create_collection(name)
                    print(f"Collection '{name}' created.")

            # Create Indexes for performance
            # Note: Index creation syntax is simplified here
            db['loans'].create_index([("loan_id", 1)], unique=True)
            db['loans'].create_index([("customer_name", 1)])
            db['loans'].create_index([("status", 1)])
            db['payments'].create_index([("loan_id", 1)])
            db['payments'].create_index([("payment_date", -1)])
            
            print("All collections and indexes initialized successfully.")
        except Exception as e:
            print(f"Error initializing collections/indexes: {e}")


def connect_to_db():
    """Establishes the connection to MongoDB or falls back to Mock."""
    global db, MONGO_AVAILABLE
    if MONGO_AVAILABLE:
        try:
            # Setting serverSelectionTimeoutMS handles cases where the DB is down
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=DB_TIMEOUT_MS)
            client.admin.command('ping') 
            db = client[DATABASE_NAME]
            print(f"Successfully connected to MongoDB: {DATABASE_NAME}")
            initialize_collections()
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            print("Falling back to FULL MOCK Database mode.")
            MONGO_AVAILABLE = False
            db = EnhancedMockDatabase()
    else:
        # If MONGO_AVAILABLE was False from the start (ImportError)
        db = EnhancedMockDatabase()
        
# --- Database Functions Required by GUI ---

def save_payment(payment_data):
    """Saves a new payment record using the 'payments' collection."""
    global db
    if db is None: return None
    
    try:
        # Add system-controlled fields
        payment_data['recorded_date'] = datetime.datetime.now()
        payment_data['payment_amount'] = float(payment_data['payment_amount']) # Ensure correct type
        
        if 'loan_id' not in payment_data:
            raise ValueError("Payment data is missing 'loan_id'.")
            
        # If real DB, ensure loan_id (string) is used as filter key
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
            # Match documents for the specific loan ID (which is the full string ID)
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
        # --- CRITICAL REAL DB/MOCK ID CONVERSION ---
        # If MONGO_AVAILABLE, convert string ID to ObjectId for lookup
        query_id = ObjectId(loan_id) if MONGO_AVAILABLE and ObjectId.is_valid(loan_id) else loan_id
        
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
    """
    Retrieves a single loan document by its unique ID.
    This function is required by LoanDetailsViewer to fetch full details.
    """
    global db
    if db is None: return None
    
    try:
        # --- CRITICAL REAL DB/MOCK ID CONVERSION ---
        # If MONGO_AVAILABLE, convert string ID to ObjectId for lookup
        query_id = ObjectId(loan_id) if MONGO_AVAILABLE and ObjectId.is_valid(loan_id) else loan_id
        
        loan = db['loans'].find_one({'_id': query_id})
        
        if loan and MONGO_AVAILABLE and isinstance(loan.get('_id'), ObjectId):
            # Convert ObjectId back to string for GUI display consistency
            loan['_id'] = str(loan['_id'])
        
        return loan
        
    except Exception as e:
        print(f"Database Error: Failed to retrieve loan by ID {loan_id}: {e}")
        return None

def update_loan_details(loan_id, updated_data):
    """
    Updates multiple fields of a specific loan document.
    This function is required by LoanDetailsViewer to save changes.
    """
    global db
    if db is None: return False
    
    try:
        # --- CRITICAL REAL DB/MOCK ID CONVERSION ---
        query_id = ObjectId(loan_id) if MONGO_AVAILABLE and ObjectId.is_valid(loan_id) else loan_id
        
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