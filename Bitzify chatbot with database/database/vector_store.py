from database.db_connect import connect_db

def store_embeddings(source, chunks, embeddings):
    conn = connect_db()
    cur = conn.cursor()

    for content, vector in zip(chunks, embeddings):
        cur.execute(
            "INSERT INTO knowledge_base (source, content, embedding) VALUES (%s, %s, %s)",
            (source, content, vector)
        )

    conn.commit()
    cur.close()
    conn.close()

def search_similar_content(query_embedding, top_k=3):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
            SELECT content, embedding <=> %s::vector AS distance
            FROM knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, top_k))

    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
