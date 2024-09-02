import os
import time
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def is_internal_link(base_url, link):
    """Check if the link is internal (belongs to the same domain)."""
    base_netloc = urlparse(base_url).netloc
    link_netloc = urlparse(link).netloc
    return base_netloc == link_netloc or link_netloc == ""

def sanitize_filename(url):
    """Convert a URL into a safe filename."""
    return url.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_")

def take_screenshot(driver, url, output_folder):
    """Take a screenshot of the current page and save it."""
    filename = sanitize_filename(url) + ".png"
    filepath = os.path.join(output_folder, filename)
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {filepath}")

def crawl_website(driver, base_url, output_folder):
    """Crawl a website, visit all internal links, and take screenshots."""
    visited_urls = set()
    urls_to_visit = set([base_url])

    while urls_to_visit:
        url = urls_to_visit.pop()
        if url not in visited_urls:
            visited_urls.add(url)
            driver.get(url)
            print(f"Visited: {url}")
            time.sleep(2)  # Allow time for the page to load

            # Take a screenshot
            take_screenshot(driver, url, output_folder)

            try:
                # Scroll through the page to load dynamic content
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                # Find all links on the page
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and is_internal_link(base_url, href):
                            full_url = urljoin(base_url, href)
                            if full_url not in visited_urls and full_url not in urls_to_visit:
                                urls_to_visit.add(full_url)
                    except (StaleElementReferenceException, NoSuchElementException):
                        print(f"Stale or missing element encountered while processing {url}. Retrying...")

            except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
                print(f"Encountered an issue while processing {url}: {e}")

def main():
    # Set up the Chrome driver with options
    options = Options()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Define the output folder for screenshots
        output_folder = "website_screenshots"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Start crawling the website
        base_url = "https://neuralbytes.org"  # Replace with your target URL
        print("Starting web crawling...")
        crawl_website(driver, base_url, output_folder)
        print("Web crawling completed.")
        
    finally:
        driver.quit()
        print("Chrome browser closed.")

if __name__ == "__main__":
    main()
