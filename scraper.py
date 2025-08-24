import requests

# Replace with real scraping logic
def run_scraper():
    # Simulated test data (replace this with your actual scraping logic)
    return [
        {
            "title": "2020 Porsche 911 Carrera",
            "price": "$110,000",
            "mileage": "12,000 miles",
            "url": "https://example.com/listing/123",
        }
    ]

# Sends a list of car listings to Discord
def send_to_discord(listings):
    webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
    for car in listings:
        message = f"**{car['title']}**\nPrice: {car['price']}\nMileage: {car['mileage']}\n[View Listing]({car['url']})"
        data = {"content": message}
        try:
            r = requests.post(webhook_url, json=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send to Discord: {e}")