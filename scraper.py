"""
Google Maps Scraper - Finds businesses without websites
"""
import time
import re
import os
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class GoogleMapsScraper:
    def __init__(self, headless=False):  # Set to False for now to avoid Google Maps detection issues
        self.driver = None
        self.businesses = []
        self.headless = headless
        
    def setup_driver(self):
        """Initialize Chrome driver"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless=new')  # Use new headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')  # Set window size
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Fix for macOS chromedriver path issue
        try:
            driver_path = ChromeDriverManager().install()
            
            # webdriver-manager sometimes returns wrong file (like THIRD_PARTY_NOTICES.chromedriver)
            # Check if the returned path is actually the chromedriver executable
            if not os.path.exists(driver_path) or 'THIRD_PARTY' in driver_path:
                # Find the actual chromedriver executable
                driver_dir = os.path.dirname(driver_path)
                
                # Search for the actual chromedriver file (not THIRD_PARTY_NOTICES)
                if os.path.exists(driver_dir):
                    # First, check the directory itself
                    for file in os.listdir(driver_dir):
                        file_path = os.path.join(driver_dir, file)
                        # Look for file named exactly 'chromedriver' (not THIRD_PARTY_NOTICES.chromedriver)
                        if file == 'chromedriver' and os.path.isfile(file_path) and 'THIRD_PARTY' not in file_path:
                            driver_path = file_path
                            break
                    
                    # If not found, search in subdirectories (common on macOS)
                    if 'THIRD_PARTY' in driver_path or not os.path.exists(driver_path):
                        for root, dirs, files in os.walk(driver_dir):
                            for file in files:
                                if file == 'chromedriver' and 'THIRD_PARTY' not in file:
                                    potential_path = os.path.join(root, file)
                                    if os.path.isfile(potential_path):
                                        driver_path = potential_path
                                        break
                            if os.path.exists(driver_path) and 'THIRD_PARTY' not in driver_path:
                                break
            
            # Make chromedriver executable if it's not (common issue on macOS)
            if os.path.exists(driver_path) and 'THIRD_PARTY' not in driver_path:
                if not os.access(driver_path, os.X_OK):
                    os.chmod(driver_path, 0o755)  # Make it executable
            
            # Verify we have a valid executable
            if not os.path.exists(driver_path) or not os.access(driver_path, os.X_OK) or 'THIRD_PARTY' in driver_path:
                raise Exception(f"Could not find valid chromedriver executable. Path was: {driver_path}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("\nTrying alternative method (let Selenium auto-detect chromedriver)...")
            # Fallback: try without specifying path (let Selenium find it)
            try:
                self.driver = webdriver.Chrome(options=options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e2:
                print(f"Failed to start Chrome driver: {e2}")
                print("\n💡 Solutions:")
                print("1. Make sure Chrome browser is installed")
                print("2. Install chromedriver manually: brew install chromedriver")
                print("3. Or download from: https://chromedriver.chromium.org/")
                raise
        
    def search_businesses(self, city, business_type, max_results=50):
        """
        Search for businesses on Google Maps
        
        Args:
            city: City name (e.g., "Boston")
            business_type: Type of business (e.g., "garage")
            max_results: Maximum number of businesses to scrape
        """
        if not self.driver:
            self.setup_driver()
            
        query = f"{business_type} in {city}"
        print(f"Searching for: {query}")
        
        # Navigate to Google Maps
        self.driver.get("https://www.google.com/maps")
        time.sleep(2)
        
        # Find search box and enter query
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
        except TimeoutException:
            print("Failed to find search box")
            return []
        
        # Wait for results to load - try multiple selectors
        time.sleep(5)  # Give more time for page to load
        
        # Wait for business results to appear before trying to scroll
        print("Waiting for results to load...")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article'], a[href*='/maps/place/']"))
            )
            print("Results loaded!")
        except TimeoutException:
            print("Warning: Results may not have loaded yet, continuing anyway...")
        
        # Find the results panel with multiple fallback selectors
        results_panel = None
        panel_selectors = [
            "div[role='main']",
            "div[aria-label*='Results']",
            "div[aria-label*='results']",
            "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",  # Common Google Maps results container
            "div[jsaction*='mouseover']",
            "div.m6QErb",  # Another common selector
        ]
        
        for selector in panel_selectors:
            try:
                results_panel = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Found results panel using selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not results_panel:
            # If we can't find the panel, try scrolling the window directly
            print("Could not find results panel, trying alternative scrolling method...")
            businesses_found = self._scroll_and_collect_businesses_alternative(max_results)
        else:
            businesses_found = set()
            scroll_pause_time = 2
            
            # Scroll the results panel
            try:
                last_height = self.driver.execute_script("return arguments[0].scrollHeight", results_panel)
                
                while len(businesses_found) < max_results:
                    # Scroll down within the results panel
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight", results_panel
                    )
                    time.sleep(scroll_pause_time)
                    
                    # Also try clicking on result items to expand them (sometimes needed)
                    try:
                        articles = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                        if articles and len(articles) > 0:
                            # Click on the first few articles to make sure they're expanded
                            for i, article in enumerate(articles[:3]):
                                try:
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", article)
                                    time.sleep(0.5)
                                except:
                                    pass
                    except:
                        pass
                    
                    # SIMPLER APPROACH: Check each business card in the list for website button
                    # This matches what you see visually - if there's a "Site Web" button, they have a website
                    articles = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    
                    for article in articles:
                        try:
                            # Get business name
                            name = ""
                            name_selectors = [
                                "div.fontHeadlineSmall", 
                                "div.qBF1Pd", 
                                "div.d4r55", 
                                "div[aria-label]",
                                "div[jslog*='place']",
                            ]
                            for ns in name_selectors:
                                try:
                                    name_elem = article.find_element(By.CSS_SELECTOR, ns)
                                    name_text = name_elem.text.strip()
                                    if name_text and name_text.lower() not in ['résultats', 'results', '']:
                                        name = name_text
                                        break
                                except:
                                    continue
                            
                            # Get business URL
                            place_url = ""
                            try:
                                link = article.find_element(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                                place_url = link.get_attribute("href")
                                if place_url and '/place/' in place_url:
                                    place_part = place_url.split('/place/')[1].split('/')[0].split('?')[0]
                                    place_url = f"https://www.google.com/maps/place/{place_part}"
                            except:
                                continue
                            
                            if not place_url:
                                continue
                            
                            # KEY CHECK: Look for "Site Web" button/icon in this article
                            # DEBUG: Let's see what buttons/links actually exist in this article
                            has_website_button = False
                            
                            # DEBUG: Print all buttons and links to see what's actually there
                            try:
                                all_buttons = article.find_elements(By.CSS_SELECTOR, "button, a")
                                print(f"\nDEBUG for {name}:")
                                print(f"  Found {len(all_buttons)} buttons/links in this article")
                                for btn in all_buttons:
                                    aria_label = btn.get_attribute("aria-label") or ""
                                    btn_text = btn.text or ""
                                    href = btn.get_attribute("href") or ""
                                    data_value = btn.get_attribute("data-value") or ""
                                    print(f"    - aria-label: '{aria_label}'")
                                    print(f"    - text: '{btn_text}'")
                                    print(f"    - href: '{href[:60] if href else 'None'}'")
                                    print(f"    - data-value: '{data_value[:60] if data_value else 'None'}'")
                                    print()
                                
                                # Now check for website button based on what we actually see
                                for btn in all_buttons:
                                    aria_label = btn.get_attribute("aria-label") or ""
                                    btn_text = btn.text.lower() or ""
                                    href = btn.get_attribute("href") or ""
                                    
                                    # Check for website indicators
                                    if any(indicator in aria_label.lower() for indicator in ['website', 'site web', 'siteweb']) or \
                                       any(indicator in btn_text for indicator in ['website', 'site web']):
                                        # Make sure it's not directions
                                        if 'direction' not in aria_label.lower() and 'itinéraire' not in aria_label.lower():
                                            has_website_button = True
                                            print(f"  ✅ FOUND WEBSITE BUTTON: {aria_label or btn_text}")
                                            break
                                    
                                    # Also check if href exists and is not Google Maps
                                    if href and href.startswith('http') and 'google.com/maps' not in href.lower():
                                        # Only count it if it has website-related aria-label
                                        if 'website' in aria_label.lower() or 'site web' in aria_label.lower():
                                            has_website_button = True
                                            print(f"  ✅ FOUND WEBSITE LINK: {href}")
                                            break
                            except Exception as e:
                                print(f"DEBUG: Error checking buttons: {e}")
                            
                            # Only add businesses WITHOUT website button
                            if not has_website_button:
                                if place_url not in businesses_found:
                                    businesses_found.add(place_url)
                                    print(f"✅ Found business WITHOUT website: {name or 'Unknown'} - {place_url[:60]}...")
                            else:
                                print(f"⏭️  Skipping (has website): {name or 'Unknown'}")
                                
                        except Exception as e:
                            print(f"DEBUG: Error processing article: {e}")
                            continue
                    
                    print(f"Total unique businesses WITHOUT websites found so far: {len(businesses_found)}")
                    
                    # Check if we've reached the end
                    new_height = self.driver.execute_script("return arguments[0].scrollHeight", results_panel)
                    if new_height == last_height:
                        print("Reached end of results")
                        break
                    last_height = new_height
                    
                    if len(businesses_found) >= max_results:
                        break
            except Exception as e:
                print(f"Error scrolling results panel: {e}")
                print("Trying alternative method...")
                businesses_found = self._scroll_and_collect_businesses_alternative(max_results)
        
        print(f"Found {len(businesses_found)} businesses WITHOUT websites, extracting details...")
        
        # Extract business details - only for businesses we know don't have websites
        businesses = []
        count = 0
        
        for place_url in list(businesses_found)[:max_results]:
            if count >= max_results:
                break
                
            # Quick extraction - we already know they don't have websites
            business_info = self.extract_business_info_simple(place_url)
            if business_info:
                businesses.append(business_info)
                count += 1
                time.sleep(0.5)  # Faster since we're just getting basic info
        
        self.businesses = businesses
        return businesses
    
    def _scroll_and_collect_businesses_alternative(self, max_results):
        """Alternative method to scroll and collect businesses when main panel selector fails"""
        businesses_found = set()
        scroll_pause_time = 2
        scroll_attempts = 0
        max_scroll_attempts = 20  # Limit scrolling attempts
        
        print("Using alternative scrolling method (scrolling window)...")
        
        while len(businesses_found) < max_results and scroll_attempts < max_scroll_attempts:
            # Scroll the window
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # Also try scrolling the results list if it exists
            try:
                # Try to find and scroll any scrollable div
                scrollable_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[style*='overflow']")
                for div in scrollable_divs:
                    try:
                        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", div)
                    except:
                        pass
            except:
                pass
            
            # Use same simple approach - check for website button in list view
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            previous_count = len(businesses_found)
            for article in articles:
                try:
                    # Get business name
                    name = ""
                    name_selectors = ["div.fontHeadlineSmall", "div.qBF1Pd", "div.d4r55"]
                    for ns in name_selectors:
                        try:
                            name_elem = article.find_element(By.CSS_SELECTOR, ns)
                            name = name_elem.text.strip()
                            if name:
                                break
                        except:
                            continue
                    
                    # Get business URL
                    place_url = ""
                    try:
                        link = article.find_element(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                        place_url = link.get_attribute("href")
                        if place_url and '/place/' in place_url:
                            place_part = place_url.split('/place/')[1].split('/')[0].split('?')[0]
                            place_url = f"https://www.google.com/maps/place/{place_part}"
                    except:
                        continue
                    
                    if not place_url:
                        continue
                    
                    # Check for website button
                    has_website_button = False
                    try:
                        website_btn = article.find_element(By.CSS_SELECTOR, "button[aria-label*='Site Web'], button[aria-label*='Website'], a[aria-label*='Site Web'], a[aria-label*='Website']")
                        has_website_button = True
                    except:
                        pass
                    
                    # Only add if NO website button
                    if not has_website_button:
                        if place_url not in businesses_found:
                            businesses_found.add(place_url)
                            print(f"Found business WITHOUT website: {name or 'Unknown'} - {place_url[:60]}...")
                except:
                    continue
            
            scroll_attempts += 1
            
            # If we didn't find new businesses, we might have reached the end
            if len(businesses_found) == previous_count:
                # Try a few more times in case page is still loading
                if scroll_attempts > 5:
                    print(f"Stopped finding new businesses after {scroll_attempts} scrolls")
                    break
        
        return businesses_found
    
    def extract_business_info_simple(self, place_url):
        """Simple extraction - just get name, address, phone. We already know they don't have websites."""
        try:
            self.driver.get(place_url)
            time.sleep(2)  # Faster - just get basic info
            
            business_info = {
                'name': '',
                'address': '',
                'phone': '',
                'website': '',  # Empty - we know they don't have one
                'rating': '',
                'reviews_count': '',
                'google_maps_url': place_url
            }
            
            # Extract name
            name_selectors = [
                "h1[data-attrid='title']",
                "h1.DUwDvf",
                "h1.fontHeadlineLarge",
                "h1",
            ]
            
            for selector in name_selectors:
                try:
                    name_element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    name_text = name_element.text.strip()
                    if name_text and name_text.lower() not in ['résultats', 'results', 'search', '']:
                        business_info['name'] = name_text
                        break
                except:
                    continue
            
            # Extract address
            try:
                address_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id='address']"
                )
                business_info['address'] = address_button.find_element(By.CSS_SELECTOR, "[data-value]").get_attribute("data-value")
            except:
                try:
                    address_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, "button[data-item-id='address'] span"
                    )
                    if address_elements:
                        business_info['address'] = address_elements[0].text.strip()
                except:
                    pass
            
            # Extract phone
            try:
                phone_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id*='phone']"
                )
                phone_text = phone_button.find_element(By.CSS_SELECTOR, "[data-value]").get_attribute("data-value")
                business_info['phone'] = phone_text
            except:
                try:
                    phone_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, "button[data-item-id*='phone'] span"
                    )
                    if phone_elements:
                        business_info['phone'] = phone_elements[0].text.strip()
                except:
                    pass
            
            if business_info['name']:
                return business_info
            return None
                
        except Exception as e:
            print(f"Error extracting business info: {str(e)}")
            return None
    
    def extract_business_info(self, place_url, return_all=False):
        """Extract business information from a Google Maps place URL
        
        Args:
            place_url: URL of the Google Maps place
            return_all: If True, return all businesses (even with websites). If False, only return businesses without websites.
        """
        try:
            self.driver.get(place_url)
            # Wait longer for page to fully load
            time.sleep(4)
            
            business_info = {
                'name': '',
                'address': '',
                'phone': '',
                'website': '',
                'rating': '',
                'reviews_count': '',
                'google_maps_url': place_url
            }
            
            # Extract name - try multiple selectors and wait for page to load
            name_selectors = [
                "h1[data-attrid='title']",
                "h1.DUwDvf",
                "h1.fontHeadlineLarge",
                "h1.qrShPb",
                "h1.x3AX1-LfntMc-header-title-title",
                "h1",
            ]
            
            for selector in name_selectors:
                try:
                    name_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    name_text = name_element.text.strip()
                    # Skip if it's "Results" or other generic text
                    if name_text and name_text.lower() not in ['résultats', 'results', 'search', '']:
                        business_info['name'] = name_text
                        break
                except:
                    continue
            
            # If still no name, try getting from URL
            if not business_info['name']:
                try:
                    # Extract name from URL if possible
                    if '/place/' in place_url:
                        name_from_url = place_url.split('/place/')[1].split('/')[0].replace('+', ' ')
                        if name_from_url and name_from_url.lower() not in ['résultats', 'results']:
                            business_info['name'] = name_from_url
                except:
                    pass
            
            print(f"DEBUG: Extracted name: '{business_info['name']}'")
            
            # Extract address
            try:
                address_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id='address']"
                )
                business_info['address'] = address_button.find_element(By.CSS_SELECTOR, "[data-value]").get_attribute("data-value")
            except:
                try:
                    address_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, "button[data-item-id='address'] span"
                    )
                    if address_elements:
                        business_info['address'] = address_elements[0].text.strip()
                except:
                    pass
            
            # Extract phone
            try:
                phone_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id*='phone']"
                )
                phone_text = phone_button.find_element(By.CSS_SELECTOR, "[data-value]").get_attribute("data-value")
                business_info['phone'] = phone_text
            except:
                try:
                    phone_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, "button[data-item-id*='phone'] span"
                    )
                    if phone_elements:
                        business_info['phone'] = phone_elements[0].text.strip()
                except:
                    pass
            
            # Extract website - ONLY look in the specific business info panel
            # We must be very careful to only get links from THIS business, not ads or related businesses
            website_found = False
            website_url = None
            
            # Wait for the business info panel to load
            time.sleep(3)
            
            # DEBUG: First, let's see what info panels exist
            print("\nDEBUG: Looking for info panel...")
            try:
                # First, find the business info panel
                info_panel = None
                panel_selectors = [
                    "div[role='complementary']",
                    "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",
                    "div.m6QErb",
                    "div[jsaction*='pane']",
                ]
                
                for panel_selector in panel_selectors:
                    try:
                        panels = self.driver.find_elements(By.CSS_SELECTOR, panel_selector)
                        print(f"  Found {len(panels)} elements with selector: {panel_selector}")
                        if panels:
                            # CRITICAL FIX: Find the panel that contains THIS business name
                            # This prevents getting ads or related businesses' info
                            business_name_lower = business_info['name'].lower()
                            for panel in panels:
                                panel_text = panel.text.lower()
                                # Check if this panel contains the business name
                                if business_name_lower in panel_text or any(word in panel_text for word in business_name_lower.split()[:2]):
                                    info_panel = panel
                                    print(f"  ✅ Using info panel that matches '{business_info['name']}'")
                                    break
                            
                            # If we didn't find a matching panel, try the first one
                            if not info_panel and panels:
                                info_panel = panels[0]
                                print(f"  ⚠️  Using first panel (could be wrong): {panel_selector}")
                            break
                    except Exception as e:
                        print(f"  Error with {panel_selector}: {e}")
                        continue
                
                if info_panel:
                    # DEBUG: Print ALL links and buttons in the info panel
                    print("\nDEBUG: All links and buttons in info panel:")
                    all_elements = info_panel.find_elements(By.CSS_SELECTOR, "a, button, div[data-value], span")
                    for i, elem in enumerate(all_elements[:20]):  # Limit to first 20 to avoid spam
                        try:
                            aria_label = elem.get_attribute("aria-label") or ""
                            text = elem.text or ""
                            href = elem.get_attribute("href") or ""
                            data_value = elem.get_attribute("data-value") or ""
                            data_item_id = elem.get_attribute("data-item-id") or ""
                            tag = elem.tag_name
                            
                            if href or data_value or 'website' in aria_label.lower() or 'site web' in aria_label.lower() or 'website' in text.lower():
                                print(f"  [{i}] <{tag}>")
                                print(f"      aria-label: '{aria_label}'")
                                print(f"      text: '{text[:50]}'")
                                print(f"      href: '{href[:60]}'")
                                print(f"      data-value: '{data_value[:60]}'")
                                print(f"      data-item-id: '{data_item_id}'")
                                print()
                        except:
                            pass
                    
                    # Method 1: Look for the specific "authority" link
                    try:
                        website_button = info_panel.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                        website_url = website_button.get_attribute("href")
                        aria_label = website_button.get_attribute("aria-label") or ""
                        
                        if website_url and website_url.startswith('http'):
                            href_lower = website_url.lower()
                            # Skip social media and Google Maps
                            if not any(skip in href_lower for skip in ['facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'google.com/maps', 'maps.google.com']):
                                # Verify it belongs to THIS business
                                business_name_lower = business_info['name'].lower()
                                clean_business_name = business_name_lower.replace('%7c', '').replace('|', '').replace('&', '').replace('%26', '')
                                aria_label_lower = aria_label.lower()
                                
                                business_words = [w for w in clean_business_name.split() if len(w) > 2]
                                matching_words = [word for word in business_words if word in aria_label_lower]
                                
                                # Must match the FIRST distinctive word (the business name)
                                first_word = business_words[0] if business_words else ""
                                first_word_match = first_word in aria_label_lower and len(first_word) > 4
                                two_words_match = len(matching_words) >= 2 and first_word in matching_words
                                
                                if first_word_match or two_words_match:
                                    website_found = True
                                    print(f"DEBUG: ✅ Found website via authority link: {website_url} (aria-label: '{aria_label}')")
                                else:
                                    print(f"DEBUG: ⚠️  Authority link doesn't match business: {website_url} (aria-label: '{aria_label}', first_word: '{first_word}')")
                    except Exception as e:
                        print(f"DEBUG: No authority link found: {e}")
                    
                    # Method 2: Look for links with "Website" or "Site Web" in aria-label or text
                    # CRITICAL: Verify the website belongs to THIS business, not another one
                    if not website_found:
                        try:
                            business_name_lower = business_info['name'].lower()
                            all_links = info_panel.find_elements(By.CSS_SELECTOR, "a, button")
                            for link in all_links:
                                aria_label = link.get_attribute("aria-label") or ""
                                link_text = link.text.lower() or ""
                                href = link.get_attribute("href") or ""
                                
                                # Check if it mentions website
                                if ('website' in aria_label.lower() or 'site web' in aria_label.lower() or 
                                    'website' in link_text) and href.startswith('http'):
                                    if 'google.com/maps' not in href.lower():
                                        # CRITICAL CHECK: Verify this website belongs to THIS business
                                        # The aria-label MUST contain THIS business name exactly
                                        aria_label_lower = aria_label.lower()
                                        
                                        # Skip Instagram/Facebook - those are social media, not websites
                                        if 'instagram.com' in href.lower() or 'facebook.com' in href.lower():
                                            print(f"DEBUG: ⚠️  Skipping social media link: {href}")
                                            continue
                                        
                                        # Clean business name for matching (remove special chars, %7C etc)
                                        clean_business_name = business_name_lower.replace('%7c', '').replace('|', '').replace('&', '').replace('%26', '')
                                        business_words = [w for w in clean_business_name.split() if len(w) > 2]  # Words longer than 2 chars
                                        
                                        # Check if aria-label contains THIS business name
                                        # Must match the DISTINCTIVE word(s) from the business name
                                        matching_words = [word for word in business_words if word in aria_label_lower]
                                        
                                        # Get the first distinctive word (usually the business name)
                                        first_word = business_words[0] if business_words else ""
                                        
                                        # For a match, we need:
                                        # 1. The FIRST word (if it's distinctive > 4 chars) OR
                                        # 2. At least 2 words including the first word
                                        first_word_match = first_word in aria_label_lower and len(first_word) > 4
                                        two_words_match = len(matching_words) >= 2 and first_word in matching_words
                                        
                                        # Also check if it mentions OTHER businesses (bad!)
                                        other_business_keywords = ['bikini garage', 'angel garage', 'our garage', 'gourmet garage', 'bp garage', 'sewa mobil', 'monkey garage', 'brodking']
                                        mentions_other = any(other in aria_label_lower for other in other_business_keywords)
                                        
                                        # If it mentions another business, check if it ALSO mentions this business
                                        if mentions_other:
                                            # Extract the OTHER business name from aria-label
                                            other_business_in_label = [other for other in other_business_keywords if other in aria_label_lower]
                                            # Check if THIS business name is ALSO in the label
                                            this_business_in_label = first_word in aria_label_lower if len(first_word) > 4 else False
                                            
                                            if not this_business_in_label:
                                                print(f"DEBUG: ⚠️  Skipping - mentions different business: {href} (aria-label: '{aria_label}', other: {other_business_in_label})")
                                                continue
                                        
                                        if first_word_match or two_words_match:
                                            website_url = href
                                            website_found = True
                                            print(f"DEBUG: ✅ Found website for THIS business: {href} (aria-label: '{aria_label}')")
                                            break
                                        else:
                                            print(f"DEBUG: ⚠️  Skipping - doesn't match business name: {href} (aria-label: '{aria_label}', business: '{business_info['name']}', first_word: '{first_word}')")
                        except Exception as e:
                            print(f"DEBUG: Error in Method 2: {e}")
                    
                    # Method 3: Look for text that says "Website:" or "Site Web:" followed by a URL
                    if not website_found:
                        try:
                            panel_text = info_panel.text
                            # Look for patterns like "Website: bikinigaragebali.com" or "Site Web: http://..."
                            import re
                            website_patterns = [
                                r'[Ww]ebsite[:\s]+([^\s]+)',
                                r'[Ss]ite [Ww]eb[:\s]+([^\s]+)',
                                r'([a-zA-Z0-9-]+\.com)',
                                r'(https?://[^\s]+)',
                            ]
                            for pattern in website_patterns:
                                matches = re.findall(pattern, panel_text)
                                for match in matches:
                                    if isinstance(match, tuple):
                                        match = match[0] if match else ""
                                    if match and 'google.com' not in match.lower() and 'maps' not in match.lower():
                                        if match.startswith('http'):
                                            website_url = match
                                        else:
                                            website_url = f"https://{match}"
                                        website_found = True
                                        print(f"DEBUG: ✅ Found website via text pattern: {website_url}")
                                        break
                                if website_found:
                                    break
                        except Exception as e:
                            print(f"DEBUG: Error in Method 3: {e}")
                else:
                    print("DEBUG: ❌ Could not find info panel!")
                
            except Exception as e:
                print(f"DEBUG: Error finding info panel: {e}")
                import traceback
                traceback.print_exc()
            
            print(f"\nDEBUG: Final result - Website found: {website_found}, URL: {website_url}")
            
            business_info['website'] = website_url if website_found else ''
            
            # Extract rating
            try:
                rating_element = self.driver.find_element(
                    By.CSS_SELECTOR, "div[data-value]"
                )
                rating_text = rating_element.get_attribute("data-value")
                if rating_text:
                    business_info['rating'] = rating_text
            except:
                pass
            
            # Extract reviews count
            try:
                reviews_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "span[aria-label*='reviews']"
                )
                if reviews_elements:
                    reviews_text = reviews_elements[0].get_attribute("aria-label")
                    numbers = re.findall(r'\d+', reviews_text)
                    if numbers:
                        business_info['reviews_count'] = numbers[0]
            except:
                pass
            
            # Only return businesses without websites (unless return_all=True)
            if return_all and business_info['name']:
                print(f"Found business: {business_info['name']} - Website: {'Yes' if website_found else 'No'}")
                return business_info
            elif not website_found and business_info['name']:
                print(f"Found business without website: {business_info['name']}")
                return business_info
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting business info: {str(e)}")
            return None
    
    def filter_businesses_without_websites(self):
        """Filter businesses that don't have websites"""
        return [b for b in self.businesses if not b.get('website') or b.get('website') == '']
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

