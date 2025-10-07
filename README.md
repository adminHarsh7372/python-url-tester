# test-url-boiler

A Python tool to analyze websites before scraping.

# This script helps freelancers and developers quickly assess the scrapability of a website by checking:

robots.txt permissions

Page load success with Playwright

Anti-bot protections (CAPTCHA, Cloudflare, etc.)

Frontend frameworks and tech stack (React, Vue, Shopify, WordPress, etc.)

JavaScript rendering requirements

Login/authentication requirements

Generates a Scrapability Score (0–100) with actionable recommendations

# Features

✅ Detects if scraping is allowed via robots.txt

✅ Launches the site with Playwright to test accessibility

✅ Identifies bot protection mechanisms

✅ Detects JS-heavy frameworks or CMS

✅ Flags login pages or restricted areas

✅ Provides step-by-step recommendations for scraping

✅ Calculates a numeric Scrapability Score

# Requirements

Python 3.10+

Playwright

Requests library (for HTTP checks)

Installation

Create a virtual environment:

python -m venv scraper_env


Activate the environment:

# Windows
scraper_env\Scripts\activate

# macOS/Linux
source scraper_env/bin/activate


Install dependencies:

pip install playwright requests


Install Playwright browsers:

playwright install

Usage

Open the script url_checker.py (or your filename)

Set the target URL at the top of the script:

TEST_URL = ""


If using a proxy, update the proxy credentials:

PROXY = "http://scrapeops:YOUR-API-KEY@residential-proxy.scrapeops.io:8181"
USERNAME = "YOUR-API-KEY"
PASSWORD = "YOUR-API-KEY"


Run the script:

python url_checker.py


# The output will include:

Robots.txt permission

Page load success

Detected frameworks/tech

Anti-bot detection

JS rendering requirement

Login requirement

Scrapability Score (0–100)

Actionable recommendations

Example Output
🔍 Analyzing: www.example.com
============================================================
✅ robots.txt allows scraping
✅ Page loaded successfully. Title: Tripadvisor
⚠️ Bot protection detected
🧠 Detected technologies: React.js frontend, Cloudflare protection
⚙️ JavaScript rendering required
✅ No login required
🧾 SCRAPABILITY SCORE: 60 / 100
🔧 Recommendations:
- Use rotating residential proxies
- Add random user-agents and delays
- Use Playwright or Selenium (JS rendering required)
- Test selectors before bulk scraping
============================================================
