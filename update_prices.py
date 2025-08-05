import json
import time
import random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

json_path = "/var/www/html/skintracker/skins.json"

# Setup headless Chrome using undetected_chromedriver
options = uc.ChromeOptions()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)

# Load skins
with open(json_path, "r") as f:
    skins = json.load(f)

for skin in skins:
    try:
        print(f"Updating: {skin['name']}")
        driver.get(skin["url"])
        time.sleep(random.uniform(2, 4))  # Allow Cloudflare page to pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract price
        containers = soup.select("div.relative.flex.px-4.py-2.hover\\:bg-gray-700.transition-colors.bg-gray-700")
        price_found = False
        for container in containers:
            condition_span = container.select_one("div.grow.mr-2 > span.whitespace-nowrap")
            price_span = container.select_one("div.flex-none.text-right.flex.items-center > span.font-bold")
            if not condition_span or not price_span:
                continue
            condition = condition_span.text.strip()
            price_text = price_span.text.strip().replace("$", "")
            if condition == skin["condition"]:
                skin["price"] = float(price_text)
                price_found = True
                print(f"→ Updated price for {condition}: ${skin['price']}")
                break
        if not price_found:
            print(f"→ Price for condition '{skin['condition']}' not found.")

        # Extract image URL
        img_tag = soup.select_one("div.relative > img")
        if img_tag and img_tag.has_attr("src"):
            skin["image"] = img_tag["src"]
            print(f"→ Image URL found: {skin['image']}")
        else:
            print("→ Image URL not found.")

    except Exception as e:
        print(f"Error updating {skin['name']}: {e}")

    # Random delay to prevent detection
    time.sleep(random.uniform(1.5, 3))

# Save updated JSON
with open(json_path, "w") as f:
    json.dump(skins, f, indent=2)

driver.quit()