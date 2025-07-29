import requests
import json
from config import GROQ_API_KEY, GROQ_MODEL

def process_query_with_llm(user_query: str, context_content: str) -> str:
    """
    Use Groq's free LLM API to process user query with context.
    """
    if not GROQ_API_KEY:
        return "Please set GROQ_API_KEY in your environment variables."
    
    # Create a prompt that combines user query with document context
    prompt = f"""You are a helpful document analysis assistant. Based on the provided document content, answer the user's question accurately and concisely.

Document Content:
{context_content[:4000]}  # Limit context to avoid token limits

User Question: {user_query}

Instructions:
- If the question asks for counting (how many, count, number of), provide the exact number
- If the question asks for specific data, extract and present it clearly
- If the question asks for a summary, provide a concise overview
- If the information is not in the documents, say so clearly
- Format your response in a clear, structured way

Answer:"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,  # Low temperature for factual responses
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            return f"Error from Groq API: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error processing with LLM: {str(e)}"

def analyze_document_content(content: str) -> dict:
    """
    Use LLM to analyze and extract structured information from document content.
    """
    if not GROQ_API_KEY:
        return {"error": "GROQ_API_KEY not set"}
    
    prompt = f"""Analyze the following document content and extract key information in JSON format:

Document Content:
{content[:3000]}

Please extract and return a JSON object with the following structure:
{{
    "document_type": "invoice/report/data/other",
    "key_numbers": ["list of important numbers found"],
    "dates": ["list of dates found"],
    "entities": ["list of important entities/names"],
    "summary": "brief summary of the document",
    "total_records": "estimated number of records/entries"
}}

JSON Response:"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except:
                # If JSON parsing fails, return raw content
                return {"raw_analysis": content}
        else:
            return {"error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}
