"""Copy-as-cURL round trip study.

For each site: open the page once in headless Chrome (Playwright), capture the navigation request
exactly as DevTools would put it into "Copy as cURL (bash)", then replay the request four ways and
compare: system curl running the command, the Python `requests` code produced by curlconverter,
the same headers through curl_cffi with Chrome impersonation, and a bare requests.get() with no
headers. Records status, body size, a challenge-page check, timing, and how many headers survived
the conversion. Writes results/curl_study.json and one .sh / .py file per command under commands/.
"""
import json, re, subprocess, sys, time, pathlib, shlex
import requests
from curl_cffi import requests as cffi_requests
from playwright.sync_api import sync_playwright
from survey import SITES, robots_ok

HERE = pathlib.Path(__file__).parent
CMDS = HERE / "commands"
CMDS.mkdir(exist_ok=True)
OUT = HERE / "results/curl_study.json"
PY = str(pathlib.Path(sys.executable))
BLOCK_RE = re.compile(r"just a moment|access denied|are you a human|verify you are human|human verification|captcha|attention required|unusual traffic|pardon our interruption|request blocked|robot check|security check|blocked", re.I)
SKIP_HEADERS = {"host", "content-length", "accept-encoding", "cookie", "connection"}
PRELUDE = """import functools, requests as _rq
for _m in ('get', 'post', 'put', 'delete', 'patch', 'head', 'request'):
    setattr(_rq, _m, functools.partial(getattr(_rq, _m), timeout=30))
"""


def title_of(body):
    m = re.search(rb"<title[^>]*>(.*?)</title>", body[:200000], re.I | re.S)
    return m.group(1).decode("utf-8", "replace").strip()[:80] if m else ""


def judge(status, body):
    blocked = status in (401, 403, 429, 503) or bool(BLOCK_RE.search(title_of(body)))
    return "blocked" if blocked else ("ok" if status == 200 else f"http {status}")


def capture(pw, url):
    headers = {}
    browser = pw.chromium.launch(headless=True, channel="chrome")
    page = browser.new_page(viewport={"width": 1366, "height": 900})

    def on_request(req):
        if req.is_navigation_request() and req.resource_type == "document" and not headers:
            headers.update(req.all_headers())

    page.on("request", on_request)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        final_url = page.url
    except Exception as e:
        final_url = url
        headers.setdefault("_error", str(e)[:100])
    browser.close()
    clean = {k: v for k, v in headers.items() if not k.startswith(":") and k.lower() not in SKIP_HEADERS and not k.startswith("_")}
    return final_url, clean


def build_curl(url, headers):
    parts = ["curl", shlex.quote(url)]
    for k, v in headers.items():
        parts.append("-H " + shlex.quote(f"{k}: {v}"))
    parts.append("--compressed")
    return " \\\n  ".join(parts)


def run_curl(url, headers, body_path):
    args = ["curl", "-sS", "-L", "--max-time", "30", "-o", str(body_path), "-w", "%{http_code}", url, "--compressed"]
    for k, v in headers.items():
        args += ["-H", f"{k}: {v}"]
    t0 = time.perf_counter()
    r = subprocess.run(args, capture_output=True, text=True, timeout=60)
    dt = time.perf_counter() - t0
    status = int(r.stdout.strip() or 0)
    body = body_path.read_bytes() if body_path.exists() else b""
    return status, body, dt, r.stderr.strip()[:100]


def convert(cmd_text):
    r = subprocess.run(["node", "-e", "const c=require('curlconverter');process.stdout.write(c.toPython(require('fs').readFileSync(0,'utf8')))"],
                       input=cmd_text, capture_output=True, text=True, timeout=60, cwd=HERE)
    return r.stdout, r.stderr.strip()[:200]


def run_converted(code, body_path):
    script = PRELUDE + code + f"\nprint(response.status_code)\nopen(r'{body_path}', 'wb').write(response.content)\n"
    path = body_path.with_suffix(".py")
    path.write_text(script, encoding="utf-8")
    t0 = time.perf_counter()
    r = subprocess.run([PY, str(path)], capture_output=True, text=True, timeout=90)
    dt = time.perf_counter() - t0
    status = int((r.stdout.strip().splitlines() or ["0"])[-1] or 0) if r.returncode == 0 else 0
    body = body_path.read_bytes() if body_path.exists() else b""
    return status, body, dt, r.stderr.strip()[-160:]


def run_cffi(url, headers):
    t0 = time.perf_counter()
    try:
        r = cffi_requests.get(url, headers=headers, impersonate="chrome", timeout=30, allow_redirects=True)
        return r.status_code, r.content, time.perf_counter() - t0, ""
    except Exception as e:
        return 0, b"", time.perf_counter() - t0, str(e)[:120]


def run_bare(url):
    t0 = time.perf_counter()
    try:
        r = requests.get(url, timeout=30)
        return r.status_code, r.content, time.perf_counter() - t0, ""
    except Exception as e:
        return 0, b"", time.perf_counter() - t0, str(e)[:120]


def main():
    rows = []
    sites = [(c, u) for c, u in SITES if robots_ok(u)]
    print(len(sites), "sites after robots.txt")
    with sync_playwright() as pw:
        for i, (cat, url) in enumerate(sites, 1):
            row = {"category": cat, "url": url}
            try:
                final_url, headers = capture(pw, url)
                row["final_url"] = final_url
                row["captured_headers"] = len(headers)
                cmd = build_curl(final_url, headers)
                (CMDS / f"{i:02d}.sh").write_text(cmd + "\n", encoding="utf-8")
                code, conv_err = convert(cmd)
                (CMDS / f"{i:02d}.py").write_text(code, encoding="utf-8")
                kept = len(re.findall(r"^\s+'[^']+': '", code, re.M))
                row["converter_headers"] = kept
                row["converter_error"] = conv_err
                results = {}
                s, b, dt, err = run_curl(final_url, headers, CMDS / f"{i:02d}.curl.html")
                results["curl"] = {"status": s, "bytes": len(b), "verdict": judge(s, b), "s": round(dt, 2), "title": title_of(b), "err": err}
                s, b, dt, err = run_converted(code, CMDS / f"{i:02d}.requests.html")
                results["converter_requests"] = {"status": s, "bytes": len(b), "verdict": judge(s, b), "s": round(dt, 2), "title": title_of(b), "err": err}
                s, b, dt, err = run_cffi(final_url, headers)
                results["curl_cffi"] = {"status": s, "bytes": len(b), "verdict": judge(s, b), "s": round(dt, 2), "title": title_of(b), "err": err}
                s, b, dt, err = run_bare(final_url)
                results["bare_requests"] = {"status": s, "bytes": len(b), "verdict": judge(s, b), "s": round(dt, 2), "title": title_of(b), "err": err}
                row["results"] = results
            except Exception as e:
                row["error"] = str(e)[:160]
            rows.append(row)
            r = row.get("results", {})
            print(f"{i:2d}/{len(sites)} {url[:45]:46s} hdr {row.get('captured_headers')}->{row.get('converter_headers')} | curl {r.get('curl',{}).get('verdict','-'):8s} conv {r.get('converter_requests',{}).get('verdict','-'):8s} cffi {r.get('curl_cffi',{}).get('verdict','-'):8s} bare {r.get('bare_requests',{}).get('verdict','-'):8s}", flush=True)
            OUT.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("done", len(rows))


if __name__ == "__main__":
    main()
