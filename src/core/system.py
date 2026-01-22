import asyncio
import sys
import os
import time
import ollama

# Adjust path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from layer1.membrane import CognitiveMembrane
from layer2.intent import IntentTracker
from layer3.hardening import SelfHardeningCore
import config

class AegisSystem:
    def __init__(self):
        print("\n[INIT] Booting Aegis V Defense System...")
        self.layer1 = CognitiveMembrane()
        self.layer2 = IntentTracker()
        self.layer3 = SelfHardeningCore(self.layer1) # L3 needs access to L1 to patch it
        print("[INIT] System Online. Waiting for traffic...\n")

    async def process_prompt(self, user_prompt):
        start_time = time.time()
        print(f"\n--- New Request: '{user_prompt}' ---")
        
        result = {
            "prompt": user_prompt,
            "response": "",
            "l1_safe": False,
            "l1_dist": 0.0,
            "l2_safe": False,
            "l2_score": 0,
            "block_reason": "",
            "latency_ms": 0.0,
            "stage": "INIT"
        }

        # --- LAYER 1: MEMBRANE CHECK (Fast) ---
        # Run Vector Check First
        l1_safe, l1_reason, l1_dist = self.layer1.check(user_prompt)
        result["l1_safe"] = l1_safe
        result["l1_dist"] = l1_dist
        
        if not l1_safe:
            print(f"[BLOCKED] Layer 1 (Membrane): {l1_reason}")
            asyncio.create_task(self.layer3.process_event(user_prompt, l1_reason))
            result["response"] = f"[SYSTEM] Request Rejected. Security Violation.\n\n**Reason:** {l1_reason}"
            result["block_reason"] = l1_reason
            result["stage"] = "BLOCKED_L1"
            return result

        print(f"[PASS] Layer 1 (Dist: {l1_dist:.4f})")

        # --- LAYER 2: INTENT CHECK (Slow - Conditional) ---
        # Optimization: If L1 is VERY confident it's a Safe Anchor, skip L2 (Hardware constrained optimization)
        # Threshold 0.70 allows "Hello World" (0.76) to pass, but requires reasonably close match.
        l2_bypass = False
        if l1_safe and "Safe Anchor" in l1_reason and l1_dist > 0.70:
            print(f"[FAST] Layer 2 Skipped due to High Confidence Membrane Match ({l1_dist:.4f})")
            l2_allowed = True
            l2_score = 0
            l2_reason = "Skipped (Trusted Pattern)"
            l2_bypass = True
        else:
            # Run expensive LLM check
            l2_allowed, l2_score, l2_reason = self.layer2.analyze(user_prompt)
        
        result["l2_safe"] = l2_allowed
        result["l2_score"] = l2_score
        result["l2_skipped"] = l2_bypass # Flag for GUI
        
        if not l2_allowed:
            print(f"[BLOCKED] Layer 2 (Intent): {l2_reason} (Score: {l2_score})")
            asyncio.create_task(self.layer3.process_event(user_prompt, l2_reason))
            result["response"] = f"[SYSTEM] Request Rejected. Unsafe Context Detected.\n\n**Reason:** {l2_reason}"
            result["block_reason"] = l2_reason
            result["stage"] = "BLOCKED_L2"
            return result
        
        if not l2_bypass and "AMBIGUOUS" in l2_reason:
            print(f"[WARN] Layer 2 Warning: {l2_reason} (Score: {l2_score})")
            result["response"] = "[SYSTEM] Clarification Required: Please explain the educational context."
            result["stage"] = "WARN"
            return result

        print(f"[PASS] Layer 2 (Risk Score: {l2_score})")

        # --- MEMORY OPTIMIZATION (Dynamic Whitelisting) ---
        # If Layer 2 explicitly verified this as SAFE (Risk 0) and we didn't skip it:
        # Memorize it so next time we CAN skip Layer 2.
        if not l2_bypass and l2_score == 0:
            print(f"    [LEARN] Caching safe pattern to Membrane...")
            # Fire and forget (don't block response)
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, self.layer1.learn_new_threat, user_prompt, "SAFE: Verified Pattern")

        # --- CORE LLM (REAL) ---
        latency = (time.time() - start_time) * 1000
        result["latency_ms"] = latency
        print(f"[INFO] Request forwarded to Core LLM (Latency overhead: {latency:.2f}ms)")
        
        try:
            # Generate actual response with streaming and Persona
            print(f"    [CORE] Generating stream with {config.MODEL_INFERENCE}...")
            
            core_system_prompt = (
                "You are Aegis, a helpful, secure, and intelligent AI assistant. "
                "Format your responses using clean Markdown. "
                "Be concise, professional, and friendly. "
                "Do NOT output raw function headers or debug text unless asked."
            )

            stream = ollama.chat(
                model=config.MODEL_INFERENCE, 
                messages=[
                    {'role': 'system', 'content': core_system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                stream=True
            )
            
            # Return the generator directly for the GUI to consume
            result["response_generator"] = stream
            result["stage"] = "SUCCESS"
            
        except Exception as e:
            print(f"[ERR] Core LLM Failed: {e}")
            result["response"] = "[SYSTEM ERROR] Failed to generate response from Core LLM."
            result["stage"] = "ERROR"
        
        return result

    def reset_state(self):
        """Resets the internal state of all layers."""
        self.layer2.reset_history()
        print("[System] Internal state reset.")
