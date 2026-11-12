#!/usr/bin/env python3
"""Small checkable benchmark for an Ollama model. Usage: ollama_bench.py MODEL think|nothink OUT.json [num_ctx]
Run it ON the Jetson (talks to 127.0.0.1:11434). Copy with scp first."""
import json, sys, time, urllib.request, urllib.error, subprocess, threading, re, tempfile

if len(sys.argv) < 4 or sys.argv[1] in ("-h", "--help") or sys.argv[2] not in ("think", "nothink"):
    sys.exit(__doc__)
MODEL, MODE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
NUM_CTX = int(sys.argv[4]) if len(sys.argv) > 4 else 4096
THINK = MODE == "think"
API = "http://127.0.0.1:11434"
NUM_PREDICT = 3000 if THINK else 700


def post(path, payload, timeout=900):
    req = urllib.request.Request(API + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


minavail = [10 ** 9]
stop = False


def mon():
    while not stop:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable"):
                minavail[0] = min(minavail[0], int(line.split()[1]) // 1024)
        time.sleep(1)


threading.Thread(target=mon, daemon=True).start()


def strip_think(t):
    return re.sub(r"<think>.*?</think>", "", t, flags=re.S).strip()


def code_ok(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    src = m.group(1) if m else text
    test = src + "\nassert is_prime(2) and is_prime(13) and is_prime(97)\nassert not is_prime(1) and not is_prime(0) and not is_prime(91) and not is_prime(100)\nprint('PASS')\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(test)
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=10)
        return "PASS" in r.stdout
    except Exception:
        return False


def json_ok(text):
    m = re.search(r"\{.*\}", text, re.S)
    try:
        d = json.loads(m.group(0))
        return str(d.get("city", "")).lower() == "tokyo" and "japan" in str(d.get("country", "")).lower()
    except Exception:
        return False


def bullets_ok(text):
    lines = [l for l in text.splitlines() if l.strip().startswith(("-", "*", "\u2022")) or re.match(r"\s*\d+[.)]", l)]
    return len(lines) == 3


TASKS = [
    ("arith", "What is 17 * 23? Answer with only the number.", lambda t: "391" in t),
    ("json", 'Return only a JSON object with keys "city" and "country" for the capital of Japan. No other text.', json_ok),
    ("trick", "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Give the final answer in cents as a number only.", lambda t: re.search(r"\b5\b", t) is not None and "10 cents" not in t.lower()),
    ("format", "List exactly 3 bullet points about MQTT QoS levels, one short line each. No intro, no outro.", bullets_ok),
    ("code", "Write a Python function is_prime(n) that returns True if n is prime. Return only the code in one code block.", code_ok),
]

res = {"model": MODEL, "mode": MODE, "num_ctx": NUM_CTX, "tasks": [], "errors": []}
for name, prompt, check in TASKS:
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False,
               "keep_alive": "5m", "options": {"num_ctx": NUM_CTX, "temperature": 0.3, "num_predict": NUM_PREDICT},
               "think": THINK}
    t0 = time.time()
    try:
        try:
            d = post("/api/chat", payload)
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            if "think" in body.lower():
                payload.pop("think")
                d = post("/api/chat", payload)
            else:
                raise RuntimeError(body)
        msg = d.get("message", {})
        content = strip_think(msg.get("content", ""))
        ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
        res["tasks"].append({"task": name, "pass": bool(check(content)), "tok": ec,
                             "tok_s": round(ec / (ed / 1e9), 2) if ed else None,
                             "load_s": round(d.get("load_duration", 0) / 1e9, 1), "wall_s": round(time.time() - t0, 1),
                             "thinking_chars": len(msg.get("thinking", "") or ""), "answer": content[:160]})
    except Exception as e:
        res["errors"].append(f"{name}: {str(e)[:200]}")
        res["tasks"].append({"task": name, "pass": False, "error": str(e)[:120]})
        break

stop = True
done = [t for t in res["tasks"] if t.get("tok_s")]
res["passed"] = f'{sum(t["pass"] for t in res["tasks"])}/{len(TASKS)}'
res["median_tok_s"] = sorted(t["tok_s"] for t in done)[len(done) // 2] if done else None
res["min_mem_available_mb"] = minavail[0]
json.dump(res, open(OUT, "w"), indent=1)
try:
    post("/api/generate", {"model": MODEL, "keep_alive": 0}, timeout=60)
except Exception:
    pass
print(MODEL, MODE, res["passed"], "median tok/s", res["median_tok_s"], "min free MB", res["min_mem_available_mb"], res["errors"])
