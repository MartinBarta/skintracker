import json
import cloudscraper
from bs4 import BeautifulSoup
import time
import random

json_path = "/var/www/html/skintracker/skins.json"
scraper = cloudscraper.create_scraper()

with open(json_path, "r") as f:
    skins = json.load(f)

for skin in skins:
    try:
        print(f"Updating: {skin['name']}")
        response = scraper.get(skin["url"], timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract price by condition
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

        # Extract image URL (adjust selector if necessary)
        # From inspection, main skin image is inside div.relative > img
        img_tag = soup.select_one("div.relative > img")
        if img_tag and img_tag.has_attr("src"):
            skin_image_url = img_tag["src"]
            skin["image"] = skin_image_url
            print(f"→ Image URL found: {skin_image_url}")
        else:
            print("→ Image URL not found.")
            # Optionally clear old image if you want:
            # skin["image"] = ""

    except Exception as e:
        print(f"Error updating {skin['name']}: {e}")

    # Rate limiting delay
    time.sleep(random.uniform(1.5, 3))

with open(json_path, "w") as f:
    json.dump(skins, f, indent=2)

print("All skins updated successfully.")