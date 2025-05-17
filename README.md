# Email Scraper

Automates lookups in a student directory and writes Name→Email mappings to a CSV, with built‑in login and 2FA handling, checkpointing, and optional headless mode.

## 🚀 Prerequisites

- **Python 3.10+**  
- **Google Chrome** (version matching your ChromeDriver)  
- **ChromeDriver** on your `PATH`  

## 🔧 Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR‑USERNAME/email_scraper.git
cd email_scraper

# 2. Create & activate a venv
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# or  .\venv\Scripts\activate   # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration
Copy the template:
```bash
cp config.template.py config.py
```
Open config.py and set your own paths:
```bash
# Path to your input CSV (must have a "Name" column):
NAMES_FILE  = 'path/to/input.csv'

# Path to write the output CSV:
OUTPUT_FILE = 'path/to/output.csv'
```
Note: config.py is listed in .gitignore, so your real file never gets committed.

## 🖥 ChromeDriver Setup
Check your Chrome version via chrome://version.

Download the matching driver from:
https://googlechromelabs.github.io/chrome-for-testing/

Unzip and move chromedriver into /usr/local/bin (or any folder on your PATH):

```bash
chmod +x chromedriver
sudo mv chromedriver /usr/local/bin/
```

## ▶️ First Run (Headed)
This initial run saves your authenticated cookies:

```bash
python lookup_emails.py
```
A browser window will open.
Click Sign in for student search, complete your UW NetID + Duo 2FA, and wait for the redirect.

Back in the terminal, press Enter.

You’ll see a small output CSV and a new cookies.pkl file.

## 🔄 Checkpointing & Resume
Ctrl+C at any time stops the script safely—your CSV is intact.

Re‑running the same command will skip names already present in the output and resume where it left off.
