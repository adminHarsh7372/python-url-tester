# 🔍 URL Scrapability Tester

A small but powerful Python + Playwright project that checks how *scrapable* a website is.  
It helps you quickly understand what kind of tech stack, bot protection, or JS rendering a site uses — before you build a scraper.

---

## ⚙️ Features

✅ Checks `robots.txt` permissions  
✅ Detects common bot protection (CAPTCHA, Cloudflare, etc.)  
✅ Identifies JavaScript-heavy frameworks  
✅ Estimates scrapability score (0–100)  
✅ Simple CLI usage  
✅ Lightweight stealth built-in  

---

## 🧩 Installation

```bash
git clone https://github.com/YOUR_USERNAME/url-tester.git
cd url-tester
pip install -r requirements.txt
playwright install chromium
