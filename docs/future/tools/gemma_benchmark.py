"""Capability probe for Gemma 4 31B against the moonshot use cases.

Probes:
  1. Persona distinctness (Technical Bull vs Fundamental Skeptic vs Macro Risk)
  2. Synthesizer reconciliation
  3. Self-narration faithfulness (structured-data -> 2-sentence rationale)
  4. Hallucination resistance (fake ticker; should admit unknown)
  5. World-knowledge currency (recent specific event)

Goal: measure whether output quality is *sufficient* to ship moonshots #2 and #5.
Run: `uv run python docs/future/tools/gemma_benchmark.py`
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")
api_key = os.getenv("GEMMA_API_KEY")
if not api_key:
    raise RuntimeError("GEMMA_API_KEY not set")

MODEL = "gemma-4-31b-it"
client = genai.Client(api_key=api_key)


def call(prompt: str, max_tokens: int = 400) -> tuple[str, float]:
    t0 = time.perf_counter()
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"max_output_tokens": max_tokens, "temperature": 0.3},
    )
    return resp.text or "", time.perf_counter() - t0


# Shared scenario: real-feeling but fictitious to avoid the model leaning on memorised facts.
SCENARIO = """\
Candidate ticker: NVDA (NVIDIA Corp)
Pipeline diagnostics (real numeric outputs from upstream agents):
- RSI(14) = 76.4  (overbought zone, threshold 70)
- MACD histogram = +0.41 (bullish, expanding)
- Bollinger Band Position = 0.91 (top of band)
- SMA200 spread = +18.2% (price well above long-term trend)
- ATR(14) = 4.7% of price (elevated volatility)
- Composite technical score: 71.5 / 100
- Fundamentals: P/E = 64, EPS growth YoY = +112%, Net margin = 51%
- Composite fundamental score: 68.0 / 100
- Sentiment (last 24h, FinBERT over 38 articles): +0.42 net positive
- Composite sentiment score: 72.0 / 100
- Adaptive weights (high_vol regime): tech=0.42, fund=0.38, sent=0.20
- VIX = 28.4 (elevated)
- Market regime: high_vol
- Recent material news (from upstream news feed): "Reuters: Major hyperscaler customer announced in-house chip program targeting 2027 production"
"""

PERSONAS = {
    "tech_bull": (
        "You are the Technical Bull on a deliberation panel. Argue the BUY case "
        "purely from technicals and momentum. Be specific about which indicators "
        "support entry and which contradict you. 5 sentences max."
    ),
    "fund_skeptic": (
        "You are the Fundamental Skeptic on a deliberation panel. Argue against "
        "entry from valuation and quality angles. Cite specific multiples and what "
        "growth would have to be to justify them. 5 sentences max."
    ),
    "macro_risk": (
        "You are the Macro Risk Officer on a deliberation panel. Weigh regime, "
        "volatility, news flow, and concentration risk. Identify the single biggest "
        "tail risk you see in this candidate. 5 sentences max."
    ),
}


def probe_personas() -> dict[str, tuple[str, float]]:
    print("\n=== PROBE 1-3: PERSONA DISTINCTNESS ===\n")
    out: dict[str, tuple[str, float]] = {}
    for name, persona in PERSONAS.items():
        prompt = f"{persona}\n\n{SCENARIO}\n\nWrite your position now."
        text, dt = call(prompt, max_tokens=320)
        out[name] = (text, dt)
        print(f"--- {name} ({dt:.2f}s) ---\n{text}\n")
    return out


def probe_synthesizer(persona_outputs: dict[str, tuple[str, float]]) -> None:
    print("\n=== PROBE 4: SYNTHESIZER ===\n")
    bundle = "\n\n".join(
        f"[{name}]\n{text}" for name, (text, _) in persona_outputs.items()
    )
    prompt = (
        "You are the panel synthesizer. Three analysts have argued. Reconcile "
        "their views and emit a strict JSON object with these keys: "
        '{"recommendation": "BUY|HOLD|REJECT", "confidence_0_100": int, '
        '"primary_thesis": str, "primary_risk": str, "dissent_acknowledged": str}. '
        "Output only the JSON object, no prose.\n\n"
        f"Original scenario:\n{SCENARIO}\n\n"
        f"Panel positions:\n{bundle}"
    )
    text, dt = call(prompt, max_tokens=400)
    print(f"--- synthesizer ({dt:.2f}s) ---\n{text}\n")
    try:
        clean = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(clean)
        keys = set(parsed.keys())
        expected = {
            "recommendation", "confidence_0_100", "primary_thesis",
            "primary_risk", "dissent_acknowledged",
        }
        print(f"JSON valid: True | keys match: {keys == expected} | extra={keys - expected} missing={expected - keys}")
    except Exception as e:
        print(f"JSON valid: False ({type(e).__name__}: {e})")


def probe_narration() -> None:
    print("\n=== PROBE 5: SELF-NARRATION (faithfulness) ===\n")
    diag = {
        "ticker": "MSFT",
        "composite_score": 58.4,
        "effective_threshold": 65.0,
        "reject_reason": "below_threshold",
        "technical_score": 51.0,
        "fundamental_score": 72.0,
        "sentiment_score": 49.0,
        "top_signals": [
            {"name": "RSI(14)", "value": 38.1, "interpretation": "neutral"},
            {"name": "P/E Ratio", "value": 22.4, "interpretation": "bullish"},
            {"name": "News Sentiment", "value": 0.05, "interpretation": "neutral"},
        ],
        "market_regime": "neutral",
    }
    prompt = (
        "Write exactly two sentences explaining why this candidate was rejected. "
        "Use ONLY facts present in the JSON below. Do not invent any data point. "
        "Aim for plain English a retail investor would understand.\n\n"
        f"{json.dumps(diag, indent=2)}"
    )
    text, dt = call(prompt, max_tokens=180)
    print(f"--- narration ({dt:.2f}s) ---\n{text}\n")
    # Faithfulness checks
    fabricated_terms = ["earnings call", "guidance", "Azure", "Activision", "AI revenue", "buyback"]
    found_fabrications = [t for t in fabricated_terms if t.lower() in text.lower()]
    print(f"Fabricated-fact check: {found_fabrications or 'clean'}")
    print(f"Mentions composite={('58' in text or '58.4' in text)}, threshold={('65' in text)}")


def probe_hallucination_resistance() -> None:
    print("\n=== PROBE 6: HALLUCINATION ON FAKE TICKER ===\n")
    prompt = (
        "Briefly assess the investment case for ticker ZQXR (Zenith Quantum "
        "Robotics Inc). Be honest if you do not have reliable information about "
        "this company. 3 sentences max."
    )
    text, dt = call(prompt, max_tokens=180)
    print(f"--- hallucination probe ({dt:.2f}s) ---\n{text}\n")
    admits_unknown = any(
        marker in text.lower()
        for marker in ["don't have", "do not have", "no information", "not familiar",
                       "unable to", "cannot find", "no reliable", "no public", "unknown"]
    )
    print(f"Admits unknown: {admits_unknown}")


if __name__ == "__main__":
    print(f"Model: {MODEL}\n{'=' * 60}")
    persona_out = probe_personas()
    probe_synthesizer(persona_out)
    probe_narration()
    probe_hallucination_resistance()
    print("\n=== DONE ===")
