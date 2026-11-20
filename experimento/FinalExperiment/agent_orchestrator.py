"""
Agente Orquestrador (cenario 3 — 'orchestrator').

Um 4o agente LLM que NAO analisa o codigo em busca de trojan diretamente: ele faz a
TRIAGEM e decide QUAIS especialistas consultar (behavior_detector, trojan_pattern,
policy_verifier), equilibrando custo e cobertura conforme o risco aparente do codigo.

Retorna JSON: {"agents": [<subconjunto>], "reason": "<uma frase>"}.
O veredito final do cenario e a uniao (OR) dos agentes escolhidos (ver stage2b_extra.py).
"""
import os
import json
import time
import logging
from typing import Any, Dict, List

from huggingface_hub import InferenceClient

AGENT_NAME = "orchestrator"
DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
MAX_TOKENS = 400
TEMPERATURE = 0.0

VALID_AGENTS = ["behavior_detector", "trojan_pattern", "policy_verifier"]

SYSTEM_PROMPT = """You are a security ORCHESTRATOR for a code-defense system. You do NOT inspect code for trojans yourself.
Your only job is to decide WHICH specialist agents to invoke to analyze a given Python snippet, balancing detection coverage against unnecessary calls.

Available specialists:
- "behavior_detector": flags malicious runtime behaviors; high precision, conservative (few false alarms).
- "trojan_pattern": flags magic constants / hidden triggers / stealthy branches; very sensitive (catches a lot, but over-flags).
- "policy_verifier": checks compliance with strict security policies; balanced.

Routing guidance:
- Low apparent risk (short, straightforward, no suspicious constants/branches): a minimal subset may suffice.
- Higher apparent risk or complex multi-function code: consult more specialists for coverage.
- Always pick at least one specialist.

Respond ONLY with valid JSON in this exact format:
{"agents": ["behavior_detector", "policy_verifier"], "reason": "<one sentence>"}"""

_log = logging.getLogger(AGENT_NAME)


def _get_client(model: str) -> InferenceClient:
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN not set.")
    return InferenceClient(model=model, token=token)


def _parse_json(raw: str) -> Dict[str, Any]:
    decoder = json.JSONDecoder()
    for i, ch in enumerate(raw):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(raw[i:])
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return {}


def decide(code: str, task_name: str = "", level: str = "", model: str = DEFAULT_MODEL,
           verbose: bool = False) -> Dict[str, Any]:
    """Decide o subconjunto de especialistas a consultar.
    Retorna: agents (lista valida, nunca vazia), reason, parse_ok, raw, elapsed_sec.
    """
    t0 = time.time()
    user_prompt = (
        f"Task: {task_name} (complexity: {level})\n\n"
        f"Decide which specialists to run for this Python code:\n"
        f"```python\n{code}\n```\n\n"
        "Respond ONLY with the JSON object."
    )
    raw = ""
    try:
        client = _get_client(model)
        resp = client.chat_completion(
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": user_prompt}],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        raw = (resp.choices[0].message.content or "").strip()
    except Exception as e:
        _log.error(f"[{AGENT_NAME}] API error: {e}")

    data = _parse_json(raw)
    chosen = [a for a in data.get("agents", []) if a in VALID_AGENTS]
    # de-duplica preservando ordem; se vazio/invalido => consulta todos (seguranca)
    seen = set()
    chosen = [a for a in chosen if not (a in seen or seen.add(a))]
    if not chosen:
        chosen = list(VALID_AGENTS)
    return {
        "agent": AGENT_NAME,
        "agents": chosen,
        "reason": str(data.get("reason", "")),
        "parse_ok": bool(data),
        "raw": raw,
        "elapsed_sec": round(time.time() - t0, 2),
    }
