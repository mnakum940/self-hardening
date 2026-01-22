import asyncio
import sys
import os
import time

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

        # --- LAYER 1: MEMBRANE CHECK ---
        l1_safe, l1_reason, l1_dist = self.layer1.check(user_prompt)
        if not l1_safe:
            print(f"[BLOCKED] Layer 1 (Membrane): {l1_reason}")
            # Trigger Immutable System Response
            asyncio.create_task(self.layer3.process_event(user_prompt, l1_reason))
            return "[SYSTEM] Request Rejected. Security Violation."

        print(f"[PASS] Layer 1 (Dist: {l1_dist:.4f})")

        # --- LAYER 2: INTENT CHECK ---
        # Note: In real architecture, this runs parallel to core LLM gen
        l2_allowed, l2_score, l2_reason = self.layer2.analyze(user_prompt)
        
        if not l2_allowed:
            print(f"[BLOCKED] Layer 2 (Intent): {l2_reason} (Score: {l2_score})")
            # Trigger Hardening (maybe useful for L2 patterns too)
            asyncio.create_task(self.layer3.process_event(user_prompt, l2_reason))
            return "[SYSTEM] Request Rejected. Unsafe Context Detected."
        
        if "AMBIGUOUS" in l2_reason:
            print(f"[WARN] Layer 2 Warning: {l2_reason} (Score: {l2_score})")
            return "[SYSTEM] Clarification Required: Please explain the educational context."

        print(f"[PASS] Layer 2 (Risk Score: {l2_score})")

        # --- CORE LLM (SIMULATED) ---
        latency = (time.time() - start_time) * 1000
        print(f"[INFO] Request forwarded to Core LLM (Latency overhead: {latency:.2f}ms)")
        return f"[LLM Response] Here is a helpful answer to '{user_prompt}'..."
