from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from twilio.rest import Client
import requests

# -------------------------------
# Config
# -------------------------------
DISCORD_WEBHOOK = "YOUR_WEBHOOK_HERE"

TRIMS = {
    "Carrera GTS Coupe AWD", "Carrera GTS Coupe RWD",
    "Turbo Coupe AWD", "Turbo S Coupe AWD",
    "Carrera 4 GTS Coupe AWD", "Carrera S Turbo Coupe RWD",
    "Carrera Turbo Coupe", "Carrera Turbo Coupe RWD",
    "Turbo", "Turbo Coupe", "Turbo S", "Carrera GTS", "Carrera 4 GTS",
}
FEATURES = {"Sunroof / Moonroof", "Leather Seats"}
COLORS = {"Red", "Silver", "Grey", "White", "Unknown"}

# Twilio
TWILIO_SID = "MGfdc320f74f891af9faa761043fa1bd13"
TWILIO_AUTH = "127ab47e2ff64db40a091b3c80647a1e"
TWILIO_FROM = "+18777300509"
TWILIO_TO = "+16233098770"
client = Client(TWILIO_SID, TWILIO_AUTH)


# -------------------------------
# Selenium setup
# -------------------------------
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# -------------------------------
# Site Scrapers
# -------------------------------
def scrape_cars_com(driver):
    url = "https://www.cars.com/shopping/results/?makes[]=porsche&models[]=porsche-911&stock_type=used&list_price_min=80000&list_price_max=130000&year_min=2015&year_max=2023"
    driver.get(url)
    time.sleep(3)

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, ".vehicle-card")
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, ".title").text
            price = card.find_element(By.CSS_SELECTOR, ".primary-price").text
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            image = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            details = card.text

            if not any(trim in title for trim in TRIMS):
                continue
            if not any(color in details for color in COLORS):
                continue

            listings.append({
                "title": title, "price": price, "link": link,
                "image": image, "details": details, "site": "Cars.com"
            })
        except:
            continue
    return listings


def scrape_autotrader(driver):
    url = "https://www.autotrader.com/cars-for-sale/porsche/911"
    driver.get(url)
    time.sleep(4)

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div.inventory-listing")
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, "h2").text
            price = card.find_element(By.CSS_SELECTOR, ".first-price").text
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            image = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            details = card.text

            listings.append({
                "title": title, "price": price, "link": link,
                "image": image, "details": details, "site": "Autotrader"
            })
        except:
            continue
    return listings


def scrape_cargurus(driver):
    url = "https://www.cargurus.com/Cars/l-Used-Porsche-911-d404"
    driver.get(url)
    time.sleep(4)

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, ".cg-dealFinderResult-wrap")
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, ".cg-listingTitle").text
            price = card.find_element(By.CSS_SELECTOR, ".cg-listingPrice").text
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            image = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            details = card.text

            listings.append({
                "title": title, "price": price, "link": link,
                "image": image, "details": details, "site": "CarGurus"
            })
        except:
            continue
    return listings


def scrape_carmax(driver):
    url = "https://www.carmax.com/cars/porsche/911"
    driver.get(url)
    time.sleep(4)

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, ".car-tile")
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, ".car-title").text
            price = card.find_element(By.CSS_SELECTOR, ".car-price").text
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            image = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            details = card.text

            listings.append({
                "title": title, "price": price, "link": "https://carmax.com" + link,
                "image": image, "details": details, "site": "CarMax"
            })
        except:
            continue
    return listings


def scrape_autotempest(driver):
    url = "https://www.autotempest.com/cars/porsche-911"
    driver.get(url)
    time.sleep(4)

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, ".result")
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, ".result-title").text
            price = card.find_element(By.CSS_SELECTOR, ".result-price").text
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            image = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            details = card.text

            listings.append({
                "title": title, "price": price, "link": link,
                "image": image, "details": details, "site": "AutoTempest"
            })
        except:
            continue
    return listings


# -------------------------------
# Main Runner
# -------------------------------
def run_all_scrapers():
    driver = get_driver()
    all_listings = []
    health_log = {}

    try:
        try:
            cars_com = scrape_cars_com(driver)
            all_listings.extend(cars_com)
            health_log["Cars.com"] = f"✅ {len(cars_com)} listings"
        except Exception as e:
            health_log["Cars.com"] = f"❌ {e}"

        try:
            autotrader = scrape_autotrader(driver)
            all_listings.extend(autotrader)
            health_log["Autotrader"] = f"✅ {len(autotrader)} listings"
        except Exception as e:
            health_log["Autotrader"] = f"❌ {e}"

        try:
            cargurus = scrape_cargurus(driver)
            all_listings.extend(cargurus)
            health_log["CarGurus"] = f"✅ {len(cargurus)} listings"
        except Exception as e:
            health_log["CarGurus"] = f"❌ {e}"

        try:
            carmax = scrape_carmax(driver)
            all_listings.extend(carmax)
            health_log["CarMax"] = f"✅ {len(carmax)} listings"
        except Exception as e:
            health_log["CarMax"] = f"❌ {e}"

        try:
            autotempest = scrape_autotempest(driver)
            all_listings.extend(autotempest)
            health_log["AutoTempest"] = f"✅ {len(autotempest)} listings"
        except Exception as e:
            health_log["AutoTempest"] = f"❌ {e}"

    finally:
        driver.quit()

    # Deduplicate by link
    unique = {}
    for car in all_listings:
        if car["link"] not in unique:
            unique[car["link"]] = car

    return list(unique.values()), health_log


    # Deduplicate by link
    unique = {}
    for car in all_listings:
        if car["link"] not in unique:
            unique[car["link"]] = car

    return list(unique.values())


# -------------------------------
# Discord + SMS
# -------------------------------
def send_to_discord(listings):
    for car in listings:
        message = {
            "embeds": [{
                "title": car["title"],
                "url": car["link"],
                "description": f"Price: {car['price']}\nSource: {car['site']}\nDetails: {car['details']}",
                "image": {"url": car["image"]}
            }]
        }
        try:
            r = requests.post(DISCORD_WEBHOOK, json=message)
            print("✅ Discord:", car["title"])
        except Exception as e:
            print("❌ Discord error:", e)


def send_sms(listings):
    for car in listings:
        msg = f"{car['site']} - {car['title']}\n{car['price']}\n{car['link']}"
        try:
            message = client.messages.create(
                body=msg, from_=TWILIO_FROM, to=TWILIO_TO
            )
            print("✅ SMS:", message.sid)
        except Exception as e:
            print("❌ SMS error:", e)


if __name__ == "__main__":
    cars = run_all_scrapers()
    print(f"Found {len(cars)} unique listings")
    send_to_discord(cars)
    send_sms(cars)
