from playwright.sync_api import sync_playwright
import urllib.robotparser
from urllib.parse import urlparse

# ================================
# 🔧 CONFIGURATION
# ================================
PROXY = "http://scrapeops:7f789021-1945-4950-9ff1-2c1a15a5937c@residential-proxy.scrapeops.io:8181"
USERNAME = "7f789021-1945-4950-9ff1-2c1a15a5937c"
PASSWORD = "7f789021-1945-4950-9ff1-2c1a15a5937c"

# URL of the target site
TEST_URL = "https://www.amazon.in/"

# ================================
# 🧩 CHECK ROBOTS.TXT
# ================================
def check_robots(url):
    robots_url = url.rstrip("/") + "/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        allowed = rp.can_fetch("*", url)
        return allowed
    except:
        return None

# ================================
# 🧠 ANALYZE SITE TECH STACK
# ================================
def analyze_tech_stack(page_content):
    tech_score_penalty = 0
    tech = []
    if "wp-content" in page_content:
        tech.append("WordPress CMS")
    if "Shopify.theme" in page_content:
        tech.append("Shopify store")
        tech_score_penalty += 5
    if "data-reactroot" in page_content or "React." in page_content:
        tech.append("React.js frontend")
        tech_score_penalty += 15
    if "vue" in page_content:
        tech.append("Vue.js frontend")
        tech_score_penalty += 15
    if "angular" in page_content:
        tech.append("Angular frontend")
        tech_score_penalty += 15
    if "Cloudflare" in page_content:
        tech.append("Cloudflare protection")
        tech_score_penalty += 20
    return tech, tech_score_penalty

# ================================
# 🚧 DETECT BOT PROTECTION
# ================================
def detect_bot_protection(content):
    patterns = ["captcha", "access denied", "bot detected", "unusual traffic", "are you human", "cloudflare"]
    for p in patterns:
        if p in content.lower():
            return True
    return False

# ================================
# 🧾 SCRAPABILITY SCORE ANALYZER
# ================================
def scrape_readiness_report(url):
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
        try:
            browser = p.chromium.launch(
                headless=False,
                proxy={"server": PROXY, "username": USERNAME, "password": PASSWORD}
            )
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
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

            # JS rendering check
            js_required = "<noscript>" in content or "defer" in content or "async" in content
            if js_required:
                print("⚙️ JavaScript rendering required")
                score -= 10
            else:
                print("✅ Minimal JS rendering")

            # Login detection
            login_required = "login" in content.lower() or "sign in" in content.lower()
            if login_required:
                print("⚠️ Login/authentication required")
                score -= 20
            else:
                print("✅ No login required")

            # Ensure score is between 0–100
            score = max(0, min(100, score))
            print("\n🧾 SCRAPABILITY SCORE:", score, "/100")

            # Recommendations
            print("\n🔧 Recommendations:")
            if bot_prot:
                print("- Use rotating residential proxies")
                print("- Add random user-agents and delays")
            if js_required:
                print("- Use Playwright or Selenium (JS rendering required)")
            else:
                print("- Static scraping (Requests + BeautifulSoup) may work")
            if login_required:
                print("- Implement login/authentication before scraping")
            print("- Test selectors before bulk scraping")
            print("="*60)

        except Exception as e:
            print(f"❌ Could not load page: {e}")
        finally:
            browser.close()

# ================================
# ▶️ RUN THE SCRAPABILITY TEST
# ================================
scrape_readiness_report(TEST_URL)
