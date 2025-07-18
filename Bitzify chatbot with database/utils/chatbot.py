from ingestion.embedder import embed_text
from database.vector_store import search_similar_content

def chatbot_reply(user_query):
    query_vector = embed_text([user_query])[0]
    results = search_similar_content(query_vector)
    if results:
        return results[0][0]
    return "Sorry, I couldn't find a relevant answer."
