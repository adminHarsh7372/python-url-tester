from playwright.sync_api import sync_playwright
import urllib.robotparser
from urllib.parse import urlparse
import os
import random
import argparse
import sys
import time

# ================================
# 🔧 CONFIGURATION (use env when possible)
# ================================
# You can still hardcode, but env vars are preferred for credentials
PROXY = os.getenv("SCRAPE_PROXY", "http://scrapeops:7f789021-1945-4950-9ff1-2c1a15a5937c@residential-proxy.scrapeops.io:8181")
USERNAME = os.getenv("SCRAPE_USERNAME", "7f789021-1945-4950-9ff1-2c1a15a5937c")
PASSWORD = os.getenv("SCRAPE_PASSWORD", "7f789021-1945-4950-9ff1-2c1a15a5937c")

# Default URL (can be overridden by CLI arg)
TEST_URL = os.getenv("TEST_URL", "https://books.toscrape.com/")

# Default headless controlled by env or CLI
DEFAULT_HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")

# ================================
# 🧩 CHECK ROBOTS.TXT (more robust)
# ================================
def check_robots(url):
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            # assume https if scheme missing
            url = "https://" + url
            parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        # Use the path for can_fetch, not the full url
        path = parsed.path or "/"
        allowed = rp.can_fetch("*", path)
        return allowed
    except Exception:
        return None

# ================================
# 🧠 ANALYZE SITE TECH STACK (add common patterns)
# ================================
def analyze_tech_stack(page_content):
    tech_score_penalty = 0
    tech = []
    c = page_content.lower()
    if "wp-content" in c or "wordpress" in c:
        tech.append("WordPress CMS")
    if "shopify" in c or "cdn.shopify.com" in c:
        tech.append("Shopify store")
        tech_score_penalty += 5
    if "data-reactroot" in c or "react." in c or "react-dom" in c:
        tech.append("React.js frontend")
        tech_score_penalty += 15
    if "_next" in c:
        tech.append("Next.js")
        tech_score_penalty += 15
    if "vue" in c and "vue" not in tech:
        tech.append("Vue.js frontend")
        tech_score_penalty += 15
    if "angular" in c:
        tech.append("Angular frontend")
        tech_score_penalty += 15
    if "cloudflare" in c:
        tech.append("Cloudflare protection")
        tech_score_penalty += 20
    if "wixstatic" in c or "wix.com" in c:
        tech.append("Wix Site")
        tech_score_penalty += 10
    if "squarespace" in c:
        tech.append("Squarespace")
        tech_score_penalty += 10
    return tech, tech_score_penalty

# ================================
# 🚧 DETECT BOT PROTECTION (expanded)
# ================================
def detect_bot_protection(content):
    patterns = [
        "captcha", "recaptcha", "access denied", "bot detected", "unusual traffic",
        "are you human", "cloudflare", "datadome", "perimeterx", "blocked"
    ]
    c = content.lower()
    for p in patterns:
        if p in c:
            return True
    return False

# ================================
# 🛡️ LIGHTWEIGHT STEALTH (improved small randomness)
# ================================
def apply_stealth(page):
    """
    Lightweight stealth to reduce obvious automation fingerprints.
    Not a full bypass for advanced fingerprinting/CAPTCHAs.
    """
    # webdriver flag
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

    # plugins & mimeTypes
    page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
        Object.defineProperty(navigator, 'mimeTypes', { get: () => [1,2,3] });
    """)

    # languages
    page.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});")

    # permissions.query spoof
    page.add_init_script("""
        const __origQuery = navigator.permissions && navigator.permissions.query;
        if (__origQuery) {
            navigator.permissions.__proto__.query = function(parameters) {
                if (parameters && parameters.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission });
                }
                return __origQuery(parameters);
            };
        }
    """)

    # webgl vendor/renderer spoof with small randomness
    vendor = random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"])
    renderer = random.choice([
        "Intel Iris OpenGL Engine",
        "NVIDIA GeForce GTX",
        "AMD Radeon RX"
    ])
    page.add_init_script(f"""
        try {{
          const getParameter = WebGLRenderingContext.getParameter;
          WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) return '{vendor}';
            if (parameter === 37446) return '{renderer}';
            return getParameter.call(this, parameter);
          }};
        }} catch (e) {{}}
    """)

    # platform
    platforms = ["Win32", "MacIntel", "Linux x86_64"]
    page.add_init_script(f"Object.defineProperty(navigator, 'platform', {{get: () => '{random.choice(platforms)}'}});")

    # chrome runtime stub
    page.add_init_script("window.chrome = window.chrome || { runtime: {} };")

# ================================
# 🧾 SCRAPABILITY SCORE ANALYZER
# ================================
def scrape_readiness_report(url, headless=DEFAULT_HEADLESS, proxy=PROXY, username=USERNAME, password=PASSWORD):
    if not url:
        print("❌ No URL provided. Set TEST_URL or pass via --url.")
        return

    # Ensure scheme present
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url

    domain = urlparse(url).netloc
    print(f"\n🔍 Analyzing: {domain}")
    print("="*60)

    # STEP 1: robots.txt
    robots_allowed = check_robots(url)
    score = 100  # start with perfect score

    if robots_allowed is True:
        print("✅ robots.txt allows scraping")
    elif robots_allowed is False:
        print("⚠️ robots.txt disallows scraping")
        score -= 15
    else:
        print("❓ robots.txt unreadable")
        score -= 5

    # STEP 2: Playwright load
    with sync_playwright() as p:
        browser = None
        context = None
        try:
            launch_kwargs = {
                "headless": headless
            }
            # only provide proxy if set
            if proxy:
                launch_kwargs["proxy"] = {"server": proxy, "username": username, "password": password}

            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()

            # apply stealth scripts
            apply_stealth(page)

            # navigate
            page.goto(url, timeout=120000)
            # prefer a networkidle wait for dynamic pages (more robust)
            try:
                page.wait_for_load_state("networkidle", timeout=60000)
            except Exception:
                # fallback: short sleep to allow JS to settle
                time.sleep(2)

            # attempt to ensure some visible content
            try:
                first_visible = page.query_selector("body *:not(script):not(style)")
                if first_visible:
                    try:
                        first_visible.wait_for_element_state("visible", timeout=15000)
                    except Exception:
                        pass
            except Exception:
                pass

            title = page.title()
            content = page.content()
            print(f"✅ Page loaded. Title: {title}")

            # Bot protection
            bot_prot = detect_bot_protection(content)
            if bot_prot:
                print("⚠️ Bot protection detected")
                score -= 25
            else:
                print("✅ No obvious bot protection")

            # Tech stack
            tech, tech_penalty = analyze_tech_stack(content)
            if tech:
                print(f"🧠 Detected technologies: {', '.join(tech)}")
                score -= tech_penalty
            else:
                print("ℹ️ No specific frameworks detected")

            # JS rendering check (improved detection)
            js_required = "<noscript" in content.lower() or "defer" in content.lower() or "async" in content.lower() or "_next" in content.lower()
            if js_required:
                print("⚙️ JavaScript rendering required")
                score -= 10
            else:
                print("✅ Minimal JS rendering")

            # Login detection (improved keywords)
            lc = content.lower()
            login_required = any(k in lc for k in ["login", "sign in", "signin", "account", "auth", "password"])
            if login_required:
                print("⚠️ Login/authentication required")
                score -= 20
            else:
                print("✅ No login required")

            # Ensure score in range
            score = max(0, min(100, score))
            print("\n🧾 SCRAPABILITY SCORE:", score, "/100")

            # Difficulty label (new, but simple)
            if score >= 80:
                level = "🟢 Easy"
            elif score >= 50:
                level = "🟡 Moderate"
            else:
                level = "🔴 Hard"
            print(f"🏁 Difficulty Level: {level}")

            # Recommendations (mostly same as your original)
            print("\n🔧 Recommendations:")
            if bot_prot:
                print("- Use rotating residential proxies")
                print("- Add random user-agents and delays")
            if js_required:
                print("- Use Playwright (JS rendering required)")
            else:
                print("- Static scraping (Requests + scrapy) may work")
            if login_required:
                print("- Implement login/authentication before scraping")
            print("- Test selectors before bulk scraping")
            print("="*60)

        except Exception as e:
            print(f"❌ Could not load page: {e}")
        finally:
            try:
                if context:
                    context.close()
            except Exception:
                pass
            try:
                if browser:
                    browser.close()
            except Exception:
                pass

# ================================
# ▶️ CLI bootstrap (keeps behavior same but adds flexibility)
# ================================
def parse_args():
    parser = argparse.ArgumentParser(description="Scrapability / URL readiness checker (keeps print output similar).")
    parser.add_argument("--url", "-u", type=str, help="URL to analyze (overrides TEST_URL)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (overrides env)")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    chosen_url = args.url or TEST_URL
    headless_flag = DEFAULT_HEADLESS
    if args.headless:
        headless_flag = True
    if args.headed:
        headless_flag = False

    scrape_readiness_report(chosen_url, headless=headless_flag, proxy=PROXY, username=USERNAME, password=PASSWORD)



