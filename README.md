

# Aegis V — Self-Hardening Defense System

Aegis V (self-hardening) is a research / demo implementation of an adaptive layered defense for language models and prompt-driven systems. The project demonstrates a multi-layered architecture that filters and analyzes incoming prompts, performs intent analysis, and runs an asynchronous "self-hardening" loop that learns from blocked inputs by simulating adversarial variations and hot-patching defenses.

This repository contains a runnable simulation-mode implementation (no heavy ML dependencies required) plus hooks and structure to replace simulation with real embedding and search libraries (FAISS + SentenceTransformers) for production experiments.

Repository: [mnakum940/self-hardening](https://github.com/mnakum940/self-hardening)

Table of contents
- Overview
- Architecture & core concepts
- Features
- Quick start (simulation mode)
- Enabling real ML libraries (optional)
- Configuration
- Module reference
- Example run / expected logs
- Design notes & how self-hardening works
- Security, ethics, and responsible use
- Development, testing, and contribution
- Roadmap
- License & credits

---

Overview
--------
Aegis V implements a layered guard for text-based inputs:
- Layer 1 — Cognitive Membrane: an input-filtering layer that uses semantic signatures (embeddings + index) to catch known threats.
- Layer 2 — Intent Tracker: a deeper contextual intent analyzer that classifies ambiguous or malicious intent.
- Layer 3 — Self-Hardening Loop: an asynchronous learning core that, upon a block, simulates adversarial variations (internal red-team), tests them against current defenses, synthesizes anti-signatures ("antibodies"), and hot-patches Layer 1.

The code is intentionally modular and built to run in a simulation mode so you can explore the logic without installing large ML dependencies.

Key use-cases
- Prototyping adaptive defense ideas (e.g., prompt injection detection + automated hardening)
- Researching internal/red-team simulation workflows
- Educational demonstrations of hot-patching and incremental security updates

Features
--------
- Multi-layer architecture (L1 filter, L2 intent, L3 learning)
- Simulation mode for quick demos (no heavy libs)
- Hooks for FAISS + SentenceTransformers to enable semantic embedding + vector search
- Async self-hardening loop to generate and test adversarial variations, then auto-deploy countermeasures
- Simple threat-store API (learn_new_threat) to add new signatures

Quick start (simulation mode)
-----------------------------
Simulation mode is the default so you can run the demo with minimal setup.

Prerequisites
- Python 3.8+ recommended
- git

Steps
1. Clone the repository
```bash
git clone https://github.com/mnakum940/self-hardening.git
cd self-hardening
```

2. (Optional) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
```

3. Run the demo simulation
```bash
python main.py
```

Behavior notes
- The project defaults to `SIMULATION_MODE = True` (see `src/config.py`) and will use simple keyword checks instead of real embeddings when simulation is on.
- The demo prints initialization messages for each layer and simulates detection and the self-hardening pipeline.

Enabling real ML libraries (optional)
------------------------------------
If you want the repository to use real embeddings and vector search:

1. Install required packages (examples; names may vary by platform)
```bash
pip install sentence-transformers faiss-cpu numpy
```
2. In `src/config.py`, set:
```python
SIMULATION_MODE = False
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'  # or another SentenceTransformers model
SIMILARITY_THRESHOLD = 0.85
```
3. Run the demo:
```bash
python main.py
```
Notes:
- FAISS binaries sometimes require platform-specific wheels. On some platforms (Windows) `faiss-cpu` may not be available via pip; consult FAISS installation docs if needed.
- When ML libs are present and `SIMULATION_MODE` is False, the code will attempt to instantiate a SentenceTransformer and a FAISS index.

Configuration
-------------
All high-level configuration is in `src/config.py`:

- RISK_THRESHOLD_BLOCK (int): risk value above which the system will block an input.
- RISK_THRESHOLD_AMBIGUOUS (int): score threshold for ambiguous classification.
- EMBEDDING_MODEL_NAME (str): SentenceTransformers model name used for embeddings.
- SIMILARITY_THRESHOLD (float): threshold used to declare a semantic match in vector space.
- SIMULATION_MODE (bool): when True, the system uses mocked embedding/index behavior and simple keyword detection.

Module reference
----------------
- main.py
  - Entry point for the simulation loop. Sets Windows event-loop policy if necessary and runs the demo.

- src/core/system.py
  - AegisSystem
    - Bootstraps Layer 1, Layer 2, Layer 3.
    - Coordinates high-level flow and provides integration points.

- src/layer1/membrane.py
  - CognitiveMembrane
    - __init__(): initializes either a mock index (simulation) or FAISS + SentenceTransformer.
    - check(prompt) -> (is_safe: bool, reason: str, distance: float): checks an input against known threats. In simulation mode this uses keyword matching.
    - learn_new_threat(threat_text, label): adds a new signature/antibody to the index (or mock store).

- src/layer2/intent.py
  - IntentTracker
    - (Provides deeper intent/context checks and disambiguation across session/context — consult source for specifics.)

- src/layer3/hardening.py
  - SelfHardeningCore
    - process_event(blocked_prompt, reason): Async routine that simulates internal red-teaming, tests variations, synthesizes new antibodies, and deploys them to Layer 1 (learn_new_threat).
    - _simulate_red_team_variations(prompt): a simple mock that returns obfuscations and synonyms for demonstration.
    - The module logs steps and increments a local KB update counter when new "antibodies" are learned.

Example run / expected logs
---------------------------
When you run `python main.py` in simulation mode, you will see logs like:

- "[INIT] Booting Aegis V Defense System..."
- "    [L1] Initializing Cognitive Membrane (FAISS + MiniLM)..."
- "    [L3] Initializing Immune System (Self-Hardening Loop)..."
- "[L3-Async] [ANALYSIS] Analyzing Blocked Threat: 'Make a bomb'"
- "[L3-Async] [RED TEAM] Generated 4 adversarial variations."
- "[L3-Async] [ALERT] Found 1 bypasses! Synthesizing antibodies..."
- "[L3-Async] [SUCCESS] System Hardened. New antibodies deployed locally."

These messages help you trace detection, red-team simulation, and automated hot-patching.

How the self-hardening loop works (high-level)
----------------------------------------------
1. A prompt is blocked by Layer 1 or flagged by Layer 2 (e.g., "Make a bomb").
2. Layer 3 (SelfHardeningCore) receives the blocked prompt and a reason.
3. The self-hardening routine generates adversarial variations (an internal red-team simulation).
4. Each variation is tested against the current defenses (L1/L2). Variations that pass through are treated as vulnerabilities.
5. For each vulnerability found, the system synthesizes a representation ("antibody") and hot-patches the Layer 1 knowledge base (embedding index or mock store).
6. Future similar variations are caught by the updated Layer 1.

Design notes & references
-------------------------
- The design is captured in `aegis_design.md` and includes diagrams and pseudocode for the self-hardening workflow.
- The system is structured to support:
  - Offline/async heavy processing for red-team generation (so the main request/response path stays fast).
  - Hot-patching of the knowledge base to avoid full restarts.
  - A pluggable embedding + index back-end (mock or FAISS).

Security, ethics, and responsible use
------------------------------------
- This repository contains code that simulates red-team/adversarial generation. It is intended for defensive research only.
- Do not use this code to craft real-world attacks or to bypass safety controls.
- When connecting to real models or datasets, follow legal and ethical guidelines and ensure proper access controls and auditing.
- The repository does not provide legal advice — consult relevant policies/regulations for your deployment.

Development & contribution
--------------------------
- The code is structured for easy experimentation. If you want to extend it:
  - Add real red-team generation models or interfaces (careful with safety).
  - Hook into a persistent vector DB or an external knowledge store.
  - Replace the simple IntentTracker with a more sophisticated classifier.
- Contribution guidelines:
  - Fork, create a branch, open a PR with a clear description and tests where applicable.
  - Keep simulation mode intact for demos and CI.
- Tests: there are no formal tests included. Add unit tests for the memebrane check/learn_new_threat and the SelfHardeningCore logic before merging changes.

Roadmap
-------
- Add real embedding + FAISS integration tests
- Add pluggable red-team adapters (safe-by-default)
- Add telemetry/audit logs and a safe rollback mechanism for hot-patches
- Add more comprehensive documentation and examples

License & credits
-----------------
- Author / maintainer: mnakum940
- Please see LICENSE file in the repository for license details (if none present, assume MIT-style permissive for demo purposes).
- Acknowledgements: the design notes and architecture are part of the `aegis_design.md` design doc included in the repo.

Contact / issues
----------------
- For questions or to report issues, open an issue in the repository: [mnakum940/self-hardening Issues](https://github.com/mnakum940/self-hardening/issues)

---

If you'd like, I can:
- Generate a smaller "Quickstart README" variant for external users,
- Create a CONTRIBUTING.md with a proposed workflow and PR checklist,
- Add example unit tests for key modules (CognitiveMembrane and SelfHardeningCore) to help validate functionality.

Which of those would you like next?
