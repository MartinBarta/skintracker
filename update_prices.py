import json
import cloudscraper
from bs4 import BeautifulSoup
import time
import random

json_path = "/var/www/html/skintracker/skins.json"

with open("/var/www/html/skintracker/proxies.txt") as f:
    proxy_list = [f"http://{line.strip()}" for line in f if line.strip()]


# Load skins
with open(json_path, "r") as f:
    skins = json.load(f)

# Proxy handling
proxy_index = 0
current_proxy = proxy_list[proxy_index]

def create_scraper_with_proxy(proxy):
    return cloudscraper.create_scraper(browser={
        'custom': 'ScraperBot'
    }, interpreter='nodejs', delay=10, proxy=proxy)

scraper = cloudscraper.create_scraper()  # create once outside loop

for skin in skins:
    success = False
    retries = 0
    while not success and retries < len(proxy_list):
        try:
            print(f"Updating: {skin['name']} using proxy {current_proxy}")
            response = scraper.get(
                skin["url"],
                timeout=20,
                proxies={"http": current_proxy, "https": current_proxy})
            if "cf-browser-verification" in response.text.lower():
                raise Exception("Cloudflare challenge page detected")

            soup = BeautifulSoup(response.text, 'html.parser')

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

            # Extract image
            img_tag = soup.select_one("div.relative > img")
            if img_tag and img_tag.has_attr("src"):
                skin_image_url = img_tag["src"]
                skin["image"] = skin_image_url
                print(f"→ Image URL found: {skin_image_url}")
            else:
                print("→ Image URL not found.")

            success = True  # mark success
        except Exception as e:
            print(f"Error updating {skin['name']} with proxy {current_proxy}: {e}")
            proxy_index = (proxy_index + 1) % len(proxy_list)
            current_proxy = proxy_list[proxy_index]
            scraper = create_scraper_with_proxy(current_proxy)
            retries += 1
            time.sleep(2)  # short wait before retry

    # Rate limiting delay
    time.sleep(random.uniform(1.5, 3))

# Save updated data
with open(json_path, "w") as f:
    json.dump(skins, f, indent=2)