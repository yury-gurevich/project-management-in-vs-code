# Archived Sprint Pointer — Gemma Narration MVP

This sprint shipped via commits `34cabd1` and `b8fb5c0`.

The original full sprint spec was removed from the tracked tree in commit
`1fc0bb4` after shipment because it was no longer intended to be a live planning
document. Several current docs still need a durable in-repo pointer for that
work, so this file exists as the stable archive target.

## What shipped

- On-demand narration for analyst diagnostics
- The shipped `src/trading/gemma/` foundation
- `narrations` and `gemma_call_audits` persistence
- Dashboard narration endpoints and the "Why rejected" surface
- Local grounding, validation, and durable audit for Gemma calls

## Recover the original full sprint spec

Run this from the repo root:

```bash
git show a6fbf629a9d0472302478797b20c1cf342706bc1:docs/del/sprint-gemma-narration.md
```

## Use these live references first

- [docs/local/prd-v2-completion-plan-2026-04-20.md](../local/prd-v2-completion-plan-2026-04-20.md) for current Phase A/B sequencing
- [docs/local/cloud-gemma-dev-mode.md](../local/cloud-gemma-dev-mode.md) for the hosted-Gemma runtime deviation that superseded the original local-Ollama assumptions
- [src/trading/gemma/templates.py](../../src/trading/gemma/templates.py) for the shipped template registry baseline
- [src/trading/gemma/narration.py](../../src/trading/gemma/narration.py) for the shipped orchestration baseline
