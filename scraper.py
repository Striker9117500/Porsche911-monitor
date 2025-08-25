from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
from twilio.rest import Client

# -------------------------------
# Config
# -------------------------------
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
    "Turbo S",
    "Carrera GTS",
    "Carrera 4 GTS",
    "Turbo Coupe",
}
FEATURES = {"Sunroof / Moonroof", "Leather Seats"}
COLORS = {"Red", "Silver", "Grey", "White", "Unknown"}

# -------------------------------
# Selenium Browser Setup (persistent session)
# -------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Keep this driver alive for the entire Flask app
driver = webdriver.Chrome(options=chrome_options)


# -------------------------------
# Scraper
# -------------------------------
def run_scraper():
    driver.get(URL)
    time.sleep(5)  # wait for JS to render

    listings = []
    cars = driver.find_elements(By.CSS_SELECTOR, "div.vehicle-card")

    for car in cars:
        try:
            title = car.find_element(By.CSS_SELECTOR, "h2.title").text
            price = car.find_element(By.CSS_SELECTOR, "span.primary-price").text
            details = car.text  # grab all text from the card

            # Basic filters
            if not any(trim in title for trim in TRIMS):
                continue
            if not any(feature in details for feature in FEATURES):
                continue
            if not any(color in details for color in COLORS):
                continue

            link = car.find_element(By.CSS_SELECTOR, "a.vehicle-card-link").get_attribute("href")
            image_el = car.find_element(By.CSS_SELECTOR, "img")
            image = image_el.get_attribute("src") if image_el else ""

            listings.append({
                "title": title,
                "price": price,
                "link": link,
                "image": image,
                "details": details
            })

        except Exception:
            continue

    print(f"✅ Found {len(listings)} matching listings")
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


# -------------------------------
# Twilio SMS
# -------------------------------
TWILIO_SID = "MGfdc320f74f891af9faa761043fa1bd13"
TWILIO_AUTH = "127ab47e2ff64db40a091b3c80647a1e"
TWILIO_FROM = "+18777300509"   # Your Twilio number
TWILIO_TO = "+16233098770"     # Your phone number

client = Client(TWILIO_SID, TWILIO_AUTH)

def send_sms(listings):
    if not listings:
        print("No new listings for SMS.")
        return

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
