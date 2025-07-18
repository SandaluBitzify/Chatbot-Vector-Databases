import os
import pandas as pd
from ingestion.extractors import *
from ingestion.embedder import embed_text
from ingestion.sentence_builder import csv_to_sentences
from database.vector_store import store_embeddings

def handle_file_upload(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        text = extract_from_pdf(file_path)
        chunks = [text]
    elif ext in [".xls", ".xlsx"]:
        text = extract_from_excel(file_path)
        chunks = [text]
    elif ext == ".docx":
        text = extract_from_docx(file_path)
        chunks = [text]
    elif ext == ".txt":
        text = extract_from_txt(file_path)
        chunks = [text]
    elif ext == ".csv":
        chunks = csv_to_sentences(file_path)
    else:
        raise ValueError("Unsupported file type")

    embeddings = embed_text(chunks)
    store_embeddings(os.path.basename(file_path), chunks, embeddings)
