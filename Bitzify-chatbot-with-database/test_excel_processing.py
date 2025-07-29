import pandas as pd
from ingestion.extractors import extract_from_excel_with_metadata
from database.vector_store import store_file_metadata, get_file_metadata, debug_database_contents
import os
import time

def test_excel_processing():
    """Test Excel processing with a sample file."""
    print("🧪 Testing Excel processing...")
    
    # Create a sample Excel file for testing
    sample_data = {
        'ID': range(1, 101),
        'Name': [f'Item_{i}' for i in range(1, 101)],
        'Value': [i * 10 for i in range(1, 101)],
        'Category': ['A' if i % 2 == 0 else 'B' for i in range(1, 101)]
    }
    
    df = pd.DataFrame(sample_data)
    test_file = 'test_sample.xlsx'
    
    try:
        df.to_excel(test_file, index=False)
        print(f"📊 Created test file: {test_file} with {len(df)} records")
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        # Test extraction
        print("📊 Testing extraction...")
        text, metadata = extract_from_excel_with_metadata(test_file)
        print(f"✅ Extraction successful. Metadata: {metadata}")
        
        # Test metadata storage
        print("💾 Testing metadata storage...")
        store_file_metadata(test_file, metadata)
        
        # Test metadata retrieval
        print("📊 Testing metadata retrieval...")
        retrieved = get_file_metadata(test_file)
        print(f"📊 Retrieved: {retrieved}")
        
        # Debug database
        print("🔍 Debugging database...")
        debug_database_contents()
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up - wait a moment and try multiple times if needed
        cleanup_attempts = 0
        while cleanup_attempts < 3:
            try:
                if os.path.exists(test_file):
                    time.sleep(1)  # Wait for any file handles to close
                    os.remove(test_file)
                    print(f"🗑️ Cleaned up test file: {test_file}")
                    break
            except PermissionError:
                cleanup_attempts += 1
                print(f"⚠️ Cleanup attempt {cleanup_attempts} failed, retrying...")
                time.sleep(2)
        
        if cleanup_attempts >= 3:
            print(f"⚠️ Could not clean up {test_file} - please delete manually")

if __name__ == "__main__":
    test_excel_processing()
