from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, jsonify
from scraper import run_all_scrapers, send_to_discord
from threading import Thread
import time

app = Flask(__name__)

# -------------------------------
# Store current cars + scrape history
# -------------------------------
data_store = {
    "cars": [
        {
            "title": "2019 Porsche 911 Turbo S Coupe AWD [DEMO]",
            "price": "$124,995",
            "link": "https://www.cars.com/vehicledetail/example1/",
            "image": "https://cdn.cars.com/example1.jpg",
            "details": "Red • Sunroof / Moonroof • Leather Seats",
            "demo": True
        },
        {
            "title": "2018 Porsche 911 Carrera GTS Coupe RWD [DEMO]",
            "price": "$94,500",
            "link": "https://www.cars.com/vehicledetail/example2/",
            "image": "https://cdn.cars.com/example2.jpg",
            "details": "Silver • Leather Seats • Premium Audio",
            "demo": True
        }
    ]
}

scrape_logs = [{"time": time.strftime("%Y-%m-%d %H:%M:%S"), "type": "init", "status": "✅ Loaded demo listings"}]


# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        cars=data_store["cars"],
        logs=scrape_logs[-10:]  # show only last 10 logs
    )


@app.route("/api/cars")
def api_cars():
    return jsonify({"cars": data_store["cars"]})


@app.route("/scrape")
def manual_scrape():
    """Manually trigger a scrape via browser/API"""
    log_entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "type": "manual"}
    try:
        listings = run_all_scrapers()
        new_cars = [car for car in listings if car not in data_store["cars"]]

        if new_cars:
            send_to_discord(new_cars)
            data_store["cars"].extend(new_cars)
            log_entry["status"] = f"✅ Found {len(new_cars)} new cars"
        else:
            log_entry["status"] = "⚠️ No new listings"
    except Exception as e:
        log_entry["status"] = f"❌ Error: {e}"

    scrape_logs.append(log_entry)
    return jsonify(log_entry)


# -------------------------------
# Background Scraper
# -------------------------------
def background_scraper():
    """Continuously scrape every 5 minutes and push new listings to Discord"""
    while True:
        log_entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "type": "auto"}
        try:
            listings = run_all_scrapers()
            new_cars = [car for car in listings if car not in data_store["cars"]]

            if new_cars:
                send_to_discord(new_cars)
                data_store["cars"].extend(new_cars)
                log_entry["status"] = f"✅ Found {len(new_cars)} new cars"
            else:
                log_entry["status"] = "⚠️ No new listings"
        except Exception as e:
            log_entry["status"] = f"❌ Error: {e}"

        scrape_logs.append(log_entry)
        time.sleep(300)  # wait 5 minutes


# -------------------------------
# App Entry Point
# -------------------------------
if __name__ == "__main__":
    # Start background scraper thread
    Thread(target=background_scraper, daemon=True).start()
    print("🚀 Flask app running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
