import requests
from bs4 import BeautifulSoup

# -------------------------------
# Config
# -------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36"
}

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1409010823287803945/2hXaZsB5zlfhCEZouu4YOIoAnpEjoJ5PaH4e6fntbQY1TgZFvtogA5tnGwX84BNJn-6f"  # <-- paste your webhook URL here

# -------------------------------
# Scraper
# -------------------------------
def run_scraper():
    url = "https://www.cars.com/shopping/results/?makes[]=porsche&models[]=porsche-911&stock_type=used"
    resp = requests.get(url, headers=HEADERS)

    print("Status Code:", resp.status_code)

    # Print first 1000 chars of HTML so we can confirm we got the page
    print(resp.text[:1000])

    soup = BeautifulSoup(resp.text, "html.parser")

    listings = []

    for card in soup.select(".vehicle-card"):
        title = card.select_one(".title")
        price = card.select_one(".primary-price")

        title_text = title.get_text(strip=True) if title else "N/A"
        price_text = price.get_text(strip=True) if price else "N/A"

        print("Found car:", title_text, "|", price_text)

        listings.append({
            "title": title_text,
            "price": price_text,
            "link": "https://www.cars.com" + card.a["href"] if card.a else "",
            "image": card.select_one("img")["src"] if card.select_one("img") else ""
        })

    return listings

# -------------------------------
# Discord
# -------------------------------
def send_to_discord(listings):
    """Send filtered listings to Discord webhook"""
    if not listings:
        print("No new listings to send.")
        return

    for car in listings:
        message = {
            "embeds": [{
                "title": car.get("title", "Porsche 911 Listing"),
                "url": car.get("link", ""),
                "description": f"Price: {car.get('price', 'N/A')}",
                "image": {"url": car.get("image", "")}
            }]
        }
        try:
            r = requests.post(DISCORD_WEBHOOK, json=message)
            if r.status_code == 204:
                print("✅ Sent to Discord:", car.get("title"))
            else:
                print("⚠️ Discord error:", r.status_code, r.text)
        except Exception as e:
            print(f"❌ Error sending to Discord: {e}")