from flask import Flask, render_template, jsonify
from scraper import run_scraper, send_to_discord
from threading import Thread
import time

app = Flask(__name__)
data_store = {"cars": []}

@app.route("/")
def index():
    return render_template("index.html", cars=data_store["cars"])

@app.route("/api/cars")
def api_cars():
    return jsonify({"cars": data_store["cars"]})

# Background task to scrape listings every 5 minutes
def background_scraper():
    while True:
        print("Scraping new listings...")
        listings = run_scraper()
        new_cars = [car for car in listings if car not in data_store["cars"]]
        
        if new_cars:
            print(f"Found {len(new_cars)} new cars.")
            send_to_discord(new_cars)
            data_store["cars"].extend(new_cars)
        else:
            print("No new listings.")
        
        time.sleep(300)  # Wait 5 minutes

if __name__ == "__main__":
    # Start background thread
    Thread(target=background_scraper, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)