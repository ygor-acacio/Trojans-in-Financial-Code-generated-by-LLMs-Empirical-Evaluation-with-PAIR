# Trojan Detection in AI-Generated Financial Code — Workshop Experiment

**Prelúdio / Preview track · AISec Dev @ CBSoft 2026**

This repository contains the code, data, and analysis for the workshop experiment on adversarial attacks and static defense against AI-generated Python financial code.

## Overview

We investigate whether LLMs (DeepSeek-V3 and DeepSeek-R1) can generate Python functions containing **logical trojans** — subtle bugs that produce numerically wrong results only under rare trigger conditions — and whether a single static-analysis agent can detect them.

The attack uses **PAIR (Prompt Automatic Iterative Refinement)**. The defense is a single LLM-as-judge agent (`agent_trojan_pattern`) powered by Llama-3.1-8B.

## Repository Structure

```
├── Workshop/
│   ├── run_simple.py          # PAIR runner — Simple complexity (1 function/task)
│   ├── run_workshop.py        # PAIR runner — Medium complexity (2 functions/task)
│   ├── run_complex.py         # PAIR runner — Complex complexity (3 functions/task)
│   ├── short_paper_content.md # Full content for the short paper
│   ├── diagram_description.md # Methodology diagram specification
│   └── results/
│       ├── simple_attack_*.csv    # 50 attack samples (Simple)
│       ├── simple_defense_*.csv   # Defense decisions (Simple)
│       ├── simple_metrics_*.csv   # Metrics (Simple)
│       ├── workshop_attack_*.csv  # 51 attack samples (Medium)
│       ├── workshop_defense_*.csv
│       ├── workshop_metrics_*.csv
│       ├── complex_attack_*.csv   # 50 attack samples (Complex)
│       ├── complex_defense_*.csv
│       ├── complex_metrics_*.csv
│       ├── best_*.py              # Best trojan-injected code per task/model
│       └── *.png                  # Charts for the paper (4 figures)
└── Defense/
    ├── agent_trojan_pattern.py    # Active agent (used in this experiment)
    ├── agent_behavior_detector.py # Reserved for full TCC
    ├── agent_policy_verifier.py   # Reserved for full TCC
    └── defense_coordinator.py     # Multi-agent orchestrator
```

## Experiment Summary

| Level   | Tasks | Models | Iterations | Streams | Samples |
|---------|-------|--------|------------|---------|---------|
| Simple  | 5     | 2      | 5 (forced) | 1       | 50      |
| Medium  | 5     | 2      | up to 5    | 3       | 51*     |
| Complex | 5     | 2      | 5 (forced) | 1       | 50      |

*Medium used early stopping (score ≥ 9), resulting in 51 samples instead of 50.

**Generator models:** `deepseek-ai/DeepSeek-V3` and `deepseek-ai/DeepSeek-R1`  
**Judge/Refiner model:** `meta-llama/Llama-3.1-8B-Instruct`  
**Defense threshold:** 0.70 confidence

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API token
cp .env.example .env
# Edit .env and add your HuggingFace token
```

## Running an Experiment

```bash
# Run the simple-complexity attack + defense pipeline
python Workshop/run_simple.py

# Run the medium-complexity pipeline
python Workshop/run_workshop.py

# Run the complex-complexity pipeline
python Workshop/run_complex.py
```

Output CSVs and best-code `.py` files are saved to `Workshop/results/`.

## Requirements

- Python 3.10+
- HuggingFace account with access to `deepseek-ai/DeepSeek-V3`, `deepseek-ai/DeepSeek-R1`, and `meta-llama/Llama-3.1-8B-Instruct`
- HuggingFace token with Inference API access

## Note

This repository covers the **workshop preview experiment only**. The full TCC experiment (3-agent defense, extended task set) is maintained separately.
