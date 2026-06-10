import anthropic
import time
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MODEL       = "claude-haiku-4-5-20251001"
PROMPT      = "What are 3 best practices for testing LLM outputs?"
MAX_TOKENS  = 300
CSV_FILE    = "llm_latency_log.csv"

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "model", "prompt",
                "ttfb_seconds", "total_time_seconds",
                "input_tokens", "output_tokens", "response_preview"
            ])
        print(f"📁 Created log file: {CSV_FILE}")

def log_to_csv(timestamp, model, prompt, ttfb, total_time,
               input_tokens, output_tokens, response):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp, model, prompt,
            round(ttfb, 4), round(total_time, 4),
            input_tokens, output_tokens, response[:100]
        ])
    print(f"📊 Logged to {CSV_FILE}")

def call_with_ttfb(prompt):
    client = anthropic.Anthropic()
    print(f"\n🚀 Sending prompt: '{prompt}'")
    print(f"   Model: {MODEL}")
    print("-" * 55)

    ttfb        = None
    full_text   = ""
    start_time  = time.perf_counter()
    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            if ttfb is None:
                ttfb = time.perf_counter() - start_time
                print(f"⚡ TTFB: {ttfb:.4f}s  (first token arrived)")
                print("\n📝 Response:\n")
            full_text += text
            print(text, end="", flush=True)
        final_message = stream.get_final_message()

    total_time    = time.perf_counter() - start_time
    input_tokens  = final_message.usage.input_tokens
    output_tokens = final_message.usage.output_tokens

    print(f"\n\n{'─' * 55}")
    print(f"📈 Metrics:")
    print(f"   TTFB          : {ttfb:.4f}s")
    print(f"   Total time    : {total_time:.4f}s")
    print(f"   Input tokens  : {input_tokens}")
    print(f"   Output tokens : {output_tokens}")
    print(f"   Timestamp     : {timestamp}")

    return timestamp, ttfb, total_time, input_tokens, output_tokens, full_text

if __name__ == "__main__":
    init_csv()
    timestamp, ttfb, total_time, input_tokens, output_tokens, response = \
        call_with_ttfb(PROMPT)
    log_to_csv(
        timestamp=timestamp, model=MODEL, prompt=PROMPT,
        ttfb=ttfb, total_time=total_time,
        input_tokens=input_tokens, output_tokens=output_tokens,
        response=response
    )
    print(f"\n✅ Done. Check {CSV_FILE} for the log entry.")
