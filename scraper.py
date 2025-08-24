import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36"
}

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
            "link": "https://www.cars.com" + card.a["href"] if card.a else ""
        })

    return listings