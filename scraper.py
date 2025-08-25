import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from twilio.rest import Client

# -------------------------------
# Config
# -------------------------------
DISCORD_WEBHOOK = "YOUR_WEBHOOK_HERE"

TRIMS = {
    "Carrera GTS Coupe AWD",
    "Carrera GTS Coupe RWD",
    "Turbo Coupe AWD",
    "Turbo S Coupe AWD",
    "Carrera 4 GTS Coupe AWD",
    "Carrera S Turbo Coupe RWD",
    "Carrera Turbo Coupe",
    "Carrera Turbo Coupe RWD",
    "Carrera GTS",
    "Carrera 4 GTS",
    "Turbo S",
    "Turbo",
    "Turbo Coupe",
}
FEATURES = {"Sunroof / Moonroof", "Leather Seats"}
COLORS = {"Red", "Silver", "Grey", "White", "Unknown"}

# -------------------------------
# Selenium Setup
# -------------------------------
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# -------------------------------
# Site Scrapers
# -------------------------------
def scrape_cars():
    url = "https://www.cars.com/shopping/results/?makes[]=porsche&models[]=porsche-911&stock_type=used&list_price_min=80000&list_price_max=130000&year_min=2015&year_max=2023"
    driver = get_driver()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    listings = []
    for card in soup.select(".vehicle-card"):
        title = card.select_one(".title")
        price = card.select_one(".primary-price")
        title_text = title.get_text(strip=True) if title else "N/A"
        price_text = price.get_text(strip=True) if price else "N/A"
        details = " ".join(d.get_text(strip=True) for d in card.select(".listing-row__details span"))

        if not any(trim in title_text for trim in TRIMS): continue
        if not any(feature in details for feature in FEATURES): continue
        if not any(color in details for color in COLORS): continue

        listings.append({
            "title": title_text,
            "price": price_text,
            "link": "https://www.cars.com" + card.a["href"] if card.a else "",
            "image": card.select_one("img")["src"] if card.select_one("img") else "",
            "details": details
        })
    return listings

def scrape_autotrader():
    url = "https://www.autotrader.com/cars-for-sale/porsche/911?dma=&searchRadius=0&location=&startYear=2015&endYear=2023&priceRange=80000-130000"
    driver = get_driver()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    listings = []
    for card in soup.select("div.inventory-listing"):
        title = card.select_one("h2")
        price = card.select_one(".first-price")
        title_text = title.get_text(strip=True) if title else "N/A"
        price_text = price.get_text(strip=True) if price else "N/A"

        details = " ".join(d.get_text(strip=True) for d in card.select(".text-gray-base"))

        if not any(trim in title_text for trim in TRIMS): continue
        if not any(color in details for color in COLORS): continue

        listings.append({
            "title": title_text,
            "price": price_text,
            "link": card.a["href"] if card.a else "",
            "image": card.select_one("img")["src"] if card.select_one("img") else "",
            "details": details
        })
    return listings

def scrape_cargurus():
    url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=85001&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50000&entitySelectingHelper.selectedEntity=d404"
    driver = get_driver()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    listings = []
    for card in soup.select(".cg-listingCard"):
        title = card.select_one("h4")
        price = card.select_one(".cg-dealFinder-priceAndMoPayment")
        title_text = title.get_text(strip=True) if title else "N/A"
        price_text = price.get_text(strip=True) if price else "N/A"
        details = " ".join(d.get_text(strip=True) for d in card.select("li"))

        if not any(trim in title_text for trim in TRIMS): continue
        if not any(color in details for color in COLORS): continue

        listings.append({
            "title": title_text,
            "price": price_text,
            "link": "https://www.cargurus.com" + card.a["href"] if card.a else "",
            "image": card.select_one("img")["src"] if card.select_one("img") else "",
            "details": details
        })
    return listings

def scrape_carmax():
    url = "https://www.carmax.com/cars/porsche/911?price=80000-130000&year=2015-2023"
    driver = get_driver()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    listings = []
    for card in soup.select(".car-tile"):
        title = card.select_one(".car-title")
        price = card.select_one(".price")
        title_text = title.get_text(strip=True) if title else "N/A"
        price_text = price.get_text(strip=True) if price else "N/A"
        details = " ".join(d.get_text(strip=True) for d in card.select("li"))

        if not any(trim in title_text for trim in TRIMS): continue
        if not any(color in details for color in COLORS): continue

        listings.append({
            "title": title_text,
            "price": price_text,
            "link": "https://www.carmax.com" + card.a["href"] if card.a else "",
            "image": card.select_one("img")["src"] if card.select_one("img") else "",
            "details": details
        })
    return listings

# -------------------------------
# Run All Scrapers
# -------------------------------
def run_scraper():
    all_listings = []
    for scraper in [scrape_cars, scrape_autotrader, scrape_cargurus, scrape_carmax]:
        try:
            results = scraper()
            all_listings.extend(results)
        except Exception as e:
            print(f"❌ Error scraping {scraper.__name__}: {e}")
    return all_listings

# -------------------------------
# Discord + SMS (same as before)
# -------------------------------
def send_to_discord(listings):
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
        except Exception as e:
            print(f"❌ Error sending to Discord: {e}")

TWILIO_SID = "MGfdc320f74f891af9faa761043fa1bd13"
TWILIO_AUTH = "127ab47e2ff64db40a091b3c80647a1e"
TWILIO_FROM = "+18777300509"
TWILIO_TO = "+16233098770"

client = Client(TWILIO_SID, TWILIO_AUTH)

def send_sms(listings):
    for car in listings:
        msg = (
            f"New Porsche 911:\n"
            f"{car.get('title', '')}\n"
            f"Price: {car.get('price', '')}\n"
            f"{car.get('link', '')}"
        )
        try:
            message = client.messages.create(
                body=msg,
                from_=TWILIO_FROM,
                to=TWILIO_TO
            )
            print("✅ SMS sent:", message.sid)
        except Exception as e:
            print("❌ Error sending SMS:", e)
