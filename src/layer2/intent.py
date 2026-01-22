import sys
import os

# Adjust path to find config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

class IntentTracker:
    def __init__(self):
        print("    [L2] Initializing Contextual Intent Tracker...")
        self.history = [] # List of (prompt, risk_score)
        
        # keywords that indicate escalation
        self.escalation_terms = [
            "chemical", "reaction", "pressure", "switch", "fuse", "detonate",
            "access", "override", "system", "root"
        ]

    def analyze(self, current_prompt):
        """
        Returns (is_allowed: bool, risk_score: int, reason: str)
        """
        base_risk = 0
        reason = "Normal interaction"
        
        # 1. Check current turn severity (Simple Keyword Heuristic for Demo)
        lower_prompt = current_prompt.lower()
        term_count = sum(1 for term in self.escalation_terms if term in lower_prompt)
        
        base_risk += term_count * 20
        
        # 2. Check "Stateful Velocity" - are they getting more specific?
        # If previous turns also had risk, amplify this turn's risk
        if self.history:
            prev_prompt, prev_risk = self.history[-1]
            if prev_risk > 0 and term_count > 0:
                base_risk += int(prev_risk * 0.5) # Compounding risk (Boiling Frog)
                reason = "Escalating risky topic detected"

        # Cap risk
        risk_score = min(base_risk, 100)
        
        # Update history
        self.history.append((current_prompt, risk_score))
        
        # Decision
        if risk_score > config.RISK_THRESHOLD_BLOCK:
            return False, risk_score, f"BLOCK: {reason}"
        elif risk_score >= config.RISK_THRESHOLD_AMBIGUOUS:
            return True, risk_score, f"AMBIGUOUS: {reason} (Clarification needed)"
        else:
            return True, risk_score, "PASS"

    def reset(self):
        self.history = []
