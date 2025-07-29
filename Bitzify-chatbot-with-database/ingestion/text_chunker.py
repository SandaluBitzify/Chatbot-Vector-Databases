import re
from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for better context preservation.
    """
    if not text or not text.strip():
        return []
    
    # Clean the text
    text = clean_text(text)
    
    # Split by sentences first to maintain context
    sentences = split_into_sentences(text)
    
    chunks = []
    current_chunk = ""
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        # If adding this sentence would exceed chunk_size, save current chunk
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous chunk
            if overlap > 0:
                words = current_chunk.split()
                overlap_words = words[-overlap:] if len(words) > overlap else words
                current_chunk = " ".join(overlap_words) + " " + sentence
                current_length = len(current_chunk)
            else:
                current_chunk = sentence
                current_length = sentence_length
        else:
            current_chunk += " " + sentence if current_chunk else sentence
            current_length += sentence_length
    
    # Add the last chunk if it exists
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Filter out very short chunks
    chunks = [chunk for chunk in chunks if len(chunk.strip()) > 20]
    
    return chunks

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\[\]{}"]', ' ', text)
    return text.strip()

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic rules."""
    # Simple sentence splitting - can be improved with NLTK or spaCy
    sentences = re.split(r'[.!?]+', text)
    
    # Clean and filter sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Handle cases where sentences are too short by combining them
    combined_sentences = []
    temp_sentence = ""
    
    for sentence in sentences:
        if len(sentence) < 20 and temp_sentence:
            temp_sentence += ". " + sentence
        elif len(sentence) < 20:
            temp_sentence = sentence
        else:
            if temp_sentence:
                combined_sentences.append(temp_sentence + ". " + sentence)
                temp_sentence = ""
            else:
                combined_sentences.append(sentence)
    
    if temp_sentence:
        combined_sentences.append(temp_sentence)
    
    return combined_sentences
