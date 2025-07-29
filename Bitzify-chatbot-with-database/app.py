from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils.file_handler import handle_file_upload
from utils.chatbot import chatbot_reply
from database.vector_store import get_document_stats, get_file_metadata, debug_database_contents

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "DocuChat AI Backend is running!",
        "version": "1.0.0"
    })

@app.route("/upload", methods=["POST"])
def upload_file():
    """Upload and process files"""
    print("📤 Upload endpoint called")
    
    # Check if file is in request
    if 'file' not in request.files:
        print("❌ No file in request")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print("❌ Empty filename")
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file extension
    allowed_extensions = {'.pdf', '.xlsx', '.xls', '.docx', '.txt', '.csv'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        print(f"❌ Unsupported file type: {file_ext}")
        return jsonify({
            "error": f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
        }), 400
    
    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    print(f"💾 Saving file to: {filepath}")
    
    try:
        file.save(filepath)
        print(f"✅ File saved successfully: {file.filename}")
        
        # Process the file
        print(f"🔄 Starting file processing: {file.filename}")
        file_metadata = handle_file_upload(filepath)
        
        print(f"✅ File processing completed for: {file.filename}")
        print(f"📊 Processing result: {file_metadata}")
        
        # Verify metadata was stored
        print("🔍 Verifying stored metadata...")
        stored_metadata = get_file_metadata(file.filename)
        print(f"📊 Retrieved metadata: {stored_metadata}")
        
        # Get the actual metadata for this file
        metadata_info = stored_metadata.get(file.filename, file_metadata)
        
        response_data = {
            "message": f"{file.filename} uploaded and processed successfully.",
            "filename": file.filename,
            "file_type": file_ext,
            "total_records": metadata_info.get('total_records', 0),
            "sheets": len(metadata_info.get('sheets', [])) if 'sheets' in metadata_info else None,
            "columns": len(metadata_info.get('columns', [])) if 'columns' in metadata_info else None,
            "processing_status": "completed",
            "debug_info": {
                "metadata_stored": bool(stored_metadata.get(file.filename)),
                "metadata_keys": list(metadata_info.keys()) if metadata_info else [],
                "processing_metadata": file_metadata,
                "stored_metadata": stored_metadata.get(file.filename, {})
            }
        }
        
        print(f"📤 Sending response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up file if processing failed
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Cleaned up failed file: {filepath}")
        except:
            pass
        
        return jsonify({
            "error": f"Error processing file: {str(e)}",
            "details": "Please check server logs for more information"
        }), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint for querying documents"""
    print("💬 Chat endpoint called")
    
    try:
        data = request.get_json()
        
        if not data:
            print("❌ No JSON data received")
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_query = data.get("message", "")
        
        if not user_query.strip():
            print("❌ Empty message")
            return jsonify({"error": "No message provided"}), 400
        
        print(f"💬 Processing query: '{user_query}'")
        
        # Generate reply using chatbot
        reply = chatbot_reply(user_query)
        
        print(f"✅ Generated reply: {reply[:100]}...")
        
        response_data = {
            "reply": reply,
            "query": user_query,
            "powered_by": "Groq LLM with Enhanced Metadata",
            "timestamp": str(os.times())
        }
        
        print(f"📤 Sending chat response")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": f"Error generating response: {str(e)}",
            "details": "Please check server logs for more information"
        }), 500

@app.route("/files", methods=["GET"])
def get_files():
    """Get information about all uploaded files"""
    print("📁 Files endpoint called")
    
    try:
        file_metadata = get_file_metadata()
        print(f"📁 Retrieved metadata for {len(file_metadata)} files")
        
        return jsonify({
            "files": file_metadata,
            "total_files": len(file_metadata),
            "status": "success"
        })
        
    except Exception as e:
        print(f"❌ Error getting file information: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": f"Error getting file information: {str(e)}",
            "files": {},
            "total_files": 0
        }), 500

@app.route("/debug", methods=["GET"])
def debug_endpoint():
    """Debug endpoint to check database contents"""
    print("🔍 Debug endpoint called")
    
    try:
        debug_database_contents()
        file_metadata = get_file_metadata()
        
        return jsonify({
            "status": "debug_complete",
            "file_metadata": file_metadata,
            "total_files": len(file_metadata),
            "backend_status": "running",
            "database_status": "connected"
        })
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": f"Debug error: {str(e)}",
            "status": "error"
        }), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 50MB."}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    print("🚀 Starting DocuChat AI Backend...")
    print("📡 Backend will be available at: http://localhost:5000")
    print("🌐 Frontend should connect from: http://localhost:3000")
    print("📁 Upload folder:", UPLOAD_FOLDER)
    
    app.run(debug=True, host="0.0.0.0", port=5000)
