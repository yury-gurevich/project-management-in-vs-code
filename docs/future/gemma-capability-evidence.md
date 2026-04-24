# Gemma capability assessment — findings

Run date: 2026-04-18
Hardware: Win10, 16 GB RAM (3.9 GB free), Intel Iris Plus 640 (no CUDA), CPU-only inference
Benchmarks: `docs/local/temp/gemma_benchmark.py` (hosted), `gemma_local_benchmark.py` (Ollama)

## Models evaluated

| Model | Where | Size | Notes |
|---|---|---|---|
| `gemma-4-31b-it` | Google API | hosted | upper bound for "Gemma quality" |
| `gemma3:4b` Q4 | Ollama local | 3.3 GB | realistic target for consumer hardware |
| `gemma3:1b` Q4 | Ollama local | 815 MB | floor reference |

Note: when asked about its own version, `gemma-4-31b-it` self-identifies as
Gemma 2 family. Whatever Google's branding, treat the model's capabilities as
"Gemma 2 / 3 era," not bleeding edge.

## Probe results

| Probe | 1B local | 4B local | 31B hosted |
|---|---|---|---|
| Persona distinctness | Confused, role-blurred | Decent, mostly in lane | Sharp, distinct heuristics |
| Synthesizer JSON validity | ✓ (counted analysts wrong) | ✓ (integrates news) | ✓ (names dissent precisely) |
| Narration faithfulness | Wrong field cited | **Fully accurate** | **Empty / failed** |
| Hallucination on fake ticker | Confident fabrication | Hedged but still fabricated | Cleanly refused |
| Persona latency (each) | 25–33 s | 60–89 s | 22–30 s |
| Synthesizer latency | 39 s | 110 s | 25 s |
| Narration latency | 12 s | 34 s | 80 s (failed) |

## Verdict by moonshot

### Moonshot #5 — self-narration
**Local 4B: SHIP IT.** Faithful to inputs, no fabrication when constrained to
provided data, ~34 s/call. Better quality on this exact task than the hosted
31B (which timed out). Privacy story fully intact.

### Moonshot #2 — multi-agent debate
**Local 4B: viable but slow.** Quality acceptable. Latency ~200 s per
candidate even with parallelized persona calls; ~100 min for a 30-candidate
pipeline. Defensible as overnight batch, not interactive.

**Hosted 31B:** quality is meaningfully better, latency ~30 s parallelized per
candidate. But violates the privacy promise unless framed as cloud opt-in.

### Hallucination — design constraint, not a deal-breaker
Both small models fabricate on unfamiliar tickers. Mitigation:
- System prompts must enforce grounding in provided JSON/diagnostics only
- Never expose Gemma to open-ended "tell me about X" prompts
- Treat ticker symbols, company names, dates as input fields the model reads,
  never as keys it looks up

## Recommended architecture for the privacy-first product

> **2026-04-20 update — dev-mode pivot.** The block below is the *target*
> architecture. During dev mode the system temporarily calls the hosted
> Google Gemma API (`gemma-4-31b-it` via `google.genai`) for moonshot #5
> narration because the current workstation cannot run Ollama + the
> trading stack concurrently. Scope, privacy cost, and exit conditions are
> in [cloud-gemma-dev-mode.md](../local/cloud-gemma-dev-mode.md). Retire this note
> when the deviation is retired.

```
Local (Gemma 3 4B Q4 via Ollama):       <-- dev-mode: temporarily hosted,
  - moonshot #5: self-narration              see cloud-gemma-dev-mode.md
  - any "reasoning over data we provide" task

Local (no LLM):
  - moonshot #1: distribution-based outputs (ABIDES)
  - moonshot #4: causal DAG over signals

Cloud opt-in (Gemma 4 31B or larger, behind explicit user toggle):
  - moonshot #2: multi-agent debate
  - "Pro mode" for users who trade privacy for fidelity
```

The target headline remains: **"Your data only leaves the machine if you
turn on Pro Mode. Everything else runs locally."** Both halves of that
statement are backed by benchmarks. During dev mode the "everything else
runs locally" half is temporarily weakened for moonshot #5 only; every
other component still runs locally.

## Open questions

1. Does 4B latency on this CPU box represent the real consumer experience, or
   is it artificially slow (only 3.9 GB free during the run)? Worth re-running
   on a clean reboot to get a cleaner number.
2. Will quality on 4B hold up for *fundamental* sector-specific reasoning
   (banks vs biotech vs energy), or did NVDA get a "famous ticker" boost?
   Worth a follow-up benchmark with 3-4 less-famous tickers.
3. Can 12B Q4 actually run on a typical consumer machine (32 GB / mid GPU)
   that you might target for the "power user" tier? Worth benchmarking on a
   second box if available.
