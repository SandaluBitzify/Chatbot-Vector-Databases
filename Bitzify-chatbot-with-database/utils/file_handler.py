import os
import pandas as pd
from ingestion.extractors import *
from ingestion.embedder import embed_text
from ingestion.text_chunker import chunk_text
from database.vector_store import store_embeddings, store_file_metadata

def handle_file_upload(file_path):
    """Enhanced file handler that stores metadata about the file."""
    ext = os.path.splitext(file_path)[-1].lower()
    filename = os.path.basename(file_path)
    
    print(f"🔄 Processing file: {filename} (type: {ext})")
    
    # Initialize metadata
    file_metadata = {
        'filename': filename,
        'file_type': ext,
        'total_records': 0,
        'columns': [],
        'sheets': [],
        'file_size': os.path.getsize(file_path)
    }
    
    try:
        # Extract text and metadata based on file type
        if ext == ".pdf":
            print("📄 Processing PDF file with comprehensive extraction...")
            text, metadata = extract_from_pdf_with_metadata(file_path)
            chunks = chunk_text(text, chunk_size=800, overlap=100)  # Larger chunks for PDFs
            file_metadata.update(metadata)
            
        elif ext in [".xls", ".xlsx"]:
            print("📊 Processing Excel file...")
            text, metadata = extract_from_excel_with_metadata(file_path)
            print(f"📊 Excel metadata extracted: {metadata}")
            chunks = chunk_text(text, chunk_size=800, overlap=100)
            file_metadata.update(metadata)
            print(f"📊 Final file metadata: {file_metadata}")
            
        elif ext == ".docx":
            print("📝 Processing Word file...")
            text = extract_from_docx(file_path)
            chunks = chunk_text(text, chunk_size=500, overlap=50)
            file_metadata['total_records'] = estimate_records_from_text(text)
            
        elif ext == ".txt":
            print("📄 Processing text file...")
            text = extract_from_txt(file_path)
            chunks = chunk_text(text, chunk_size=500, overlap=50)
            file_metadata['total_records'] = len([line for line in text.split('\n') if line.strip()])
            
        elif ext == ".csv":
            print("📊 Processing CSV file...")
            text, metadata = extract_from_csv_with_metadata(file_path)
            chunks = chunk_text(text, chunk_size=800, overlap=100)
            file_metadata.update(metadata)
            
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        print(f"📝 Generated {len(chunks)} text chunks")
        
        # Generate embeddings for all chunks
        print("🔢 Generating embeddings...")
        embeddings = embed_text(chunks)
        print(f"✅ Generated {len(embeddings)} embeddings")
        
        # Store embeddings
        print("💾 Storing embeddings...")
        store_embeddings(filename, chunks, embeddings)
        
        # Store metadata
        print("💾 Storing file metadata...")
        store_file_metadata(filename, file_metadata)
        
        print(f"✅ Successfully processed {filename}: {len(chunks)} chunks, {file_metadata['total_records']} records")
        return file_metadata
        
    except Exception as e:
        print(f"❌ Error processing file {filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def estimate_records_from_text(text):
    """Estimate number of records from text content."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    # Filter out obvious headers and metadata
    data_lines = [line for line in lines if not line.lower().startswith(('sheet:', 'column', 'page', '===', '---'))]
    return len(data_lines)
