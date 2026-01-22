# Aegis V Configuration

# Thresholds
RISK_THRESHOLD_BLOCK = 70
RISK_THRESHOLD_AMBIGUOUS = 40

# Layer 1 Settings
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
SIMILARITY_THRESHOLD = 0.85  # Distance threshold for declaring a match

# Simulation Settings
SIMULATION_MODE = True  # If True, uses mocks for heavy models to ensure the demo runs effectively on all envs
