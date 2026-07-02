# LLM Latency Benchmark

A lightweight, CI-gateable harness for measuring **latency and throughput of LLM API calls**. It captures time-to-first-token (TTFB) and end-to-end response time on a streamed request, runs repeated trials, aggregates the results statistically, and applies **threshold-based PASS/FAIL gates** — the same pattern you'd wire into a CI pipeline to catch performance regressions before they ship.

Built as part of an AI-native quality engineering portfolio, with a focus on treating LLM performance as a testable, monitorable signal rather than a black box.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Anthropic API](https://img.shields.io/badge/Anthropic-Claude-orange)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## Why this exists

LLM response time is a first-class quality attribute — it drives user experience, cost, and SLA compliance — but it's non-deterministic and easy to regress silently. This project demonstrates a QE approach to that problem:

- **Instrument** the request (TTFB via streaming, total wall-clock time, token counts).
- **Repeat** the measurement to characterize variance, not just a single lucky run.
- **Aggregate** into interpretable statistics (min / max / mean / median / stdev).
- **Gate** on thresholds so a slowdown fails loudly instead of drifting unnoticed.

## Features

- **Streaming TTFB measurement** — captures the exact moment the first token arrives, separately from total completion time.
- **Repeated-run benchmarking** — configurable number of trials with per-run and summary reporting.
- **Statistical summary** — min, max, mean, median, and standard deviation for both TTFB and total time.
- **Threshold gates** — configurable pass/fail checks on average TTFB and average total time, suitable for use as a CI quality gate.
- **CSV logging** — every run is appended to a timestamped CSV for trend analysis and historical baselines.
- **Zero-config secrets** — reads the API key from a local `.env` file (never committed).

## How it works

The core technique is measuring TTFB off the streaming response. Instead of waiting for the whole completion, the harness starts a timer, opens a streamed request, and records the elapsed time the instant the first text chunk arrives:

```
start timer ──▶ open stream ──▶ first token? ──▶ record TTFB
                                       │
                                       ▼
                              consume remaining tokens
                                       │
                                       ▼
                        record total time + token usage ──▶ log to CSV
```

`benchmark.py` wraps this in a loop, collects TTFB and total-time samples across N runs, and prints a summary table plus a threshold check.

## Repository layout

| File | Purpose |
|------|---------|
| `api_call.py` | Single instrumented call — streams a prompt, prints live output, logs TTFB / total time / tokens to `llm_latency_log.csv`. |
| `benchmark.py` | Runs the prompt N times (default 5), reports per-run metrics, prints a statistical summary, and applies pass/fail threshold gates. Logs to `llm_benchmark_log.csv`. |
| `llm_latency_log.csv` | Append-only log of single-call latency runs. |
| `llm_benchmark_log.csv` | Append-only log of benchmark runs (one row per trial). |
| `requirements.txt` | Pinned environment. Core runtime deps are `anthropic` and `python-dotenv`; the file also captures the broader QE toolchain used across the portfolio (pytest, deepeval, ragas, jiwer, etc.). |

## Quick start

**1. Clone and set up a virtual environment**

```bash
git clone https://github.com/aarprojects/llm-latency-benchmark.git
cd llm-latency-benchmark
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> The two scripts only require `anthropic` and `python-dotenv`. If you want a minimal install: `pip install anthropic python-dotenv`.

**2. Add your API key**

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

`.env` is git-ignored and will not be committed.

**3. Run a single instrumented call**

```bash
python api_call.py
```

**4. Run the benchmark (5 trials + threshold gates)**

```bash
python benchmark.py
```

## Sample output

```
📊 BENCHMARK SUMMARY  (5 runs)
═══════════════════════════════════════════════════════
  Metric                       TTFB   Total Time
  ────────────────────── ────────── ────────────
  Min                       0.5977s      3.4600s
  Max                       1.5485s      4.4120s
  Average                   0.8410s      3.6775s
  Median                    0.6950s      3.4851s
  Std Deviation             0.3985s      0.4120s
═══════════════════════════════════════════════════════

🔍 Threshold Check:
   Avg TTFB  < 2.0s : 0.8410s  ✅ PASS
   Avg Total < 8.0s : 3.6775s  ✅ PASS
```

*(Figures above are from an actual logged run against Claude Haiku 4.5; your numbers will vary with model, prompt, and network conditions.)*

## Configuration

Both scripts expose their knobs as constants at the top of the file:

| Constant | Meaning |
|----------|---------|
| `MODEL` | Target model (default `claude-haiku-4-5-20251001`). |
| `PROMPT` | The prompt under test. |
| `MAX_TOKENS` | Output token cap. |
| `RUNS` | Number of benchmark trials (`benchmark.py`). |
| `AVG_TTFB_THRESHOLD` / `AVG_TOTAL_THRESHOLD` | Pass/fail gate limits (`benchmark.py`). |

## Using it as a CI gate

Because `benchmark.py` fails its threshold check when latency exceeds the configured limits, it slots naturally into CI: run it on a schedule or on release candidates, and treat a `FAIL` as a build-blocking performance regression. A minimal GitHub Actions step:

```yaml
- name: LLM latency gate
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: python benchmark.py
```

*(Exit-code enforcement is a natural next step — see roadmap.)*

## Roadmap

- Return a non-zero exit code on threshold failure so CI blocks automatically.
- Parametrize model, prompt, and thresholds via CLI args / config file.
- Multi-model comparison in a single run.
- Percentile latency (p50 / p95 / p99) alongside mean and stdev.
- Optional dashboard / plot of the CSV history for trend visualization.

## About

Built by **Anupa Abdul Rahiman**, a Quality Engineering leader focused on AI-native quality — treating LLM behavior, performance, and evaluation as first-class, testable, monitorable signals.

---

*License: add a `LICENSE` file (MIT recommended for a public portfolio project).*
