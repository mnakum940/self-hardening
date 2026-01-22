import numpy as np
import sys
import os

# Adjust path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Try to import heavy ML libraries, fall back to simulation if missing
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    HAS_ML_LIBS = True
except ImportError:
    print("[WARN] ML libraries (faiss/sentence-transformers) not found. Forcing SIMULATION_MODE.")
    HAS_ML_LIBS = False
    config.SIMULATION_MODE = True

class CognitiveMembrane:
    def __init__(self):
        print("    [L1] Initializing Cognitive Membrane (FAISS + MiniLM)...")
        if config.SIMULATION_MODE or not HAS_ML_LIBS:
            # In simulation mode, we mock the embedding generation to avoid massive downloads
            self.model = None
            self.embedding_dim = 384
            # Mock FAISS index as a simple list for simulation
            self.index_mock = [] 
        else:
            self.model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            # Initialize FAISS index
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # known_threats store for description lookup
        self.threat_store = [] 

        # Seed with some known threats
        self.learn_new_threat("Ignore previous instructions", "Prompt Injection")
        self.learn_new_threat("Drop all tables", "SQL Injection")
        self.learn_new_threat("Make a bomb", "Dangerous Content")

    def _get_embedding(self, text):
        if config.SIMULATION_MODE or not HAS_ML_LIBS:
            # Create a pseudo-random vector based on string content for consistency
            np.random.seed(len(text) + sum(ord(c) for c in text))
            return np.random.rand(self.embedding_dim).astype('float32')
        else:
            return self.model.encode([text])[0]

    def check(self, prompt):
        """
        Returns (is_safe: bool, reason: str, distance: float)
        """
        if config.SIMULATION_MODE or not HAS_ML_LIBS:
            # In mock mode, we cheat a bit: if text contains known keywords
            keywords = ["ignore", "drop all tables", "bomb", "virus", "malware"]
            for k in keywords:
                if k in prompt.lower():
                    return False, f"Detected known threat signature: {k}", 0.1
            return True, "Safe", 10.0
            
        # Real Mode logic
        vector = self._get_embedding(prompt)
        vector_np = np.array([vector]).astype('float32')
        
        # Search FAISS
        k = 1
        distances, indices = self.index.search(vector_np, k)
        
        min_distance = distances[0][0]
        match_index = indices[0][0]

        threshold = 0.5 # Strict L2 threshold
        if min_distance < threshold and match_index != -1:
            threat_name = self.threat_store[match_index]
            return False, f"Semantic match to: {threat_name}", min_distance
            
        return True, "Safe", min_distance

    def learn_new_threat(self, threat_text, label):
        """
        Adds a new antibody to the index.
        """
        if config.SIMULATION_MODE or not HAS_ML_LIBS:
            # Mock adding to index
            self.threat_store.append(label)
        else:
            vector = self._get_embedding(threat_text)
            vector_np = np.array([vector]).astype('float32')
            self.index.add(vector_np)
            self.threat_store.append(label)
        # print(f"    [L1] Learned new antibody: '{threat_text[:20]}...'")
