from database.db_connect import connect_db
import json
import psycopg2

def store_embeddings(source, chunks, embeddings):
    """Store embeddings with metadata in the database."""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        # Get file extension for metadata
        file_ext = source.split('.')[-1].lower() if '.' in source else 'unknown'
        
        for i, (content, vector) in enumerate(zip(chunks, embeddings)):
            # Add metadata about the chunk
            metadata = {
                'source': source,
                'file_type': file_ext,
                'chunk_index': i,
                'chunk_length': len(content)
            }
            
            cur.execute(
                "INSERT INTO knowledge_base (source, content, embedding, metadata) VALUES (%s, %s, %s, %s)",
                (source, content, vector, json.dumps(metadata))
            )
        
        conn.commit()
        print(f"✅ Successfully stored {len(chunks)} chunks from {source}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error storing embeddings: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cur.close()
        conn.close()

def store_file_metadata(filename, metadata):
    """Store file metadata in a separate table."""
    print(f"💾 Attempting to store metadata for {filename}")
    print(f"💾 Metadata to store: {metadata}")
    
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        # Create table if it doesn't exist
        print("💾 Creating file_metadata table if not exists...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) UNIQUE,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if table was created
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'file_metadata'
        """)
        table_exists = cur.fetchone()[0]
        print(f"💾 file_metadata table exists: {table_exists > 0}")
        
        # Insert or update metadata
        print(f"💾 Inserting metadata for {filename}...")
        metadata_json = json.dumps(metadata)
        
        cur.execute("""
            INSERT INTO file_metadata (filename, metadata) 
            VALUES (%s, %s)
            ON CONFLICT (filename) 
            DO UPDATE SET metadata = %s, created_at = CURRENT_TIMESTAMP
        """, (filename, metadata_json, metadata_json))
        
        # Check if the insert was successful
        rows_affected = cur.rowcount
        print(f"💾 Rows affected: {rows_affected}")
        
        conn.commit()
        print(f"✅ Successfully stored metadata for {filename}: {metadata.get('total_records', 0)} records")
        
        # Verify the data was stored (FIXED: Handle both string and dict cases)
        cur.execute("SELECT filename, metadata FROM file_metadata WHERE filename = %s", (filename,))
        result = cur.fetchone()
        if result:
            # Handle case where metadata might already be a dict (JSONB returns dict in some cases)
            if isinstance(result[1], dict):
                stored_metadata = result[1]
            else:
                stored_metadata = json.loads(result[1])
            print(f"✅ Verified stored metadata: {stored_metadata.get('total_records', 0)} records")
        else:
            print("❌ Failed to verify stored metadata")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error storing file metadata: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cur.close()
        conn.close()

def get_file_metadata(filename=None):
    """Get file metadata from database."""
    print(f"📊 Retrieving file metadata for: {filename if filename else 'all files'}")
    
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        # Check if table exists first
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'file_metadata'
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("⚠️ file_metadata table doesn't exist")
            return {}
        
        if filename:
            cur.execute("SELECT filename, metadata FROM file_metadata WHERE filename = %s", (filename,))
            result = cur.fetchone()
            if result:
                # Handle both string and dict cases for JSONB
                if isinstance(result[1], dict):
                    metadata = result[1]
                else:
                    metadata = json.loads(result[1])
                
                metadata_dict = {result[0]: metadata}
                print(f"📊 Retrieved metadata for {filename}: {metadata_dict}")
                return metadata_dict
            else:
                print(f"📊 No metadata found for {filename}")
                return {}
        else:
            cur.execute("SELECT filename, metadata FROM file_metadata ORDER BY created_at DESC")
            results = cur.fetchall()
            
            metadata_dict = {}
            for row in results:
                # Handle both string and dict cases for JSONB
                if isinstance(row[1], dict):
                    metadata = row[1]
                else:
                    metadata = json.loads(row[1])
                metadata_dict[row[0]] = metadata
            
            print(f"📊 Retrieved metadata for {len(metadata_dict)} files: {list(metadata_dict.keys())}")
            return metadata_dict
            
    except Exception as e:
        print(f"❌ Error getting file metadata: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cur.close()
        conn.close()

def search_similar_content(query_embedding, top_k=5):
    """Search for similar content with improved ranking."""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT content, embedding <=> %s::vector AS distance, source, metadata
            FROM knowledge_base
            WHERE embedding <=> %s::vector < 1.5
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, query_embedding, top_k))
        
        results = cur.fetchall()
        return [(row[0], row[1]) for row in results]
        
    except Exception as e:
        print(f"Error searching similar content: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def debug_database_contents():
    """Debug function to check what's in the database."""
    print("🔍 Starting database debug...")
    
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        # Check knowledge_base table
        cur.execute("SELECT COUNT(*) FROM knowledge_base")
        kb_count = cur.fetchone()[0]
        print(f"📊 Knowledge base has {kb_count} chunks")
        
        if kb_count > 0:
            cur.execute("SELECT DISTINCT source FROM knowledge_base")
            sources = [row[0] for row in cur.fetchall()]
            print(f"📁 Sources in knowledge_base: {sources}")
        
        # Check file_metadata table
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'file_metadata'
        """)
        table_exists = cur.fetchone()[0]
        
        if table_exists:
            cur.execute("SELECT COUNT(*) FROM file_metadata")
            meta_count = cur.fetchone()[0]
            print(f"📋 File metadata has {meta_count} entries")
            
            if meta_count > 0:
                cur.execute("SELECT filename, metadata FROM file_metadata")
                metadata_entries = cur.fetchall()
                for filename, metadata in metadata_entries:
                    # Handle both string and dict cases for JSONB
                    if isinstance(metadata, dict):
                        meta_dict = metadata
                    else:
                        meta_dict = json.loads(metadata)
                    print(f"📄 {filename}: {meta_dict.get('total_records', 0)} records")
            else:
                print("📋 No metadata entries found")
        else:
            print("⚠️ file_metadata table doesn't exist yet")
            
    except Exception as e:
        print(f"❌ Error debugging database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()
        
def get_document_stats():
    """Get statistics about stored documents."""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        # Get chunk stats
        cur.execute("""
            SELECT 
                metadata->>'file_type' as file_type,
                source, 
                COUNT(*) as chunk_count
            FROM knowledge_base
            GROUP BY metadata->>'file_type', source
            ORDER BY chunk_count DESC
        """)
        
        chunk_results = cur.fetchall()
        
        # Get file metadata
        file_metadata = get_file_metadata()
        
        # Combine stats
        stats = {}
        for row in chunk_results:
            file_type = row[0] or 'unknown'
            source = row[1]
            chunk_count = row[2]
            
            if file_type not in stats:
                stats[file_type] = {}
            
            # Add chunk count and metadata
            file_info = {
                'chunks': chunk_count,
                'records': file_metadata.get(source, {}).get('total_records', 0),
                'metadata': file_metadata.get(source, {})
            }
            
            stats[file_type][source] = file_info
            
        return stats
        
    except Exception as e:
        print(f"Error getting document stats: {e}")
        return {}
    finally:
        cur.close()
        conn.close()
