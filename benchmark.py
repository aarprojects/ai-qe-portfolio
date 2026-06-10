import anthropic
import time
import csv
import os
import statistics
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MODEL      = "claude-haiku-4-5-20251001"
PROMPT     = "What are 3 best practices for testing LLM outputs?"
MAX_TOKENS = 300
RUNS       = 5
CSV_FILE   = "llm_benchmark_log.csv"

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "run", "model", "prompt",
                "ttfb_seconds", "total_time_seconds",
                "input_tokens", "output_tokens"
            ])
        print(f"📁 Created log file: {CSV_FILE}")

def log_to_csv(row):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def single_run(run_number):
    client     = anthropic.Anthropic()
    ttfb       = None
    full_text  = ""
    start_time = time.perf_counter()
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": PROMPT}]
    ) as stream:
        for text in stream.text_stream:
            if ttfb is None:
                ttfb = time.perf_counter() - start_time
            full_text += text
        final_message = stream.get_final_message()

    total_time    = time.perf_counter() - start_time
    input_tokens  = final_message.usage.input_tokens
    output_tokens = final_message.usage.output_tokens

    print(f"   Run {run_number}: TTFB {ttfb:.4f}s  |  Total {total_time:.4f}s  |  Tokens in/out {input_tokens}/{output_tokens}")

    log_to_csv([
        timestamp, run_number, MODEL, PROMPT,
        round(ttfb, 4), round(total_time, 4),
        input_tokens, output_tokens
    ])

    return ttfb, total_time

def print_summary(ttfb_list, total_list):
    print(f"\n{'═' * 55}")
    print(f"📊 BENCHMARK SUMMARY  ({RUNS} runs)")
    print(f"{'═' * 55}")
    print(f"  {'Metric':<22} {'TTFB':>10} {'Total Time':>12}")
    print(f"  {'─'*22} {'─'*10} {'─'*12}")
    print(f"  {'Min':<22} {min(ttfb_list):>10.4f}s {min(total_list):>11.4f}s")
    print(f"  {'Max':<22} {max(ttfb_list):>10.4f}s {max(total_list):>11.4f}s")
    print(f"  {'Average':<22} {statistics.mean(ttfb_list):>10.4f}s {statistics.mean(total_list):>11.4f}s")
    print(f"  {'Median':<22} {statistics.median(ttfb_list):>10.4f}s {statistics.median(total_list):>11.4f}s")
    print(f"  {'Std Deviation':<22} {statistics.stdev(ttfb_list):>10.4f}s {statistics.stdev(total_list):>11.4f}s")
    print(f"{'═' * 55}")

    AVG_TTFB_THRESHOLD  = 2.0
    AVG_TOTAL_THRESHOLD = 8.0
    avg_ttfb  = statistics.mean(ttfb_list)
    avg_total = statistics.mean(total_list)

    print(f"\n🔍 Threshold Check:")
    ttfb_status  = "✅ PASS" if avg_ttfb  < AVG_TTFB_THRESHOLD  else "❌ FAIL"
    total_status = "✅ PASS" if avg_total < AVG_TOTAL_THRESHOLD else "❌ FAIL"
    print(f"   Avg TTFB  < {AVG_TTFB_THRESHOLD}s  : {avg_ttfb:.4f}s  {ttfb_status}")
    print(f"   Avg Total < {AVG_TOTAL_THRESHOLD}s  : {avg_total:.4f}s  {total_status}")
    print(f"\n📁 All runs logged to: {CSV_FILE}")

if __name__ == "__main__":
    init_csv()

    print(f"\n🚀 Benchmarking: {RUNS} runs")
    print(f"   Model  : {MODEL}")
    print(f"   Prompt : '{PROMPT[:50]}...'")
    print(f"{'─' * 55}")

    ttfb_list  = []
    total_list = []

    for i in range(1, RUNS + 1):
        ttfb, total = single_run(i)
        ttfb_list.append(ttfb)
        total_list.append(total)
        if i < RUNS:
            time.sleep(1)

    print_summary(ttfb_list, total_list)
