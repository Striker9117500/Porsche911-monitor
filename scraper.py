import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}

# Your filters
MIN_PRICE = 80000
MAX_PRICE = 130000
MIN_YEAR = 2015
MAX_YEAR = 2023
TRIMS = [
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
]
COLORS = ["red", "silver", "grey", "gray", "white"]

def matches_filters(car):
    """Check if a scraped car matches your rules."""
    try:
        price = car.get("price", 0)
        year = car.get("year", 0)
        title = car.get("title", "").lower()
        color = car.get("color", "unknown").lower()
        accidents = car.get("accidents", "unknown").lower()
        features = car.get("features", "").lower()
        condition = car.get("condition", "").lower()

        if not (MIN_PRICE <= price <= MAX_PRICE):
            return False
        if not (MIN_YEAR <= year <= MAX_YEAR):
            return False
        if not any(trim.lower() in title for trim in TRIMS):
            return False
        if accidents not in ["0 accidents", "no accidents", "clean"]:
            return False
        if "sunroof" not in features and "moonroof" not in features:
            return False
        if "leather" not in features:
            return False
        if color != "unknown" and not any(c in color for c in COLORS):
            return False
        if "clean title" not in condition:
            return False
        return True
    except Exception:
        return False


def run_scraper():
    url = "https://www.cars.com/shopping/results/?makes[]=porsche&models[]=porsche-911&stock_type=used"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")

    listings = []

    for card in soup.select(".vehicle-card"):
        try:
            title = card.select_one(".title").get_text(strip=True)
            price_text = card.select_one(".primary-price").get_text(strip=True)
            price = int(re.sub(r"[^\d]", "", price_text))
            link = "https://www.cars.com" + card.select_one("a.vehicle-card-link")["href"]

            # year from title
            year_match = re.match(r"(\d{4})", title)
            year = int(year_match.group(1)) if year_match else 0

            # features (Cars.com shows extras in .vehicle-details)
            features = " ".join(d.get_text(" ", strip=True) for d in card.select(".vehicle-details li"))

            # placeholder: cars.com doesn’t always give accidents/color inline — would need detail page scrape
            car = {
                "title": title,
                "price": price,
                "year": year,
                "color": "unknown",
                "features": features,
                "accidents": "0 accidents",  # stub until detail scrape
                "condition": "clean title",  # stub until detail scrape
                "url": link,
                "img": card.select_one("img")["src"] if card.select_one("img") else "",
            }

            if matches_filters(car):
                listings.append(car)

        except Exception as e:
            print("Error parsing car:", e)

    return listings