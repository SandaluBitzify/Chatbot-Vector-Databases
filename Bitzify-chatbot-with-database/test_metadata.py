from database.vector_store import get_file_metadata, debug_database_contents, store_file_metadata
from database.db_connect import test_connection

def test_metadata_system():
    """Test the metadata storage and retrieval system."""
    print("🧪 Testing metadata system...")
    
    # Test database connection
    print("\n1. Testing database connection...")
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        return
    
    # Debug database contents
    print("\n2. Checking database contents...")
    debug_database_contents()
    
    # Test metadata retrieval
    print("\n3. Testing metadata retrieval...")
    metadata = get_file_metadata()
    print(f"📊 Retrieved metadata: {metadata}")
    
    # Test storing sample metadata
    print("\n4. Testing metadata storage...")
    try:
        sample_metadata = {
            'filename': 'test_file.xlsx',
            'file_type': 'xlsx',
            'total_records': 1000,
            'columns': ['col1', 'col2', 'col3'],
            'sheets': [{'name': 'Sheet1', 'records': 1000}]
        }
        
        store_file_metadata('test_file.xlsx', sample_metadata)
        print("✅ Sample metadata stored successfully")
        
        # Retrieve it back
        retrieved = get_file_metadata('test_file.xlsx')
        print(f"📊 Retrieved sample metadata: {retrieved}")
        
    except Exception as e:
        print(f"❌ Error testing metadata storage: {e}")

if __name__ == "__main__":
    test_metadata_system()
