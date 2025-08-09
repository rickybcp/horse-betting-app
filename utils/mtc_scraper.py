"""
MTC Jockey Club scraper module for horse racing data
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re


def scrape_mtc_next_race_day(desired_month_text: str | None = None):
    """Scrape next race day card from MTC Jockey Club fixtures page.
    Attempts to:
      1) Open fixtures page
      2) Optionally select the desired month tab/button if provided
      3) Click the first visible "View Race Card" link
      4) On the race card page, iterate races tabs and extract race name/time and runners
    Returns the races list in our standard schema.
    """
    fixtures_url = 'https://www.mtcjockeyclub.com/form-guide/fixtures'

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = None
    races_data = []

    def safe_text(el):
        try:
            return el.text.strip()
        except Exception:
            return ''

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(fixtures_url)

        wait = WebDriverWait(driver, 20)
        # Wait for any content to be present
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body *')))

        # If a month is specified, try to click it
        if desired_month_text:
            try:
                month_buttons = driver.find_elements(By.XPATH, f"//button[contains(., '{desired_month_text}') or contains(., '{desired_month_text[:3]}')]|//a[contains(., '{desired_month_text}') or contains(., '{desired_month_text[:3]}')]")
                for btn in month_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        time.sleep(1)
                        break
            except Exception:
                pass

        # Find and click the first visible "View Race Card" (or similar) link
        racecard_links = driver.find_elements(By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'view race card') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'race card')]")
        clicked = False
        for link in racecard_links:
            try:
                if link.is_displayed() and link.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    link.click()
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            # If no direct link found, try to locate buttons
            buttons = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'view race card') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'race card')]")
            for btn in buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        btn.click()
                        clicked = True
                        break
                except Exception:
                    continue

        if not clicked:
            print("Could not find a 'View Race Card' link/button. Returning empty result.")
            return []

        # We should now be on the race card page; wait for tabbed races or content
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body *')))

        # Try to collect race tabs/buttons
        race_tabs = driver.find_elements(By.XPATH, "//a[contains(@class,'nav-link') and (contains(., 'Race') or contains(., 'R') or contains(., 'Course'))] | //button[contains(@class,'nav-link') and (contains(., 'Race') or contains(., 'R'))]")
        if not race_tabs:
            # Fallback: look for elements that look like race selectors
            race_tabs = driver.find_elements(By.XPATH, "//a[contains(., 'Race') or contains(., 'R1') or contains(., 'R2')] | //button[contains(., 'Race') or contains(., 'R1') or contains(., 'R2')]")

        # If still nothing, try to treat the current page as a single race card (no tabs)
        if not race_tabs:
            race_tabs = []

        def parse_current_race_panel() -> dict | None:
            """Parse current visible race panel into our schema."""
            # Race header/name
            race_name = ''
            race_time = ''

            # Try common header containers
            header_candidates = driver.find_elements(By.XPATH, "//h1|//h2|//h3|//div[contains(@class,'race')][contains(@class,'title')]|//div[contains(@class,'race')][contains(@class,'header')]")
            for hc in header_candidates:
                txt = safe_text(hc)
                if txt and ('Race' in txt or 'R' in txt or ':' in txt):
                    race_name = txt
                    # Extract time like 12:45
                    m = re.search(r"(\d{1,2}:\d{2})", txt)
                    if m:
                        race_time = m.group(1)
                    break

            # If time still empty, search elsewhere
            if not race_time:
                try:
                    time_el = driver.find_element(By.XPATH, "//*[contains(text(),':') and string-length(normalize-space())<=10]")
                    race_time = safe_text(time_el)
                except Exception:
                    race_time = ''

            # Horses list
            horses = []
            # Try several candidate containers commonly used for runners
            runner_containers = driver.find_elements(By.XPATH, "//div[contains(@class,'runner') or contains(@class,'entry') or contains(@class,'horse') or contains(@class,'card') or contains(@class,'row')]//div[.//text()]")
            if not runner_containers:
                # Fallback to list items/rows
                runner_containers = driver.find_elements(By.XPATH, "//li[contains(@class,'runner') or contains(@class,'entry')] | //tr[contains(@class,'runner') or contains(@class,'entry')] | //div[contains(@class,'runner')]")

            # Limit to a reasonable number to avoid grabbing layout grids
            candidates = runner_containers[:50]
            for idx, rc in enumerate(candidates, start=1):
                txt = safe_text(rc)
                if not txt:
                    continue
                # Heuristic: require some alphabetic content to avoid empty grid cols
                if not re.search(r"[A-Za-z]", txt):
                    continue
                # Extract horse number if present like "1" or "No. 1"
                num_match = re.search(r"(?:No\.?\s*)?(\d{1,2})\b", txt)
                horse_number = int(num_match.group(1)) if num_match else idx
                # Extract a name-like token: longest word sequence
                # This is heuristic; the site may have a dedicated name element
                name_match = None
                try:
                    # Prefer child element that looks like a name
                    name_el = rc.find_element(By.XPATH, ".//*[contains(@class,'name') or contains(@class,'horse')][1]")
                    name_match = safe_text(name_el)
                except Exception:
                    pass
                horse_name = name_match if name_match else (re.search(r"([A-Z][A-Z'\- ]{2,})", txt) or [None])
                if isinstance(horse_name, list):
                    horse_name = horse_name[0]
                if not horse_name:
                    # Fallback to first 4 words as name
                    horse_name = " ".join(txt.split()[:4])

                horses.append({
                    "number": horse_number,
                    "name": horse_name.strip(),
                    # Odds may not be available in fixture; skip or set None
                    "odds": None,
                    # Default points to 1 if odds unknown
                    "points": 1
                })

            if not race_name:
                # Provide a generic name
                race_name = f"Race {len(races_data) + 1}"

            return {
                "id": f"mtc_{len(races_data)+1}_{datetime.now().strftime('%Y%m%d')}",
                "name": race_name,
                "time": race_time or datetime.now().strftime('%H:%M'),
                "horses": horses,
                "winner": None,
                "status": 'upcoming'
            }

        if race_tabs:
            for tab in race_tabs[:12]:  # reasonable upper bound
                try:
                    if tab.is_displayed() and tab.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
                        tab.click()
                        time.sleep(0.8)
                        race_data = parse_current_race_panel()
                        if race_data:
                            races_data.append(race_data)
                except Exception as e:
                    print(f"Tab parse error: {e}")
                    continue
        else:
            # Single race card fallback
            race_data = parse_current_race_panel()
            if race_data:
                races_data.append(race_data)

    except Exception as e:
        print(f"Error during MTC scraping: {e}")
        races_data = []
    finally:
        if driver:
            driver.quit()

    return races_data
