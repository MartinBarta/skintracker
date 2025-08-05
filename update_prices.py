import json
import cloudscraper
from bs4 import BeautifulSoup
import time
import random

json_path = "/var/www/html/skintracker/skins.json"
scraper = cloudscraper.create_scraper()

# Load existing skins
with open(json_path, "r") as f:
    skins = json.load(f)

for skin in skins:
    try:
        print(f"Updating: {skin['name']}")
        response = scraper.get(skin["url"], timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Price extraction ---
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
                try:
                    skin["price"] = float(price_text)
                    price_found = True
                    print(f"→ Updated price for {condition}: ${skin['price']}")
                except ValueError:
                    print(f"→ Couldn't convert price text to float: '{price_text}'")
                break

        if not price_found:
            print(f"→ Price for condition '{skin['condition']}' not found on page: {skin['url']}")

        # --- Image extraction ---
        img_tag = soup.select_one("div.relative > img")
        if img_tag and img_tag.has_attr("src"):
            skin["image"] = img_tag["src"]
            print(f"→ Image URL found: {skin['image']}")
        else:
            print("→ Image URL not found.")

    except Exception as e:
        print(f"⚠️ Error updating {skin['name']}: {e}")

    # Delay to avoid rate limits
    time.sleep(random.uniform(1.5, 3))

# Save updated data
try:
    with open(json_path, "w") as f:
        json.dump(skins, f, indent=2)
    print("✅ Finished updating all skins.")
except PermissionError:
    print(f"❌ Permission denied while saving {json_path}. Try running with sudo or fixing file permissions.")