import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration - now using environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:root@localhost:5432/Chatbot')

# Alternative: individual components (if you prefer this approach)
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'Chatbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

print("Database configuration loaded!")

# Embedding model configuration
MODEL_NAME = os.getenv('MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')
EMBEDDING_DIM = int(os.getenv('EMBEDDING_DIM', 384))

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found in environment variables!")
    print("Please get your free API key from https://console.groq.com")
else:
    print("Groq API key loaded successfully!")
