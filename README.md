# Cursor Quality Lab

> An open-source product quality framework for AI-native developer tools — featuring an automated VoC signal pipeline, LLM-as-judge bug classification, and a structured bug report portfolio built through deep product immersion.

[![Pipeline](https://img.shields.io/badge/pipeline-passing-brightgreen)](https://github.com/aarprojects/cursor-quality-lab/actions)
[![Classifier](https://img.shields.io/badge/classifier-LLM--as--judge-blue)](pipeline/ingest.py)
[![Issues Triaged](https://img.shields.io/badge/issues%20triaged-13-orange)](pipeline/triage_output.json)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## What this is

Most quality programs stop at bug reporting. This one doesn't.

This project explores what a **Product Quality Engineer** role looks like when built natively on AI — replacing manual triage spreadsheets with an automated pipeline that ingests community signal, classifies severity using an LLM, routes issues to the right team, and alerts on P0s before they compound.

Three pillars:

- **Deep product testing** — hands-on usage to surface real bugs, written as engineer-ready reports
- **VoC signal intelligence** — community pain points mined, categorized, and synthesized into actionable product signal
- **Automated triage pipeline** — keyword rules → LLM-as-judge, with human-in-the-loop for low-confidence items

---

## Project structure

```
cursor-quality-lab/
├── bug-reports/                  # Hands-on product testing
│   ├── bug_report_1.md           # Agent mode — P0 file write regression
│   ├── bug_report_2.md           # Tab completion — P0 indexing failure
│   └── bug_report_3.md           # Context window — P1 compression bug
│
├── voc/
│   └── voc_memo.md               # Top 5 pain points — PM-ready weekly signal
│
├── pipeline/                     # Automated triage infrastructure
│   ├── ingest.py                 # LLM-as-judge classifier + routing engine
│   ├── voc_raw_data.csv          # 19 community signals, manually tagged
│   ├── voc_raw_data_reddit.csv   # Classified + routed output, P0 first
│   ├── triage_output.json        # 13 triaged P0/P1 issues with reasoning
│   ├── human_review_queue.json   # Low-confidence items for human review
│   └── gap_analysis.md           # Where the feedback loop breaks
│
├── .github/
│   └── workflows/
│       └── voc_pipeline.yml      # Daily cron + P0 Slack alert
│
└── notes/                        # Raw product observations
```

---

## Bug portfolio

Three engineer-ready reports from direct product testing — each with severity rationale, reproduction steps, customer impact, and engineering scope hypothesis.

| # | Product area | Severity | Summary |
|---|---|---|---|
| [1](bug-reports/bug_report_1.md) | Agent mode | **P0** | File changes applied to disk with no diff UI — data loss risk |
| [2](bug-reports/bug_report_2.md) | Tab completion | **P0** | Indexing hangs silently — all requests return `[not_found]` |
| [3](bug-reports/bug_report_3.md) | Context window | **P1** | Compression discards edits from 2 minutes ago — recency not weighted |

Each report includes a written severity rationale — not just what broke, but *why this severity and not one lower*.

---

## VoC signal pipeline

### How it works

```
Community signal (Reddit · Cursor Forum · Changelog)
        │
        ▼
  ingest.py
        ├── LLM-as-judge (claude-haiku-4-5)
        │       └── low confidence → human_review_queue.json
        ├── Deduplication (rapidfuzz fuzzy matching)
        ├── Routing engine
        │       ├── P0               → engineering_escalation
        │       ├── P1 (3+ reports)  → engineering_escalation
        │       ├── P1               → product_triage
        │       ├── P2               → backlog
        │       └── Noise            → close
        └── Outputs
                ├── triage_output.json
                └── voc_raw_data_reddit.csv
                        │
                        ▼
              GitHub Actions (daily 9am UTC)
                        └── P0 detected → Slack alert 🚨
```

### Classifier evolution

| Stage | Classifier | Accuracy vs manual tags | Notes |
|---|---|---|---|
| v1 | Keyword rules | 42% (8/19) | Fast, free, misses descriptive phrasing |
| v2 | Claude API — LLM-as-judge | Run to measure | Nuance, confidence scoring, reasoning |

The v1 baseline was kept intentionally — the accuracy delta between v1 and v2 is the core eval story.

### Run locally

```bash
git clone https://github.com/aarprojects/cursor-quality-lab.git
cd cursor-quality-lab/pipeline

pip install anthropic rapidfuzz
export ANTHROPIC_API_KEY=your_key

python ingest.py                   # LLM classifier, CSV mode (default)
python ingest.py --no-llm          # keyword rules only, no API key needed
python ingest.py --source reddit   # live Reddit pull (requires credentials)
```

### Output files

| File | Contents |
|---|---|
| `triage_output.json` | P0/P1 issues — severity, routing, report_count, sample quotes, LLM reasoning |
| `human_review_queue.json` | Low-confidence items flagged for human review |
| `voc_raw_data_reddit.csv` | All classified issues, sorted P0 first |

---

## Gap analysis

Where the feedback loop breaks today:

| Gap | Impact | Status |
|---|---|---|
| Reddit → nowhere | High-engagement P1s have no path to engineering | Identified |
| Forum → slow triage | Oldest unresolved reports 8+ months old | Identified |
| Duplicates inflate noise | Same bug looks like separate reports | ✅ Fixed — fuzzy dedup + report_count |
| Changelog fixes are silent | Users never learn their bug was fixed | Identified |

Proposed measurement: **loop closure rate** = % of P0s acknowledged by engineering within 24 hours.

Full analysis: [`pipeline/gap_analysis.md`](pipeline/gap_analysis.md)

---

## GitHub Actions

Runs daily at 9am UTC. On any P0 detection, fires a Slack webhook immediately.

```yaml
on:
  schedule:
    - cron: "0 9 * * *"
  workflow_dispatch:
```

To enable: add `ANTHROPIC_API_KEY` and `SLACK_WEBHOOK_URL` as repository secrets.

---

## VoC memo — top 5 pain points (June 2026)

Ranked by severity × frequency from 19 community signals:

1. **Agent mode — file integrity failures** — P0 — engineering escalation
2. **Tab completion — indexing failure** — P0 — engineering escalation
3. **Agent mode — CI and automation reliability** — P1 — product triage
4. **Context window — compression discards recent edits** — P1 — product triage
5. **Performance — token explosion** — P1 — product triage

Full memo: [`voc/voc_memo.md`](voc/voc_memo.md)

---

## Numbers

| Metric | Value |
|---|---|
| Community signals analyzed | 19 |
| P0s detected | 5 |
| Issues triaged (P0 + P1) | 13 |
| Engineering escalations | 8 |
| Keyword classifier accuracy | 42% |
| Pipeline cadence | Daily — automated |

---

*Built by [Anupa Abdul Rahiman](https://github.com/aarprojects) — Staff QE / Automation Tech Lead*  
*Previously: Block/Square · eBay*
