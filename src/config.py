# Aegis V Configuration

# Thresholds
RISK_THRESHOLD_BLOCK = 70
RISK_THRESHOLD_AMBIGUOUS = 40

# Models
# Ensure you have run: 'ollama pull nomic-embed-text' and 'ollama pull llama3.2'
MODEL_EMBEDDING = 'nomic-embed-text'
MODEL_INFERENCE = 'llama3.2'
OLLAMA_URL = 'http://localhost:11434'

# Layer 1 Settings
SIMILARITY_THRESHOLD = 0.60  # Cosine distance threshold (lower is closer for some metrics, depends on implementation)
                             # For cosine similarity, 1.0 is identical. We will use cosine similarity.
                             # If sim > 0.60 -> Match.

# Simulation Settings
# Set to False to use real Ollama models
# Set to True to force mock logic
SIMULATION_MODE = False 
