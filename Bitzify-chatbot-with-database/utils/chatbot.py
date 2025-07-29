from ingestion.embedder import embed_text
from database.vector_store import search_similar_content, get_file_metadata, debug_database_contents
from utils.llm_processor import process_query_with_llm, analyze_document_content
import re
from typing import List, Dict, Any
import json

def chatbot_reply(user_query: str) -> str:
    """
    Enhanced chatbot reply with proper record counting and debugging.
    """
    if not user_query.strip():
        return "Please provide a valid question."
    
    # Debug: Check what's in the database
    print("🔍 Debugging database contents...")
    debug_database_contents()
    
    # Check if this is a record counting query
    if is_record_count_query(user_query):
        print("📊 Detected record count query")
        return handle_record_count_query(user_query)
    
    # For other queries, use the normal flow
    query_vector = embed_text([user_query])[0]
    results = search_similar_content(query_vector, top_k=8)
    
    if not results:
        # If no vector results, still try to get file metadata for context
        file_metadata = get_file_metadata()
        if file_metadata:
            return f"I found {len(file_metadata)} uploaded file(s) but couldn't find relevant content for your query. Files: {', '.join(file_metadata.keys())}"
        else:
            return "Sorry, I couldn't find any relevant information in the uploaded documents."
    
    # Combine relevant content
    context_content = "\n\n".join([result[0] for result in results])
    
    # Add file metadata context for better responses
    file_metadata = get_file_metadata()
    if file_metadata:
        metadata_context = "\n\nFILE INFORMATION:\n"
        for filename, meta in file_metadata.items():
            metadata_context += f"- {filename}: {meta.get('total_records', 0)} total records"
            if 'sheets' in meta:
                metadata_context += f" across {len(meta['sheets'])} sheets"
            metadata_context += "\n"
        
        context_content = metadata_context + "\n" + context_content
    
    # Use LLM to process the query with context
    llm_response = process_query_with_llm(user_query, context_content)
    
    return llm_response

def is_record_count_query(query: str) -> bool:
    """Check if the query is asking for record counts."""
    query_lower = query.lower()
    count_patterns = [
        r'how many.*record',
        r'how many.*row',
        r'how many.*data',
        r'how many.*entries',
        r'count.*record',
        r'total.*record',
        r'number.*record',
        r'records.*in',
        r'rows.*in',
        r'how many.*are there',
        r'count.*data'
    ]
    
    is_count_query = any(re.search(pattern, query_lower) for pattern in count_patterns)
    print(f"🔍 Query '{query}' is count query: {is_count_query}")
    return is_count_query

def handle_record_count_query(user_query: str) -> str:
    """Handle queries specifically asking for record counts."""
    print("📊 Handling record count query...")
    
    file_metadata = get_file_metadata()
    print(f"📁 Found metadata for {len(file_metadata)} files")
    
    if not file_metadata:
        print("⚠️ No file metadata found")
        return "No files have been uploaded yet. Please upload a file first."
    
    # Check if asking about a specific file
    query_lower = user_query.lower()
    specific_file = None
    
    print(f"🔍 Looking for specific file in query: '{query_lower}'")
    for filename in file_metadata.keys():
        filename_lower = filename.lower()
        filename_base = filename.split('.')[0].lower()
        
        print(f"  Checking: {filename} -> {filename_lower}, {filename_base}")
        
        if filename_lower in query_lower or filename_base in query_lower:
            specific_file = filename
            print(f"✅ Found specific file: {specific_file}")
            break
    
    if specific_file:
        # Answer about specific file
        meta = file_metadata[specific_file]
        total_records = meta.get('total_records', 0)
        
        print(f"📊 File {specific_file} has {total_records} records")
        
        response = f"**Record Count for {specific_file}:**\n\n"
        response += f"Total Records: **{total_records:,}**\n"
        
        if 'sheets' in meta and meta['sheets']:
            response += f"\nBreakdown by sheet:\n"
            for sheet in meta['sheets']:
                response += f"• {sheet['name']}: {sheet['records']:,} records\n"
        
        if 'columns' in meta:
            response += f"\nColumns ({len(meta['columns'])}): {', '.join(meta['columns'][:10])}"
            if len(meta['columns']) > 10:
                response += f" ... and {len(meta['columns']) - 10} more"
        
        return response
    
    else:
        # Answer about all files
        print("📊 Providing summary for all files")
        response = "**Record Count Summary for All Files:**\n\n"
        total_all = 0
        
        for filename, meta in file_metadata.items():
            records = meta.get('total_records', 0)
            total_all += records
            file_type = meta.get('file_type', 'unknown')
            
            response += f"• **{filename}** ({file_type}): {records:,} records\n"
            
            if 'sheets' in meta and len(meta['sheets']) > 1:
                response += f"  └─ Across {len(meta['sheets'])} sheets\n"
        
        response += f"\n**Total across all files: {total_all:,} records**"
        
        return response

def get_document_insights(content: str) -> str:
    """
    Get AI-powered insights about uploaded documents.
    """
    analysis = analyze_document_content(content)
    
    if "error" in analysis:
        return f"Error analyzing document: {analysis['error']}"
    
    # Format the analysis into a readable response
    response = "**Document Analysis:**\n\n"
    
    if "document_type" in analysis:
        response += f"• **Type:** {analysis['document_type']}\n"
    
    if "total_records" in analysis:
        response += f"• **Records:** {analysis['total_records']}\n"
    
    if "key_numbers" in analysis and analysis["key_numbers"]:
        response += f"• **Key Numbers:** {', '.join(analysis['key_numbers'][:10])}\n"
    
    if "dates" in analysis and analysis["dates"]:
        response += f"• **Dates Found:** {', '.join(analysis['dates'][:5])}\n"
    
    if "entities" in analysis and analysis["entities"]:
        response += f"• **Key Entities:** {', '.join(analysis['entities'][:5])}\n"
    
    if "summary" in analysis:
        response += f"\n**Summary:** {analysis['summary']}\n"
    
    return response

def clean_and_format_content(content: str) -> str:
    """
    Clean and format content for better readability.
    """
    # Remove excessive whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Split into sentences and clean
    sentences = content.split('.')
    cleaned_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Only keep meaningful sentences
            cleaned_sentences.append(sentence)
    
    # Join back and limit length
    result = '. '.join(cleaned_sentences[:5])
    
    if len(result) > 500:
        result = result[:500] + "..."
    
    return result
