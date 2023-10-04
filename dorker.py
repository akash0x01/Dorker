from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageDraw, ImageFont
import sys
import time
import os
from urllib.parse import quote_plus
import urllib3
import re

# Disable SSL related warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def sanitize_filename(filename):
    return re.sub(r'[^\w\d_]', '_', filename)

def add_black_border(image, border_height=50):
    width, height = image.size
    new_height = height + border_height
    new_image = Image.new("RGB", (width, new_height), "black")
    new_image.paste(image, (0, border_height))
    return new_image

def take_screenshot(driver, url, sub_url, file_name, folder_name):
    full_url = f"{url}{sub_url}"
    driver.get(full_url)
    driver.execute_script("document.body.style.zoom='150%'")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print(f"An error occurred while waiting for the page {full_url} to load: {e}")

    screenshot_name = os.path.join(folder_name, sanitize_filename(file_name) + '.png')
    driver.save_screenshot(screenshot_name)

    screenshot = Image.open(screenshot_name)
    screenshot_with_border = add_black_border(screenshot)

    draw = ImageDraw.Draw(screenshot_with_border)
    font = ImageFont.truetype("MartianMono-SemiBold.ttf", 14)
    draw.text((10, 10), f"URL: {full_url}", font=font, fill="red")

    screenshot_with_border.save(screenshot_name, dpi=(1000, 1000))
    print(f"Screenshot saved for {sub_url}")

def search_engine_dorking(driver, query, search_engine, folder_name):
    search_urls = {
        'google': f'https://www.google.com/search?q={query}',
        'bing': f'https://www.bing.com/search?q={query}',
        'yahoo': f'https://search.yahoo.com/search?p={query}'
    }

    if search_engine not in search_urls:
        print(f"Search engine {search_engine} not supported.")
        return

    full_url = search_urls[search_engine]
    take_screenshot(driver, '', full_url, f"{search_engine}_{query}", folder_name)

def main(url):
    url = url.rstrip('/')

    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)

    timestamp = str(int(time.time()))
    folder_name = f"{timestamp}_screenshots"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    dork_queries = [
        f'site:{url} filetype:txt',
        f'site:{url} filetype:pdf',
        f'site:{url} inurl:admin'
    ]

    search_engines = ['google', 'bing', 'yahoo']

    for search_engine in search_engines:
        for query in dork_queries:
            encoded_query = quote_plus(query)
            search_engine_dorking(driver, encoded_query, search_engine, folder_name)

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <website_url>")
    else:
        main(sys.argv[1])
