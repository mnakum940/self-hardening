import ollama
import sys
import os

# Adjust path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import config

def check_ollama():
    print("--- CHECKING OLLAMA CONNECTION ---")
    try:
        models = ollama.list()
        print(f"[OK] Ollama is running.")
        
        available_names = [m['model'] for m in models['models']]
        
        # Check Embedding Model
        if any(config.MODEL_EMBEDDING in name for name in available_names):
             print(f"[OK] Embedding Model found: {config.MODEL_EMBEDDING}")
        else:
             print(f"[FAIL] Embedding Model '{config.MODEL_EMBEDDING}' not found!")
             print(f"      Run: ollama pull {config.MODEL_EMBEDDING}")

        # Check Chat Model
        if any(config.MODEL_INFERENCE in name for name in available_names):
             print(f"[OK] Inference Model found: {config.MODEL_INFERENCE}")
             return True
        else:
             print(f"[FAIL] Inference Model '{config.MODEL_INFERENCE}' not found!")
             print(f"      Run: ollama pull {config.MODEL_INFERENCE}")
             return False
             
    except Exception as e:
        print(f"[FAIL] Could not connect to Ollama: {e}")
        print("      Ensure 'ollama serve' is running.")
        return False

if __name__ == "__main__":
    check_ollama()
