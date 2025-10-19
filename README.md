<h1 align="center">🧠 URL Scrapability Tester</h1>

<p align="center">
  <b>Smart, automated analyzer that checks if a website is scrapable — safely and efficiently.</b><br>
  Built with <a href="https://playwright.dev/python/">Playwright</a> to detect bot protection, rendering complexity, and more.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-Automation-success?logo=microsoft-edge" alt="Playwright">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen" alt="Status">
</p>

---

## ⚙️ Overview

The **URL Scrapability Tester** is an automated utility that evaluates whether a website can be scraped effectively.  
It performs **ethical, pre-scraping diagnostics** to determine if a target site allows or blocks automated requests — without breaking rules.

### 🧩 Key Capabilities
- ✅ Checks **robots.txt** permissions  
- ⚙️ Detects **JavaScript rendering** and **login barriers**  
- 🧠 Identifies **frontend frameworks** (React, Next.js, WordPress, etc.)  
- 🛡️ Scans for **bot detection systems** (reCAPTCHA, Cloudflare, DataDome, etc.)  
- 📸 Captures **full-page screenshots** for reports  
- 🔢 Generates a **Scrapability Score (0–100)** with difficulty levels  

---

## 🧠 Scrapability Score System

| Factor | Impact | Penalty |
|--------|---------|----------|
| `robots.txt` disallows scraping | Medium | −15 |
| Bot protection (CAPTCHA, CF, etc.) | Critical | −30 |
| JavaScript rendering required | Medium | −12 |
| Login required | High | −20 |
| Heavy frontend tech (React, Shopify, etc.) | Variable | −5 to −20 |

**Score Range & Difficulty:**
| Score | Level |
|--------|--------|
| 80–100 | 🟢 Easy |
| 50–79  | 🟡 Moderate |
| 0–49   | 🔴 Hard |

---

## 🖼️ Example Output = examples-output.txt

