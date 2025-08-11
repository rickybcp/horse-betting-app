"""
Results Scraper for Supertote Mauritius
Scrapes actual race results from completed races
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def scrape_race_results():
    """
    Scrape actual race results from Supertote Mauritius website
    Returns a dictionary of race results with race ID as key and winner horse name as value
    """
    results = {}
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize WebDriver with Windows-compatible setup
        try:
            # Try the standard approach first
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"⚠️ Standard WebDriver failed: {e}")
            try:
                # Try without service specification
                driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                print(f"⚠️ Alternative WebDriver failed: {e2}")
                # Try with explicit path
                import os
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                if os.path.exists(chrome_path):
                    chrome_options.binary_location = chrome_path
                    driver = webdriver.Chrome(options=chrome_options)
                else:
                    raise Exception("Chrome not found in expected location")
        
        try:
            # Navigate to Supertote Mauritius racing page
            print("🌐 Navigating to Supertote Mauritius racing page...")
            driver.get("https://supertote.mu/racing")
            
            # Wait for page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give additional time for dynamic content to load
            time.sleep(8)
            
            print("🔍 Looking for race results using XPath selectors...")
            
            # Find all race list items (ol/li elements)
            race_list_items = driver.find_elements(By.XPATH, "/html/body/div/ol/li")
            print(f"🔍 Found {len(race_list_items)} race list items")
            
            # Process each race list item
            for i, race_item in enumerate(race_list_items):
                try:
                    # Get race number from span[2] - extract last character
                    race_number_elem = race_item.find_element(By.XPATH, ".//div[1]/span[2]")
                    race_number_text = race_number_elem.text.strip()
                    race_number = race_number_text[-1] if race_number_text else ""
                    
                    if race_number and race_number.isdigit():
                        print(f"🏁 Found Race {race_number}")
                        
                        # Get winner horse number from first row, second column
                        winner_horse_number_elem = race_item.find_element(By.XPATH, ".//div[2]/table/tbody/tr[1]/td[2]")
                        winner_horse_number_text = winner_horse_number_elem.text.strip()
                        # Convert to integer for consistency with race data
                        winner_horse_number = int(winner_horse_number_text) if winner_horse_number_text.isdigit() else None
                        
                        # Get winner horse name from first row, third column
                        winner_horse_name_elem = race_item.find_element(By.XPATH, ".//div[2]/table/tbody/tr[1]/td[3]")
                        winner_horse_name = winner_horse_name_elem.text.strip()
                        
                        if winner_horse_name and winner_horse_number:
                            # Use numeric race ID to match existing race data
                            race_id = int(race_number)
                            results[race_id] = {
                                "winner_name": winner_horse_name,
                                "winner_number": winner_horse_number,  # This is now an integer
                                "race_number": race_number,
                                "raw_text": f"Race {race_number}: {winner_horse_name} (#{winner_horse_number})"
                            }
                            print(f"🏆 Race {race_number}: Winner is {winner_horse_name} (#{winner_horse_number})")
                        else:
                            print(f"⚠️ Race {race_number}: Missing horse name or number")
                    else:
                        print(f"⚠️ Skipping item {i+1}: Invalid race number '{race_number}'")
                        
                except NoSuchElementException as e:
                    print(f"⚠️ Race item {i+1}: Missing required elements - {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ Error processing race item {i+1}: {e}")
                    continue
            
            if not results:
                print("⚠️ No race results found")
                print("🔍 Debugging information:")
                print(f"📄 Page title: {driver.title}")
                print(f"📄 Page URL: {driver.current_url}")
                
                # Try to get some page content for debugging
                page_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"📄 Page text length: {len(page_text)} characters")
                print(f"📄 First 500 characters: {page_text[:500]}")
                
                # Look for any racing-related content
                if "race" in page_text.lower() or "horse" in page_text.lower():
                    print("✅ Found racing-related content in page text")
                else:
                    print("❌ No racing-related content found in page text")
                
        except TimeoutException:
            print("⏰ Timeout waiting for page to load")
            results = {}
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            results = {}
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Failed to initialize WebDriver: {e}")
        results = {}
    
    return results


def scrape_results_with_fallback():
    """
    Scrape results from Supertote Mauritius
    Returns a dictionary of race results
    """
    print("🚀 Starting race results scraping from Supertote Mauritius...")
    
    # Scrape real results
    real_results = scrape_race_results()
    
    if real_results:
        print(f"✅ Successfully scraped {len(real_results)} race results")
        return real_results
    else:
        print("⚠️ No results were scraped")
        return {}


if __name__ == "__main__":
    # Test the scraper
    results = scrape_results_with_fallback()
    print(f"\n📋 Final Results: {results}")
