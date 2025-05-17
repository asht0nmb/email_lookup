import os
import csv
import time
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, InvalidSessionIdException

# ——— CONFIG ———
WRITE_RESULTS                = False  # <- Make 'False' to test - 'True' to output csv
LOGIN_URL                    = 'https://directory.uw.edu/'
SEARCH_URL                   = 'https://directory.uw.edu/'
SIGNIN_BUTTON_SELECTOR       = (By.CSS_SELECTOR, '#sign-in')
SEARCH_INPUT_SELECTOR        = (By.ID, 'query')
STUDENTS_ONLY_LABEL_SELECTOR = (By.CSS_SELECTOR, '#search-population > div > label:nth-child(2)')
RESULT_ROW_SELECTOR          = (By.CSS_SELECTOR, 'table.table-condensed tbody tr.summary-row')
EMAIL_CELL_SELECTOR          = (By.CSS_SELECTOR, 'td:nth-child(3)')
COOKIES_FILE                 = 'cookies.pkl'

import config
NAMES_FILE                   = config.NAMES_FILE
OUTPUT_FILE                  = config.OUTPUT_FILE
# ——————————

def get_authenticated_driver():
    driver = webdriver.Chrome()
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(SIGNIN_BUTTON_SELECTOR)
    ).click()
    input("Complete UW login + Duo 2FA in the browser, then press Enter here…")
    pickle.dump(driver.get_cookies(), open(COOKIES_FILE, 'wb'))
    return driver

driver = get_authenticated_driver()

# Navigate & select “Students Only”
driver.get(SEARCH_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located(SEARCH_INPUT_SELECTOR))
WebDriverWait(driver, 10).until(EC.element_to_be_clickable(STUDENTS_ONLY_LABEL_SELECTOR)).click()

# ——— BUILD CHECKPOINT LIST ———
processed = set()
mode = 'w'
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, newline='') as existing:
        reader_existing = csv.reader(existing)
        next(reader_existing, None)  # skip header
        for r in reader_existing:
            processed.add(r[0])
    mode = 'a'

# ——— CSV SETUP & MAIN LOOP ———
with open(OUTPUT_FILE, mode, newline='') as out, open(NAMES_FILE, newline='') as names_csv:
    writer = csv.writer(out)
    reader = csv.DictReader(names_csv)

    if mode == 'w' and WRITE_RESULTS:
        writer.writerow(['Name', 'Email', 'Notes'])

    for row in reader:
        name = row['Name'].strip()
        if not name or name in processed:
            continue

        try:
            # 1) Capture the current first row (if any)
            try:
                old_first = driver.find_elements(*RESULT_ROW_SELECTOR)[0]
            except IndexError:
                old_first = None

            # 2) Type + submit
            box = driver.find_element(*SEARCH_INPUT_SELECTOR)
            box.clear()
            box.send_keys(name + Keys.RETURN)

            # 3) Wait for the old row to go stale
            if old_first:
                WebDriverWait(driver, 2.5).until(EC.staleness_of(old_first))

            # 4) Gather new rows
            try:
                WebDriverWait(driver, 2).until(
                    EC.presence_of_all_elements_located(RESULT_ROW_SELECTOR)
                )
                rows = driver.find_elements(*RESULT_ROW_SELECTOR)
            except:
                rows = []

            # 5) Scrape email
            if len(rows) == 1:
                try:
                    email = rows[0].find_element(*EMAIL_CELL_SELECTOR).text.strip()
                except StaleElementReferenceException:
                    rows = driver.find_elements(*RESULT_ROW_SELECTOR)
                    email = rows[0].find_element(*EMAIL_CELL_SELECTOR).text.strip()
                notes = ''
            elif len(rows) > 1:
                email = rows[0].find_element(*EMAIL_CELL_SELECTOR).text.strip()
                notes = f'{len(rows)} matches (using first)'
            else:
                email, notes = '', 'No match'

            # 6) Write & print
            if WRITE_RESULTS:
                writer.writerow([name, email, notes])
            print(f"{name:30} → {email or notes}")

            # 7) Mark done & throttle
            processed.add(name)
            time.sleep(1)

        except InvalidSessionIdException:
            print(f"🚨 Browser session ended while processing '{name}'. Stopping early.")
            break

driver.quit()
print("✅ All done! Check", OUTPUT_FILE)