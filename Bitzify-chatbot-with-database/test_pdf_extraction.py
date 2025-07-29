from ingestion.pdf_extractors import extract_from_pdf_comprehensive
import os

def test_pdf_extraction():
    """Test comprehensive PDF extraction."""
    print("🧪 Testing comprehensive PDF extraction...")
    
    # You can test with any PDF file you have
    test_files = [
        "Void_Bill_Report (11).pdf"  # Replace with your actual PDF file
    ]
    
    for pdf_file in test_files:
        if os.path.exists(pdf_file):
            print(f"\n📄 Testing with: {pdf_file}")
            
            try:
                text, metadata = extract_from_pdf_comprehensive(pdf_file)
                
                print(f"✅ Extraction successful!")
                print(f"📊 Records found: {metadata['total_records']}")
                print(f"📊 Methods used: {metadata['extraction_methods']}")
                print(f"📊 Tables found: {metadata['tables_found']}")
                print(f"📊 Text length: {metadata['text_length']} characters")
                print(f"📄 First 500 characters:\n{text[:500]}...")
                
            except Exception as e:
                print(f"❌ Test failed for {pdf_file}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ Test file {pdf_file} not found")
    
    print("\n🧪 PDF extraction test completed!")

if __name__ == "__main__":
    test_pdf_extraction()
