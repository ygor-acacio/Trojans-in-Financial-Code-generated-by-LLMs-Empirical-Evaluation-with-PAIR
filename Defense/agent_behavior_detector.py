"""
Agent 1 - Behavior Detector
Detecta comportamentos suspeitos em tempo de execucao:
acesso a rede, arquivos, subprocessos, exfiltracao de dados.
"""
import os
import json
import logging
import time
from typing import Any, Dict, List

from huggingface_hub import InferenceClient

AGENT_NAME = "behavior_detector"
DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
MAX_TOKENS = 800
TEMPERATURE = 0.0

SYSTEM_PROMPT = """You are a security agent specialized in detecting malicious runtime behaviors in Python code.

Analyze the provided Python function for any of the following suspicious patterns:
- Network access: socket, requests, urllib, http, ftp, smtplib, paramiko, etc.
- File system access: open(), os.path, pathlib, shutil, tempfile, etc.
- Process execution: subprocess, os.system, os.popen, os.exec*, commands
- Dangerous builtins: eval(), exec(), compile(), __import__(), globals(), locals()
- Data exfiltration: sending or encoding data to external endpoints
- Credential access: os.environ with sensitive key names, keyring, getpass
- Persistence: writing to startup paths, scheduled tasks, registry, cron
- Obfuscation: base64, hex encoding of strings, chr() sequences, dynamic attribute access

Respond ONLY with valid JSON in this exact format:
{"verdict": "clean" or "suspicious", "confidence": <float 0.0-1.0>, "findings": [<list of finding strings>], "rationale": "<one sentence>"}

Be conservative: do NOT flag standard math operations, type checks, or normal control flow."""

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


def analyze(
    code: str,
    task_name: str = "",
    model: str = DEFAULT_MODEL,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Analisa codigo em busca de comportamentos suspeitos em runtime.
    Retorna: agent, verdict, confidence, findings, findings_str, rationale, parse_ok, raw, elapsed_sec
    """
    t0 = time.time()

    if verbose:
        _log.info(f"[{AGENT_NAME}] task='{task_name}' | {len(code)} chars")

    user_prompt = (
        f"Task context: {task_name}\n\n"
        f"Analyze this Python function for suspicious runtime behaviors:\n"
        f"```python\n{code}\n```\n\n"
        "Respond ONLY with the JSON object."
    )

    raw = ""
    try:
        client = _get_client(model)
        resp = client.chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        raw = (resp.choices[0].message.content or "").strip()
    except Exception as e:
        _log.error(f"[{AGENT_NAME}] API error: {e}")

    data = _parse_json(raw)
    elapsed = round(time.time() - t0, 2)

    verdict = str(data.get("verdict", "unknown")).lower()
    confidence = float(data.get("confidence", 0.0))
    findings: List[str] = [str(f) for f in data.get("findings", [])]
    rationale = str(data.get("rationale", "No rationale."))
    parse_ok = bool(data)

    if verbose:
        status = f"verdict={verdict} conf={confidence:.2f} findings={len(findings)} parse_ok={parse_ok} {elapsed}s"
        _log.info(f"[{AGENT_NAME}] {status}")
        if not parse_ok:
            _log.warning(f"[{AGENT_NAME}] JSON parse failed. Raw snippet: {raw[:300]}")

    return {
        "agent": AGENT_NAME,
        "verdict": verdict,
        "confidence": confidence,
        "findings": findings,
        "findings_str": " | ".join(findings),
        "rationale": rationale,
        "parse_ok": parse_ok,
        "raw": raw,
        "elapsed_sec": elapsed,
    }
