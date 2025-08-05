import json
import asyncio
import random
import time
import os
from pyppeteer import launch
from bs4 import BeautifulSoup

os.environ['PYPPETEER_EXECUTABLE_PATH'] = '/usr/bin/chromium-browser'
json_path = "/var/www/html/skintracker/skins.json"

async def update_skins():
    with open(json_path, "r") as f:
        skins = json.load(f)

    browser = await launch(executablePath='/usr/bin/chromium-browser',headless=True, args=['--no-sandbox'])
    page = await browser.newPage()

    for skin in skins:
        try:
            print(f"Updating: {skin['name']}")
            await page.goto(skin["url"], timeout=30000)
            await page.waitForSelector("div.relative", timeout=15000)
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Price
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

            # Image
            img_tag = soup.select_one("div.relative > img")
            if img_tag and img_tag.has_attr("src"):
                skin["image"] = img_tag["src"]
                print(f"→ Image URL found: {skin['image']}")
            else:
                print("→ Image URL not found.")

        except Exception as e:
            print(f"Error updating {skin['name']}: {e}")

        await asyncio.sleep(random.uniform(2, 4))

    await browser.close()

    with open(json_path, "w") as f:
        json.dump(skins, f, indent=2)

asyncio.get_event_loop().run_until_complete(update_skins())