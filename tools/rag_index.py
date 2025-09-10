"""
RAG Index Tool for JarvisX
Document indexing and retrieval using FAISS
"""

import os
import json
import pickle
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
import faiss
from loguru import logger
from core.io import FileManager

class RAGIndex:
    """RAG (Retrieval-Augmented Generation) index for document search"""
    
    def __init__(self, index_dir: str, temp_dir: str):
        self.index_dir = Path(index_dir)
        self.temp_dir = Path(temp_dir)
        self.index_file = self.index_dir / "faiss_index.bin"
        self.metadata_file = self.index_dir / "metadata.json"
        self.vectorizer_file = self.index_dir / "vectorizer.pkl"
        
        # Ensure directories exist
        self.index_dir.mkdir(exist_ok=True)
        
        self.file_manager = FileManager(str(self.temp_dir))
        self.index = None
        self.metadata = []
        self.vectorizer = None
        
        # Load existing index if available
        self._load_index()
    
    def add_documents(self, documents: List[Dict], chunk_size: int = 512) -> bool:
        """Add documents to the index"""
        try:
            logger.info(f"Adding {len(documents)} documents to RAG index")
            
            # Process documents into chunks
            chunks = self._chunk_documents(documents, chunk_size)
            
            # Vectorize chunks
            vectors = self._vectorize_chunks(chunks)
            
            # Add to index
            if self.index is None:
                self._create_index(vectors.shape[1])
            
            self.index.add(vectors)
            
            # Update metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    'id': len(self.metadata) + i,
                    'content': chunk['content'],
                    'source': chunk['source'],
                    'chunk_index': chunk['chunk_index'],
                    'total_chunks': chunk['total_chunks'],
                    'metadata': chunk.get('metadata', {})
                }
                self.metadata.append(chunk_metadata)
            
            # Save index and metadata
            self._save_index()
            
            logger.info(f"Successfully added {len(chunks)} chunks to index")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        try:
            if self.index is None or self.vectorizer is None:
                logger.warning("Index not initialized")
                return []
            
            # Vectorize query
            query_vector = self._vectorize_text(query)
            
            # Search index
            distances, indices = self.index.search(query_vector, top_k)
            
            # Retrieve results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.metadata):
                    result = {
                        'rank': i + 1,
                        'score': float(1.0 / (1.0 + distance)),  # Convert distance to similarity score
                        'content': self.metadata[idx]['content'],
                        'source': self.metadata[idx]['source'],
                        'metadata': self.metadata[idx]['metadata']
                    }
                    results.append(result)
            
            logger.info(f"Search completed, found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            return []
    
    def update_document(self, doc_id: str, new_content: str) -> bool:
        """Update a document in the index"""
        try:
            logger.info(f"Updating document: {doc_id}")
            
            # Find document chunks
            chunks_to_update = [i for i, meta in enumerate(self.metadata) 
                              if meta['source'] == doc_id]
            
            if not chunks_to_update:
                logger.warning(f"Document {doc_id} not found in index")
                return False
            
            # Remove old chunks
            self._remove_chunks(chunks_to_update)
            
            # Add updated content
            updated_doc = {
                'id': doc_id,
                'content': new_content,
                'metadata': {}
            }
            
            return self.add_documents([updated_doc])
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the index"""
        try:
            logger.info(f"Removing document: {doc_id}")
            
            # Find document chunks
            chunks_to_remove = [i for i, meta in enumerate(self.metadata) 
                               if meta['source'] == doc_id]
            
            if not chunks_to_remove:
                logger.warning(f"Document {doc_id} not found in index")
                return False
            
            # Remove chunks
            self._remove_chunks(chunks_to_remove)
            
            # Save updated index
            self._save_index()
            
            logger.info(f"Successfully removed document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing document: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get index statistics"""
        try:
            stats = {
                'total_documents': len(set(meta['source'] for meta in self.metadata)),
                'total_chunks': len(self.metadata),
                'index_size': self.index.ntotal if self.index else 0,
                'vector_dimension': self.index.d if self.index else 0,
                'index_file_size': self.index_file.stat().st_size if self.index_file.exists() else 0,
                'metadata_file_size': self.metadata_file.stat().st_size if self.metadata_file.exists() else 0
            }
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
    
    def clear_index(self) -> bool:
        """Clear the entire index"""
        try:
            logger.info("Clearing RAG index")
            
            # Reset index
            self.index = None
            self.metadata = []
            self.vectorizer = None
            
            # Remove index files
            if self.index_file.exists():
                self.index_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            if self.vectorizer_file.exists():
                self.vectorizer_file.unlink()
            
            logger.info("Index cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            return False
    
    def _chunk_documents(self, documents: List[Dict], chunk_size: int) -> List[Dict]:
        """Split documents into chunks"""
        chunks = []
        
        for doc in documents:
            content = doc['content']
            source = doc['id']
            
            # Simple text chunking (can be improved with more sophisticated methods)
            words = content.split()
            total_chunks = (len(words) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_content = ' '.join(chunk_words)
                
                chunk = {
                    'content': chunk_content,
                    'source': source,
                    'chunk_index': i // chunk_size,
                    'total_chunks': total_chunks,
                    'metadata': doc.get('metadata', {})
                }
                chunks.append(chunk)
        
        return chunks
    
    def _vectorize_chunks(self, chunks: List[Dict]) -> np.ndarray:
        """Convert text chunks to vectors"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Initialize vectorizer if not exists
            if self.vectorizer is None:
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                # Fit on all chunks
                all_texts = [chunk['content'] for chunk in chunks]
                self.vectorizer.fit(all_texts)
            
            # Transform chunks
            texts = [chunk['content'] for chunk in chunks]
            vectors = self.vectorizer.transform(texts)
            
            # Convert to dense numpy array
            return vectors.toarray().astype(np.float32)
            
        except ImportError:
            logger.error("scikit-learn not available for vectorization")
            # Fallback to simple hash-based vectors
            return self._fallback_vectorization(chunks)
    
    def _vectorize_text(self, text: str) -> np.ndarray:
        """Vectorize a single text query"""
        try:
            if self.vectorizer is None:
                logger.error("Vectorizer not initialized")
                return np.array([])
            
            vector = self.vectorizer.transform([text])
            return vector.toarray().astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error vectorizing text: {e}")
            return np.array([])
    
    def _fallback_vectorization(self, chunks: List[Dict]) -> np.ndarray:
        """Fallback vectorization using simple hashing"""
        logger.warning("Using fallback vectorization method")
        
        # Simple hash-based vectors (not recommended for production)
        vectors = []
        for chunk in chunks:
            # Create a simple hash-based vector
            vector = np.zeros(128, dtype=np.float32)
            text = chunk['content'].lower()
            
            for i, char in enumerate(text):
                if i >= 128:
                    break
                vector[i] = hash(char) % 100 / 100.0
            
            vectors.append(vector)
        
        return np.array(vectors)
    
    def _create_index(self, dimension: int):
        """Create a new FAISS index"""
        try:
            # Use IndexFlatIP for inner product (cosine similarity)
            self.index = faiss.IndexFlatIP(dimension)
            logger.info(f"Created FAISS index with dimension {dimension}")
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
            raise
    
    def _remove_chunks(self, chunk_indices: List[int]):
        """Remove chunks from index and metadata"""
        try:
            # Remove from metadata (in reverse order to maintain indices)
            for idx in sorted(chunk_indices, reverse=True):
                if idx < len(self.metadata):
                    del self.metadata[idx]
            
            # Rebuild index with remaining vectors
            if self.metadata and self.vectorizer:
                texts = [meta['content'] for meta in self.metadata]
                vectors = self.vectorizer.transform(texts).toarray().astype(np.float32)
                
                # Create new index
                self._create_index(vectors.shape[1])
                self.index.add(vectors)
            
        except Exception as e:
            logger.error(f"Error removing chunks: {e}")
    
    def _save_index(self):
        """Save index and metadata to disk"""
        try:
            # Save FAISS index
            if self.index:
                faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            # Save vectorizer
            if self.vectorizer:
                with open(self.vectorizer_file, 'wb') as f:
                    pickle.dump(self.vectorizer, f)
            
            logger.info("Index saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def _load_index(self):
        """Load existing index from disk"""
        try:
            if not self.index_file.exists() or not self.metadata_file.exists():
                logger.info("No existing index found")
                return
            
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))
            
            # Load metadata
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
            
            # Load vectorizer
            if self.vectorizer_file.exists():
                with open(self.vectorizer_file, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            
            logger.info(f"Loaded existing index with {len(self.metadata)} chunks")
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            # Reset to clean state
            self.index = None
            self.metadata = []
            self.vectorizer = None