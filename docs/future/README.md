# Future Direction — Reading Guide

> **What this folder is.** The committed, tracked record of where this system
> is heading and why. Written 2026-04-19. All documents here are load-bearing
> planning material — they inform sprint execution and architectural decisions.
>
> **What this folder is not.** Implementation code, runbooks, or temporary
> scratch. Those live in `docs/local/` (gitignored) and `docs/local/temp/`
> respectively.

---

## Read in this order

| # | Document | One-line hook |
|---|---|---|
| 1 | [vision-and-scope.md](vision-and-scope.md) | Why this direction, for whom, and what "privacy-first + distributions + narration" means in practice |
| 2 | [integration-map.md](integration-map.md) | How the moonshots map to PRD-v2 phases and eight work groups (A–H) — the master sequencing plan |
| 3 | [gemma-capability-evidence.md](gemma-capability-evidence.md) | Benchmark evidence that Gemma 3 4B local is sufficient for narration; why hosted 31B is not strictly better |
| 4 | [data-strategy-and-gap-analysis.md](data-strategy-and-gap-analysis.md) | The real moat is the data corpus, not the algorithm — what to collect, for how long, and what 2 years of historical data unlocks |
| 5 | ~~sprint-gemma-narration.md~~ | **Shipped** (b8fb5c0, 34cabd1). Archived at [docs/del/sprint-gemma-narration.md](../del/sprint-gemma-narration.md). |
| 6 | ~~sprint-abides-distribution.md~~ | **Shipped** (0b95d32). Archived at [docs/del/sprint-abides-distribution.md](../del/sprint-abides-distribution.md). |

---

## Context docs (in `docs/`, already tracked)

| Document | What it is |
|---|---|
| [docs/PRD-v2.md](../PRD-v2.md) | The product PRD. All future work populates slots PRD-v2 already left open. |
| [docs/moonshots.md](../moonshots.md) | The five moonshots ranked by daring × feasibility. The source vision document. |
| [docs/ai-prediction-roadmap.md](../ai-prediction-roadmap.md) | ML roadmap (ML-1 through ML-5). |
| [docs/sprint-loop.md](../sprint-loop.md) | How to close a sprint: branch, quality gate, tag, push, cleanup. |

---

## Benchmark tools (in `tools/`)

| File | What it runs |
|---|---|
| [tools/gemma_benchmark.py](tools/gemma_benchmark.py) | 6-probe benchmark against hosted `gemma-4-31b-it` via Google genai SDK |
| [tools/gemma_local_benchmark.py](tools/gemma_local_benchmark.py) | Same 6 probes against local Ollama endpoint. CLI arg: model tag. |
