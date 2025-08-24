import json

def run_scraper():
    # Placeholder scraper logic
    # TODO: implement site-specific scrapers
    with open("config.json") as f:
        cfg = json.load(f)
    # Mock listing
    return [{
        "title": "2020 Porsche 911 Turbo S",
        "price": 125000,
        "year": 2020,
        "trim": "Turbo S Coupe AWD",
        "color": "red",
        "features": ["sunroof", "leather seats"],
        "accident_free": True,
        "clean_title": True,
        "url": "https://example.com/car",
        "image": "https://example.com/car.jpg"
    }]
