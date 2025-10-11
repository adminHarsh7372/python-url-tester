from playwright.sync_api import sync_playwright
import urllib.robotparser
from urllib.parse import urlparse
import os
import random
import argparse
import time

# ================================
# 🔧 CONFIGURATION
# ================================
PROXY = os.getenv("PROXY", "")
USERNAME = os.getenv("PROXY_USER", "")
PASSWORD = os.getenv("PROXY_PASS", "")
TEST_URL = os.getenv("TEST_URL", "https://example.com")
DEFAULT_HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "./screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
]

# ================================
# 🤖 ROBOTS CHECK
# ================================
def check_robots(url):
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception:
            return None
        return rp.can_fetch("*", "/")
    except Exception:
        return None

# ================================
# 🧠 TECH STACK DETECTION
# ================================
def analyze_tech_stack(page_content):
    c = page_content.lower()
    tech = []
    penalty = 0
    patterns = {
        "WordPress CMS": ["wp-content", "wordpress"],
        "Shopify store": ["shopify", "cdn.shopify.com"],
        "React.js frontend": ["react.", "react-dom", "data-reactroot"],
        "Next.js": ["_next", "__NEXT_DATA__"],
        "Vue.js frontend": ["vue"],
        "Angular frontend": ["angular"],
        "Cloudflare protection": ["cloudflare"],
        "Wix Site": ["wixstatic", "wix.com"],
        "Squarespace": ["squarespace"],
        "Astro/Gatsby static": ["astro.build", "gatsby"],
    }
    weights = {
        "WordPress CMS": 5, "Shopify store": 8, "React.js frontend": 15, "Next.js": 15,
        "Vue.js frontend": 15, "Angular frontend": 15, "Cloudflare protection": 20,
        "Wix Site": 10, "Squarespace": 10, "Astro/Gatsby static": 5,
    }
    for tech_name, keys in patterns.items():
        if any(k in c for k in keys):
            tech.append(tech_name)
            penalty += weights[tech_name]
    return tech, penalty

# ================================
# 🚧 BOT DETECTION
# ================================
def detect_bot_protection(content, page):
    c = (content or "").lower()
    textual_patterns = [
        "captcha", "recaptcha", "access denied", "bot detected",
        "unusual traffic", "are you human", "datadome", "perimeterx", "blocked",
        "cf-browser-verification", "checking your browser"
    ]
    if any(p in c for p in textual_patterns):
        return True
    try:
        if page.query_selector('iframe[src*="recaptcha"]') or page.query_selector('.g-recaptcha'):
            return True
        if page.query_selector('div[id="challenge-form"]') or page.query_selector('div[class*="cf-browser-verification"]'):
            return True
        if page.query_selector('script[src*="perimeterx"]') or page.query_selector('script[src*="datadome"]'):
            return True
    except Exception:
        return True
    return False

# ================================
# 🛡️ STEALTH 
# ================================
def apply_stealth(page):
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    page.add_init_script("window.chrome = window.chrome || { runtime: {} };")
    page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
        Object.defineProperty(navigator, 'mimeTypes', {get: () => [1,2,3]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
    """)
    vendor = random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"])
    renderer = random.choice(["Intel Iris OpenGL", "NVIDIA GeForce GTX", "AMD Radeon RX"])
    page.add_init_script(f"""
        try {{
          const getParameter = WebGLRenderingContext.getParameter;
          WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{vendor}';
            if (param === 37446) return '{renderer}';
            return getParameter.call(this, param);
          }};
        }} catch (e) {{}}
    """)

# ================================
# 🧾 MAIN SCRAPE READINESS REPORT
# ================================
def scrape_readiness_report(url, headless=DEFAULT_HEADLESS, proxy=PROXY, username=USERNAME, password=PASSWORD, take_screenshot=True):
    if not url:
        print("❌ No URL provided.")
        return

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    domain = urlparse(url).netloc
    print(f"\n🔍 Analyzing: {domain}")
    print("="*60)
    score = 100

    robots_allowed = check_robots(url)
    if robots_allowed is True:
        print("✅ robots.txt allows scraping")
    elif robots_allowed is False:
        print("⚠️ robots.txt disallows scraping")
        score -= 15
    else:
        print("❓ robots.txt unreadable or missing")
        score -= 5

    with sync_playwright() as p:
        browser = None
        context = None
        try:
            ua = random.choice(USER_AGENTS)
            launch_kwargs = {"headless": headless}
            if proxy:
                launch_kwargs["proxy"] = {"server": proxy, "username": username, "password": password}

            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(user_agent=ua, viewport={"width":1920,"height":1080}, ignore_https_errors=True)
            page = context.new_page()
            apply_stealth(page)

            # 🔹 LOAD BLOCK (reliable for JS-heavy sites)
            max_attempts = 3
            attempts = 0
            last_exception = None
            response = None
            while attempts < max_attempts:
                try:
                    response = page.goto(url, timeout=45000, wait_until="load")  # use "load" instead of "networkidle"
                    # Short wait for JS-heavy content if detected
                    js_markers = ["_next", "reactroot", "data-reactroot", "window.__INITIAL_STATE__"]
                    if any(m in page.content().lower() for m in js_markers):
                        page.wait_for_timeout(3000)  # 3 seconds
                    break
                except Exception as e:
                    attempts += 1
                    last_exception = e
                    time.sleep(1)
                    if attempts == max_attempts:
                        print(f"❌ Failed to load page after {max_attempts} attempts: {e}")
                        break

            # HTTP status and redirects
            status = response.status if response else "Unknown"
            final_url = page.url if page else url
            print(f"✅ HTTP status: {status}, final URL after redirects: {final_url}")

            title = page.title() or "No title"
            content = page.content()
            print(f"✅ Page loaded. Title: {title}")

            bot_prot = detect_bot_protection(content, page)
            print("⚠️ Bot protection detected" if bot_prot else "✅ No obvious bot protection")
            if bot_prot:
                score -= 30

            tech, penalty = analyze_tech_stack(content)
            if tech:
                print(f"🧠 Detected technologies: {', '.join(tech)}")
                score -= penalty
            else:
                print("ℹ️ No specific frameworks detected")

            # JS rendering detection
            js_markers = ["<noscript", "_next", "defer", "async", "reactroot", "data-reactroot", "id=\"__next\"", "window.__INITIAL_STATE__"]
            js_required = any(m in content.lower() for m in js_markers)
            try:
                body_text = page.inner_text("body")[:200].strip()
                if len(body_text) < 50 and js_required:
                    js_required = True
            except Exception:
                js_required = True
            print("⚙️ JavaScript rendering required" if js_required else "✅ Minimal JS rendering")
            if js_required:
                score -= 12

            # Improved login detection
            login_required = False
            try:
                if page.query_selector('input[type="password"]') or page.query_selector('form[action*="login"], form[action*="signin"]'):
                    login_required = True
                else:
                    lc = content.lower()
                    if any(k in lc for k in ["login", "sign in", "signin", "auth", "password", "sign-in"]):
                        login_required = True
            except Exception:
                login_required = True
            print("⚠️ Login/authentication required" if login_required else "✅ No login required")
            if login_required:
                score -= 20

            # Optional screenshot capture
            if take_screenshot:
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"{domain.replace('.', '_')}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")

            score = max(0, min(100, score))
            print(f"\n🧾 SCRAPABILITY SCORE: {score}/100")
            if score >= 80:
                level = "🟢 Easy"
            elif score >= 50:
                level = "🟡 Moderate"
            else:
                level = "🔴 Hard"
            print(f"🏁 Difficulty Level: {level}")

        except Exception as e:
            print(f"❌ Could not load page: {e}")
            if 'last_exception' in locals() and last_exception:
                print("Last exception:", last_exception)
        finally:
            if context:
                context.close()
            if browser:
                browser.close()

# ================================
# ▶️ CLI
# ================================
def parse_args():
    parser = argparse.ArgumentParser(description="URL Scrapability Tester")
    parser.add_argument("--url", "-u", type=str, help="URL to analyze")
    parser.add_argument("--headless", action="store_true", help="Force headless mode")
    parser.add_argument("--headed", action="store_true", help="Run with GUI")
    parser.add_argument("--no-screenshot", action="store_true", help="Disable screenshot capture")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    chosen_url = args.url or TEST_URL
    headless_flag = DEFAULT_HEADLESS
    if args.headless:
        headless_flag = True
    if args.headed:
        headless_flag = False

    scrape_readiness_report(
        chosen_url,
        headless=headless_flag,
        proxy=PROXY,
        username=USERNAME,
        password=PASSWORD,
        take_screenshot=not args.no_screenshot
    )
