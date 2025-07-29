from sentence_transformers import SentenceTransformer
from config import MODEL_NAME

model = SentenceTransformer(MODEL_NAME)

def embed_text(texts):
    return model.encode(texts).tolist()
