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

DISCORD_WEBHOOK = "YOUR_WEBHOOK_HERE"

URL = "https://www.cars.com/shopping/results/?makes[]=porsche&models[]=porsche-911&stock_type=used&list_price_min=80000&list_price_max=130000&year_min=2015&year_max=2023"

# Your filters
TRIMS = {
    "Carrera GTS Coupe AWD",
    "Carrera GTS Coupe RWD",
    "Turbo Coupe AWD",
    "Turbo S Coupe AWD",
    "Carrera 4 GTS Coupe AWD",
    "Carrera S Turbo Coupe RWD",
    "Carrera Turbo Coupe",
    "Carrera Turbo Coupe RWD",
    "Turbo",
    "Turbo Coupe",
}
FEATURES = {"Sunroof / Moonroof", "Leather Seats"}
COLORS = {"Red", "Silver", "Grey", "White", "Unknown"}


# -------------------------------
# Scraper
# -------------------------------
def run_scraper():
    resp = requests.get(URL, headers=HEADERS)
    print("Status Code:", resp.status_code)

    soup = BeautifulSoup(resp.text, "html.parser")
    listings = []

    for card in soup.select(".vehicle-card"):
        title = card.select_one(".title")
        price = card.select_one(".primary-price")

        title_text = title.get_text(strip=True) if title else "N/A"
        price_text = price.get_text(strip=True) if price else "N/A"

        # Extract details text (features, color, trim etc)
        details = " ".join(d.get_text(strip=True) for d in card.select(".listing-row__details span"))

        # Basic filters
        if not any(trim in title_text for trim in TRIMS):
            continue
        if not any(feature in details for feature in FEATURES):
            continue
        if not any(color in details for color in COLORS):
            continue

        listings.append({
            "title": title_text,
            "price": price_text,
            "link": "https://www.cars.com" + card.a["href"] if card.a else "",
            "image": card.select_one("img")["src"] if card.select_one("img") else "",
            "details": details
        })

    return listings


# -------------------------------
# Discord
# -------------------------------
def send_to_discord(listings):
    if not listings:
        print("No new listings to send.")
        return

    for car in listings:
        message = {
            "embeds": [{
                "title": car.get("title", "Porsche 911 Listing"),
                "url": car.get("link", ""),
                "description": f"Price: {car.get('price', 'N/A')}\nDetails: {car.get('details', '')}",
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
