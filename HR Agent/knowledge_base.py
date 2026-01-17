import os
import logging
import re
import pickle
from typing import List, Dict
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Verify config import works or just use logging directly
import logging

class KnowledgeBase:
    def __init__(self, embedding_model_name='all-MiniLM-L6-v2', index_path='faiss_index.bin', docs_path='documents.pkl'):
        self.embedding_model_name = embedding_model_name
        self.encoder = None
        self.vector_store = None
        self.documents = [] 
        self.structured_facts = [] 
        self.index_path = index_path
        self.docs_path = docs_path
        
    def _load_model(self):
        if self.encoder is None:
            logging.info(f"Loading embedding model: {self.embedding_model_name}")
            self.encoder = SentenceTransformer(self.embedding_model_name)

    def load_existing_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            try:
                logging.info(f"Loading existing artifacts from {self.index_path}...")
                self.vector_store = faiss.read_index(self.index_path)
                with open(self.docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                logging.info(f"Loaded {len(self.documents)} documents and index of size {self.vector_store.ntotal}")
                return True
            except Exception as e:
                logging.error(f"Failed to load existing index: {e}")
                return False
        return False

    def ingest_pdf(self, file_path: str):
        # 1. Try Loading first
        if self.load_existing_index():
            return

        # 2. Ingest if no index
        self._load_model()
        logging.info(f"Ingesting file: {file_path}")
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return
            
        try:
            reader = PdfReader(file_path)
            full_text_chunks = []
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # Basic cleaning: remove excessive whitespace, handle hyphens
                    text = re.sub(r'\s+', ' ', text).strip()
                    full_text_chunks.append({"page": i + 1, "text": text})
            
            logging.info(f"Extracted content from {len(full_text_chunks)} pages.")
            self._process_chunks(full_text_chunks, os.path.basename(file_path))
            
        except Exception as e:
            logging.error(f"Error reading PDF: {e}")

    def _process_chunks(self, pages_data: List[Dict], source_name: str):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, # Increased chunk size for better context
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        all_splits = []
        for page in pages_data:
            # A. Semantic Splitting
            splits = text_splitter.split_text(page["text"])
            for split in splits:
                all_splits.append({
                    "text": split,
                    "source": source_name,
                    "page": page["page"],
                    "type": "semantic"
                })
            
            # B. Deterministic Extraction (Heuristic)
            lines = page["text"].split('\n')
            for line in lines:
                if re.search(r'(\$|\d+%|\d+\s?days|\d+\s?years|Limit|Eligibility)', line, re.IGNORECASE):
                    self.structured_facts.append({
                        "fact": line.strip(),
                        "source": source_name,
                        "page": page["page"],
                        "type": "deterministic"
                    })
        
        self.documents = all_splits
        logging.info(f"Created {len(self.documents)} semantic chunks.")
        
        self._build_vector_store()
        
    def _build_vector_store(self):
        if not self.documents:
            return
        
        # Batch processing for embeddings
        batch_size = 32
        texts = [doc["text"] for doc in self.documents]
        logging.info(f"Generating embeddings for {len(texts)} chunks...")
        
        self._load_model()
        embeddings = self.encoder.encode(texts, batch_size=batch_size, show_progress_bar=True)
        
        self.vector_store = faiss.IndexFlatL2(embeddings.shape[1])
        self.vector_store.add(embeddings)
        logging.info(f"Vector store built. Index size: {self.vector_store.ntotal}")

        # Save to disk
        try:
            faiss.write_index(self.vector_store, self.index_path)
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            logging.info("Saved index and documents to disk.")
        except Exception as e:
            logging.error(f"Failed to save artifacts: {e}")


    def query_similarity(self, query: str, k=5) -> List[Dict]:
        if self.vector_store is None: return []
        self._load_model()
        query_vec = self.encoder.encode([query], show_progress_bar=False)
        distances, indices = self.vector_store.search(query_vec, k)
        return [self.documents[i] for i in indices[0] if i != -1 and i < len(self.documents)]

    def query_structured(self, query: str) -> List[Dict]:
        # Heuristic keyword match on structured facts
        keywords = query.lower().split()
        results = []
        for fact in self.structured_facts:
            fact_text = fact["fact"].lower()
            if any(k in fact_text for k in keywords):
                results.append(fact)
        return results[:5] 
