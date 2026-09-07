# FlamAI R&D — The Audit

Submission for the AI Team Intern R&D assignment, **The Audit**.

## Overview

This project audits a previous intern's tokenizer and serving benchmark before
routing and capacity decisions are made.

The audit covers:

- Multilingual tokenizer evaluation
- Measurement and code-level audit of `fertility.py`
- Corrected cross-language tokenization analysis
- KV-cache capacity calculations
- Serving throughput and goodput reconciliation
- Production monitoring recommendations
- A decision memo for improving multilingual conversational style

## Repository Structure

```text
NOTEBOOK.md
AI_USAGE.md
README.md
requirements.txt

fertility.py
REPORT_v0.md

bench/
├── model_spec.md
└── bench_log.csv

corpus_sample/

partA/
├── memo.md
├── prepare_corpus.py
├── verify_corpus.py
├── corpus/
└── experiments/

partB/
└── answers.md

partC/
└── memo.md