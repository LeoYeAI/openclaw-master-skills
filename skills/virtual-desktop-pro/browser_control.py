#!/usr/bin/env python3
"""
Virtual Desktop — Browser Control v3
CDP to authenticated kasmweb/chrome + Playwright + CapSolver + Claude Vision
Usage: python3 browser_control.py [action] [args...]

Actions:
  screenshot  <url> [label]
  navigate    <url> [selector]
  click       <url> <selector>
  click_xy    <url> <x> <y>
  fill        <url> <selector> <value>
  select      <url> <selector> <value>
  hover       <url> <selector>
  scroll      <url> <direction> [pixels]
  keyboard    <url> <selector> <key>
  extract     <url> <selector> [output_file]
  wait_for    <url> <selector> [timeout_ms]
  upload      <url> <file_selector> <file_path>
  analyze     <image_path_or_url> [question]
  captcha     <url>
  workflow    <json_steps_file>
  status
"""
import sys, os, json, time, traceback, base64, requests
from datetime import datetime
from playwright.sync_api import sync_playwright

# ── Workspace paths ──
WORKSPACE   = os.environ.get("WORKSPACE", "/workspace")
SCREENSHOTS = f"{WORKSPACE}/screenshots"
LOGS        = f"{WORKSPACE}/logs/browser"
AUDIT       = f"{WORKSPACE}/AUDIT.md"
ERRORS      = f"{WORKSPACE}/.learnings/ERRORS.md"
LEARNINGS   = f"{WORKSPACE}/.learnings/LEARNINGS.md"

# ── Config ──
UA            = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
CDP_URL       = os.environ.get("BROWSER_CDP_URL", "http://browser:9222")
CAPSOLVER_KEY = os.environ.get("CAPSOLVER_API_KEY", "")
VPS_IP        = os.environ.get("VPS_IP", "YOUR_VPS_IP")

# ── Timestamp calculated per call, not at startup ──
def get_ts():
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")

def get_date():
    return datetime.now().strftime("%Y-%m-%d")

# ── Logging ──

def audit(msg):
    os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
    with open(AUDIT, "a") as f:
        f.write(f"\n[{get_ts()}] [virtual-desktop] {msg}\n")

def log_error(platform, title, what, cause, fix, prevention):
    os.makedirs(os.path.dirname(ERRORS), exist_ok=True)
    with open(ERRORS, "a") as f:
        f.write(
            f"\n## [{get_date()}] {platform} — {title}\n"
            f"**Logged**: {get_ts()}\n**Priority**: medium\n**Status**: pending\n"
            f"**Area**: browser_automation\n**What happened**: {what}\n"
            f"**Root cause**: {cause}\n**Fix applied**: {fix}\n**Prevention**: {prevention}\n"
        )

def log_learning(platform, category, discovery, usage):
    os.makedirs(os.path.dirname(LEARNINGS), exist_ok=True)
    with open(LEARNINGS, "a") as f:
        f.write(
            f"\n## [{get_date()}] {platform} — {category}\n"
            f"**Category**: {category}\n**Discovery**: {discovery}\n**Usage**: {usage}\n"
        )

def write_log(msg):
    os.makedirs(LOGS, exist_ok=True)
    with open(f"{LOGS}/{get_date()}.log", "a") as f:
        f.write(f"\n[{get_ts()}] {msg}\n")

# ── Browser ──

def get_browser(p):
    """CDP to kasmweb/chrome — session already authenticated. Headless fallback."""
    try:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context(
            user_agent=UA,
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            timezone_id="Europe/Paris",
            extra_http_headers={"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}
        )
        return browser, ctx
    except Exception:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        return browser, browser.new_context(
            user_agent=UA,
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            timezone_id="Europe/Paris"
        )

# ── Screenshot with per-call timestamp ──
def snap(page, label):
    os.makedirs(SCREENSHOTS, exist_ok=True)
    path = f"{SCREENSHOTS}/{get_ts()}_{label}.png"
    try:
        page.screenshot(path=path, full_page=True)
    except Exception as e:
        write_log(f"snap error ({label}): {e}")
    return path

# ── CAPTCHA ──

def detect_captcha(page):
    selectors = [
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        ".cf-turnstile",
        "[data-sitekey]",
        "iframe[src*='challenges.cloudflare']"
    ]
    for sel in selectors:
        try:
            if page.query_selector(sel):
                return True
        except Exception:
            pass
    try:
        text = page.inner_text("body").lower()
        return any(w in text for w in [
            "i'm not a robot", "je ne suis pas un robot",
            "verify you are human", "captcha"
        ])
    except Exception:
        return False

def solve_captcha_api(page_url, sitekey, kind="recaptcha"):
    if not CAPSOLVER_KEY:
        return None
    task_type = "HCaptchaTaskProxyless" if kind == "hcaptcha" else "ReCaptchaV2TaskProxyless"
    try:
        r = requests.post(
            "https://api.capsolver.com/createTask",
            json={"clientKey": CAPSOLVER_KEY, "task": {
                "type": task_type,
                "websiteURL": page_url,
                "websiteKey": sitekey
            }},
            timeout=30
        )
        task_id = r.json().get("taskId")
        if not task_id:
            return None
        for _ in range(30):
            time.sleep(3)
            res = requests.post(
                "https://api.capsolver.com/getTaskResult",
                json={"clientKey": CAPSOLVER_KEY, "taskId": task_id},
                timeout=10
            ).json()
            if res.get("status") == "ready":
                return res["solution"]["gRecaptchaResponse"]
    except Exception as e:
        write_log(f"CapSolver error: {e}")
    return None

def auto_solve_captcha(page):
    audit("CAPTCHA detected — autonomous resolution starting")
    el = page.query_selector("[data-sitekey]")
    if el:
        sitekey = el.get_attribute("data-sitekey")
        kind = "hcaptcha" if page.query_selector("iframe[src*='hcaptcha']") else "recaptcha"
        token = solve_captcha_api(page.url, sitekey, kind)
        if token:
            # Token passed via Playwright args — not interpolated in JS string
            page.evaluate("""(token) => {
                var el = document.querySelector('[name="g-recaptcha-response"],[name="h-captcha-response"]');
                if (el) el.value = token;
                try { ___grecaptcha_cfg.clients[0].aa.l.callback(token); } catch(e) {}
                try { hcaptcha.submit(); } catch(e) {}
            }""", token)
            time.sleep(2)
            audit("OK CAPTCHA solved via CapSolver")
            log_learning(page.url, "captcha", f"CAPTCHA {kind} solved", "CapSolver API token injection")
            return True

    if page.query_selector(".cf-turnstile, iframe[src*='challenges.cloudflare']"):
        audit("Cloudflare Turnstile detected — waiting for CapSolver extension 60s")
        time.sleep(60)
        if not detect_captcha(page):
            audit("OK Cloudflare Turnstile resolved")
            return True

    path = snap(page, "captcha_manual")
    audit(f"CAPTCHA not resolved automatically — screenshot: {path}")
    # IP read from .env
    print(f"⚠️ CAPTCHA manuel requis. Ouvre https://{VPS_IP}:6901 — Screenshot: {path}")
    return False

# ── Claude Vision ──

def cmd_analyze(src, question="Describe in detail what you see in this image."):
    audit(f"BEFORE analyze {src}")
    try:
        # If web page URL, take screenshot first
        if src.startswith("http") and not src.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            with sync_playwright() as p:
                browser, ctx = get_browser(p)
                page = ctx.new_page()
                page.goto(src)
                page.wait_for_load_state("networkidle")
                src = snap(page, "analyze")
                audit(f"OK screenshot for analyze: {src}")
                browser.close()

        # Read image
        if src.startswith("http"):
            img_data = base64.b64encode(requests.get(src, timeout=15).content).decode()
            mt = "image/jpeg"
        else:
            with open(src, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            mt = {
                "png": "image/png", "jpg": "image/jpeg",
                "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif"
            }.get(src.split(".")[-1].lower(), "image/png")

        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            print("❌ ANTHROPIC_API_KEY missing from .env")
            return

        # Verify API response before accessing content
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mt, "data": img_data}},
                    {"type": "text", "text": question}
                ]}]
            },
            timeout=30
        )
        data = resp.json()
        if "content" not in data:
            raise Exception(f"API error: {data.get('error', data)}")
        result = data["content"][0]["text"]

        out = f"{SCREENSHOTS}/{get_ts()}_analysis.txt"
        with open(out, "w") as f:
            f.write(f"# Analysis\n**Source**: {src}\n**Question**: {question}\n\n{result}\n")
        audit(f"OK analyze — saved: {out}")
        print(result)
        print(f"\n✅ Saved: {out}")

    except Exception as e:
        write_log(f"analyze error\n{traceback.format_exc()}")
        print(f"❌ {e}")

# ── run() helper — audit before browser.close() ──

def run(url, fn, label):
    audit(f"BEFORE {label} {url}")
    try:
        with sync_playwright() as p:
            browser, ctx = get_browser(p)
            page = ctx.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            if detect_captcha(page):
                auto_solve_captcha(page)
            result = fn(page)
            snap(page, label)
            audit(f"OK {label}")
            browser.close()
            return result
    except Exception as e:
        write_log(f"{label} error\n{traceback.format_exc()}")
        log_error("unknown", f"{label} failed", str(e), "see log", "screenshot taken", "check selector/url")
        print(f"❌ {e}")

# ── Commands ──

def cmd_screenshot(url, label="screenshot"):
    run(url, lambda p: None, label)
    print(f"✅ Screenshot: {SCREENSHOTS}/")

def cmd_navigate(url, selector=None):
    def fn(page):
        if selector:
            for el in page.query_selector_all(selector):
                print(el.inner_text())
        else:
            print(page.inner_text("body")[:5000])
    run(url, fn, "navigate")

def cmd_click(url, selector):
    def fn(page):
        page.click(selector)
        time.sleep(1.0)
        page.wait_for_load_state("networkidle")
        print(f"✅ Clicked: {selector}")
    run(url, fn, "click")

def cmd_click_xy(url, x, y):
    def fn(page):
        page.mouse.click(int(x), int(y))
        time.sleep(1.0)
        print(f"✅ Clicked: ({x},{y})")
    run(url, fn, f"click_xy_{x}_{y}")

def cmd_fill(url, selector, value):
    def fn(page):
        page.fill(selector, value)
        time.sleep(0.5)
        print(f"✅ Filled: {selector}")
    run(url, fn, "fill")

def cmd_select(url, selector, value):
    def fn(page):
        page.select_option(selector, value)
        time.sleep(0.5)
        print(f"✅ Selected: {value}")
    run(url, fn, "select")

def cmd_hover(url, selector):
    def fn(page):
        page.hover(selector)
        time.sleep(0.8)
        print(f"✅ Hovered: {selector}")
    run(url, fn, "hover")

def cmd_scroll(url, direction="down", pixels=500):
    m = {"down": (0, int(pixels)), "up": (0, -int(pixels)),
         "right": (int(pixels), 0), "left": (-int(pixels), 0)}
    dx, dy = m.get(direction, (0, int(pixels)))
    def fn(page):
        page.mouse.wheel(dx, dy)
        time.sleep(0.5)
        print(f"✅ Scrolled {direction} {pixels}px")
    run(url, fn, f"scroll_{direction}")

def cmd_keyboard(url, selector, key):
    def fn(page):
        page.click(selector)
        time.sleep(0.3)
        page.keyboard.press(key)
        time.sleep(0.5)
        print(f"✅ Key: {key}")
    run(url, fn, f"key_{key}")

def cmd_extract(url, selector, output_file=None):
    def fn(page):
        results = [
            {
                "text": el.inner_text().strip(),
                "href": el.get_attribute("href") or "",
                "src":  el.get_attribute("src")  or ""
            }
            for el in page.query_selector_all(selector)
        ]
        out = json.dumps(results, ensure_ascii=False, indent=2)
        if output_file:

            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w") as f:
                f.write(out)
            print(f"✅ Extracted {len(results)} items → {output_file}")
        else:
            print(out)
    run(url, fn, "extract")

def cmd_wait_for(url, selector, timeout_ms=10000):
    def fn(page):
        page.wait_for_selector(selector, timeout=int(timeout_ms))
        print(f"✅ Element appeared: {selector}")
    run(url, fn, "wait_for")

def cmd_upload(url, file_selector, file_path):
    def fn(page):
        page.set_input_files(file_selector, file_path)
        time.sleep(1.0)
        print(f"✅ Uploaded: {file_path}")
    run(url, fn, "upload")

def cmd_captcha(url):
    audit(f"BEFORE captcha {url}")
    try:
        with sync_playwright() as p:
            browser, ctx = get_browser(p)
            page = ctx.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            if detect_captcha(page):
                solved = auto_solve_captcha(page)
                snap(page, "captcha_result")
                audit(f"{'OK' if solved else 'FAILED'} captcha")
                browser.close()
                print(f"{'✅ CAPTCHA solved' if solved else '⚠️ Manual resolution required'}")
            else:
                snap(page, "no_captcha")
                audit("OK captcha — none detected")
                browser.close()
                print("✅ No CAPTCHA detected")
    except Exception as e:
        write_log(f"captcha error\n{traceback.format_exc()}")
        print(f"❌ {e}")

def cmd_workflow(steps_file):
    """
    Workflow JSON multi-étapes avec CAPTCHA auto + vision.
    Actions: goto, click, click_xy, fill, select, hover, scroll,
             keyboard, wait_for, extract, screenshot, wait, captcha, analyze
    """
    audit(f"BEFORE workflow {steps_file}")
    with open(steps_file) as f:
        steps = json.load(f)
    log = {"date": get_ts(), "file": steps_file, "steps": [], "status": "started"}
    try:
        with sync_playwright() as p:
            browser, ctx = get_browser(p)
            page = ctx.new_page()
            for i, step in enumerate(steps):
                a = step.get("action", "")
                t = step.get("target", "")
                v = step.get("value", "")
                try:
                    if a == "goto":
                        page.goto(t)
                        page.wait_for_load_state("networkidle")
                    
                        if detect_captcha(page):
                            auto_solve_captcha(page)
                    elif a == "click":
                        page.click(t); time.sleep(0.8)
                    elif a == "click_xy":
                        page.mouse.click(int(step.get("x", 0)), int(step.get("y", 0)))
                        time.sleep(0.8)
                    elif a == "fill":
                        page.fill(t, v); time.sleep(0.5)
                    elif a == "select":
                        page.select_option(t, v); time.sleep(0.5)
                    elif a == "hover":
                        page.hover(t); time.sleep(0.5)
                    elif a == "scroll":
                        m = {"down": (0,500), "up": (0,-500), "right": (500,0), "left": (-500,0)}
                        dx, dy = m.get(step.get("direction", "down"), (0, 500))
                        page.mouse.wheel(dx, dy); time.sleep(0.5)
                    elif a == "keyboard":
                        page.click(t); time.sleep(0.3); page.keyboard.press(v)
                    elif a == "wait_for":
                        page.wait_for_selector(t, timeout=int(step.get("timeout_ms", 10000)))
                    elif a == "wait":
                        time.sleep(float(v) if v else 1.0)
                    elif a == "extract":
                        data = [{"text": el.inner_text().strip()} for el in page.query_selector_all(t)]
                        if v:
                
                            os.makedirs(os.path.dirname(v), exist_ok=True)
                            with open(v, "w") as ef:
                                json.dump(data, ef, ensure_ascii=False, indent=2)
                    elif a == "screenshot":
                        snap(page, f"step{i}")
                    elif a == "captcha":
                        if detect_captcha(page):
                            auto_solve_captcha(page)
                    elif a == "analyze":
                        path = snap(page, f"step{i}_analyze")
                        cmd_analyze(path, v or "Describe this page in detail.")
                    else:
                        print(f"⚠️ Unknown action: {a}")

                    log["steps"].append({"step": i, "action": a, "status": "ok"})
                    print(f"✅ Step {i}: {a} {t}")

                except Exception as e:
                    log["steps"].append({"step": i, "action": a, "status": "failed", "error": str(e)})
                    snap(page, f"step{i}_error")
                    print(f"❌ Step {i} ({a}): {e}")

            log["status"] = "completed"
            snap(page, "workflow_done")
            audit("OK workflow completed")
            browser.close()

    except Exception as e:
        log["status"] = "failed"
        write_log(f"workflow error\n{traceback.format_exc()}")

    finally:
        mem = f"{WORKSPACE}/memory/{get_date()}.md"
        os.makedirs(os.path.dirname(mem), exist_ok=True)
        with open(mem, "a") as f:
            f.write(f"\n## Workflow — {get_ts()}\n```json\n{json.dumps(log, indent=2)}\n```\n")
        audit(f"{log['status']} workflow {steps_file}")
        print(f"{'✅' if log['status'] == 'completed' else '❌'} Workflow {log['status']}")

def cmd_status():
    cdp_ok = False
    try:
        cdp_ok = requests.get(f"{CDP_URL}/json", timeout=3).status_code == 200
    except Exception:
        pass
    checks = {
        "playwright":      os.system("which playwright > /dev/null 2>&1") == 0,
        "chrome_cdp":      cdp_ok,
        "screenshots_dir": os.path.exists(SCREENSHOTS),
        "audit_file":      os.path.exists(AUDIT),
        "capsolver":       bool(CAPSOLVER_KEY),
        "browserbase":     bool(os.environ.get("BROWSERBASE_API_KEY", "")),
        "claude_vision":   bool(os.environ.get("ANTHROPIC_API_KEY", "")),
    }
    print("\n🖥️ Virtual Desktop v3 — Status")
    for k, v in checks.items():
        print(f"  {'✅' if v else '❌'} {k}")

# ── CLI Dispatcher ──
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    a = sys.argv[1]
    args = sys.argv[2:]
    if   a == "screenshot": cmd_screenshot(args[0], args[1] if len(args) > 1 else "screenshot")
    elif a == "navigate":   cmd_navigate(args[0], args[1] if len(args) > 1 else None)
    elif a == "click":      cmd_click(args[0], args[1])
    elif a == "click_xy":   cmd_click_xy(args[0], args[1], args[2])
    elif a == "fill":       cmd_fill(args[0], args[1], args[2])
    elif a == "select":     cmd_select(args[0], args[1], args[2])
    elif a == "hover":      cmd_hover(args[0], args[1])
    elif a == "scroll":     cmd_scroll(args[0], args[1] if len(args) > 1 else "down", args[2] if len(args) > 2 else 500)
    elif a == "keyboard":   cmd_keyboard(args[0], args[1], args[2])
    elif a == "extract":    cmd_extract(args[0], args[1], args[2] if len(args) > 2 else None)
    elif a == "wait_for":   cmd_wait_for(args[0], args[1], args[2] if len(args) > 2 else 10000)
    elif a == "upload":     cmd_upload(args[0], args[1], args[2])
    elif a == "analyze":    cmd_analyze(args[0], args[1] if len(args) > 1 else "Describe what you see.")
    elif a == "captcha":    cmd_captcha(args[0])
    elif a == "workflow":   cmd_workflow(args[0])
    elif a == "status":     cmd_status()
    else:
        print(f"❌ Unknown action: {a}")
        print(__doc__)
