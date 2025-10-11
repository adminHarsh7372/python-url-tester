🔍 URL Scrapability Tester

A small but powerful Python + Playwright project that checks how scrapable a website is.
It helps you quickly understand what kind of tech stack, bot protection, or JS rendering a site uses — before you build a scraper.

⚙️ Features

✅ Checks robots.txt permissions
✅ Detects common bot protection (CAPTCHA, Cloudflare, PerimeterX, Datadome, etc.)
✅ Identifies JavaScript-heavy frameworks (React, Next.js, Vue, Angular, etc.)
✅ Estimates scrapability score (0–100) with difficulty level
✅ Detects if login/authentication is required
✅ Captures screenshots to verify bot blocks or page rendering
✅ Reports HTTP status codes and final redirected URLs
✅ Intelligent retries and progressive waits for JS-heavy pages
✅ Simple CLI usage
✅ Lightweight stealth built-in (randomized user-agent, WebGL tweaks, navigator masking)

🧩 Installation
git clone https://github.com/YOUR_USERNAME/url-tester.git
cd url-tester
pip install -r requirements.txt
playwright install chromium

🏁 Usage
Basic
python scraper.py --url https://example.com

Headed (GUI) Mode
python scraper.py --url https://example.com --headed

Headless Mode
python scraper.py --url https://example.com --headless

Disable Screenshot Capture
python scraper.py --url https://example.com --no-screenshot

📸 Screenshot Capture

The scraper saves a screenshot of the page by default to the ./screenshots folder.
This is useful for confirming if the site triggered a CAPTCHA, bot detection, or did not fully render.

📊 What It Reports

robots.txt permissions

HTTP status code and final redirected URL

Page title

Bot protection detection

Detected frameworks/technologies

JavaScript rendering requirement

Login/authentication requirement

Scrapability score (0–100) and difficulty level

Screenshot path (if enabled)
