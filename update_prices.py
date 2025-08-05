import os
import json
import asyncio
import random
from pyppeteer import launch
from bs4 import BeautifulSoup

# Use system Chromium (adjust path if needed)
os.environ['PYPPETEER_EXECUTABLE_PATH'] = '/usr/bin/chromium-browser'

JSON_PATH = "/var/www/html/skintracker/skins.json"
DEBUG_SAVE_PATH = "/tmp/skintracker_debug"

# Create debug folder if not exists
os.makedirs(DEBUG_SAVE_PATH, exist_ok=True)

async def update_skins():
    with open(JSON_PATH, "r") as f:
        skins = json.load(f)

    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()

    for skin in skins:
        print(f"Updating: {skin['name']}")
        try:
            # Go to skin page with network idle wait
            await page.goto(skin["url"], timeout=60000, waitUntil='networkidle2')

            # Wait for general container to appear (adjust selector if needed)
            await page.waitForSelector("div.relative", timeout=30000)

            # Get HTML content and parse with BeautifulSoup
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Find all price containers
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
            # Save HTML and screenshot for debugging
            content = await page.content()
            safe_name = skin['name'].replace(' ', '_').replace('|', '').replace('/', '')
            with open(f"{DEBUG_SAVE_PATH}/{safe_name}.html", "w", encoding="utf-8") as f:
                f.write(content)
            await page.screenshot({'path': f"{DEBUG_SAVE_PATH}/{safe_name}.png"})
            print(f"Saved debug files for {skin['name']} in {DEBUG_SAVE_PATH}")

        # Random delay between requests
        await asyncio.sleep(random.uniform(2, 4))

    await browser.close()

    # Write updated data back to JSON
    with open(JSON_PATH, "w") as f:
        json.dump(skins, f, indent=2)

if __name__ == "__main__":
    asyncio.run(update_skins())