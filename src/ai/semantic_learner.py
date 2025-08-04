"""
Semantic learning module for query understanding and improvement.
Handles AI model management and query memory.
"""

import json
import logging
import os
from typing import List, Dict, Optional, Tuple
import numpy as np

from ..core.config import get_settings

logger = logging.getLogger(__name__)

class SemanticLearner:
    """Manages semantic learning for query understanding and improvement."""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.known_queries: List[Dict] = []
        self.known_vectors = None
        self.index = None
        self._initialize_model()
        self._load_memory()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            import torch
            from sentence_transformers import SentenceTransformer, models
            
            # Set offline mode for stability
            os.environ.update({
                'HF_HUB_OFFLINE': '1',
                'TRANSFORMERS_OFFLINE': '1',
                'HF_HUB_DISABLE_PROGRESS_BARS': '1',
                'PYTORCH_ENABLE_MPS_FALLBACK': '1',
                'PYTORCH_MPS_HIGH_WATERMARK_RATIO': '0.0',
                'PYTORCH_DISABLE_MMAP': '1',
                'OMP_NUM_THREADS': '1',
                'MKL_NUM_THREADS': '1',
                'TOKENIZERS_PARALLELISM': 'false',
                'CUDA_VISIBLE_DEVICES': '',
            })
            
            # Load model
            if os.path.exists(self.settings.model.model_path):
                logger.info(f"Loading model from {self.settings.model.model_path}")
                word_embedding_model = models.Transformer(self.settings.model.model_path)
                pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
                self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
            else:
                logger.info("Using default sentence transformer model")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Configure model
            self.model = self.model.to('cpu')
            self.model.eval()
            
            # Disable gradients
            for param in self.model.parameters():
                param.requires_grad = False
            
            logger.info("✅ Semantic model initialized successfully")
            
        except ImportError as e:
            logger.warning(f"⚠️ Semantic learning libraries not available: {e}")
            self.model = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize semantic model: {e}")
            self.model = None
    
    def _load_memory(self):
        """Load existing query memory."""
        if not self.model:
            return
        
        try:
            memory_file = self.settings.data_dir / "query_memory.json"
            vectors_file = self.settings.data_dir / "query_vectors.npy"
            
            if memory_file.exists() and vectors_file.exists():
                with open(memory_file, 'r') as f:
                    self.known_queries = json.load(f)
                
                self.known_vectors = np.load(vectors_file)
                
                if self.known_vectors is not None and self.known_vectors.shape[0] > 0:
                    import faiss
                    dimension = self.known_vectors.shape[1]
                    self.index = faiss.IndexFlatL2(dimension)
                    vectors_cpu = self.known_vectors.astype('float32')
                    self.index.add(vectors_cpu)
                    logger.info(f"🧠 Loaded {len(self.known_queries)} queries from memory")
            else:
                logger.info("🧠 Starting with empty query memory")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not load query memory: {e}")
            self.known_queries = []
            self.known_vectors = None
            self.index = None
    
    def _save_memory(self):
        """Save query memory to disk."""
        if not self.model:
            return
        
        try:
            memory_file = self.settings.data_dir / "query_memory.json"
            vectors_file = self.settings.data_dir / "query_vectors.npy"
            
            with open(memory_file, 'w') as f:
                json.dump(self.known_queries, f, indent=2)
            
            if self.known_vectors is not None:
                np.save(vectors_file, self.known_vectors)
                
            logger.info("💾 Query memory saved successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save query memory: {e}")
    
    def add_query_feedback(self, original_question: str, sql_query: str, 
                          was_helpful: bool = True, improvement_suggestion: str = None,
                          chart_type: str = None) -> None:
        """Add query feedback to memory."""
        if not self.model:
            logger.info("📝 Feedback noted (semantic learning not available)")
            return
        
        try:
            # Encode the query
            import torch
            with torch.no_grad():
                self.model.eval()
                vector = self.model.encode([original_question])[0]
            
            # Store query information
            query_info = {
                'question': original_question,
                'sql_query': sql_query,
                'was_helpful': was_helpful,
                'improvement_suggestion': improvement_suggestion,
                'chart_type': chart_type,
                'timestamp': str(np.datetime64('now'))
            }
            
            self.known_queries.append(query_info)
            
            # Update vectors
            if self.known_vectors is None:
                self.known_vectors = vector.reshape(1, -1)
            else:
                self.known_vectors = np.vstack([self.known_vectors, vector])
            
            # Update index
            if self.index is not None:
                import faiss
                self.index.add(vector.reshape(1, -1).astype('float32'))
            
            # Save to disk
            self._save_memory()
            
            feedback_type = "positive" if was_helpful else "negative"
            logger.info(f"🧠 Added {feedback_type} feedback to memory")
            
        except Exception as e:
            logger.error(f"❌ Failed to add query feedback: {e}")
    
    def get_similar_queries(self, question: str, threshold: float = 0.8) -> List[Dict]:
        """Get similar queries from memory."""
        if not self.model or not self.index:
            return []
        
        try:
            # Encode the question
            import torch
            with torch.no_grad():
                self.model.eval()
                query_vector = self.model.encode([question])[0]
            
            # Search for similar queries
            D, I = self.index.search(query_vector.reshape(1, -1).astype('float32'), k=5)
            
            similar_queries = []
            for i, distance in zip(I[0], D[0]):
                if distance < threshold and i < len(self.known_queries):
                    similar_queries.append(self.known_queries[i])
            
            return similar_queries
            
        except Exception as e:
            logger.error(f"❌ Failed to get similar queries: {e}")
            return []
    
    def get_improvement_suggestions(self, question: str, threshold: float = 0.85) -> List[str]:
        """Get improvement suggestions based on similar failed queries."""
        similar_queries = self.get_similar_queries(question, threshold)
        
        suggestions = []
        for query in similar_queries:
            if not query.get('was_helpful', True) and query.get('improvement_suggestion'):
                suggestions.append(query['improvement_suggestion'])
        
        return list(set(suggestions))  # Remove duplicates

# Global semantic learner instance
semantic_learner = SemanticLearner()

def get_semantic_learner() -> SemanticLearner:
    """Get the global semantic learner instance."""
    return semantic_learner 