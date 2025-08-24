from flask import Flask, render_template, jsonify
from scraper import run_scraper, send_to_discord
from threading import Thread
import time

app = Flask(__name__)

# Store current cars + scrape history
data_store = {"cars": []}
scrape_logs = []  # keep track of scrape history


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
        listings = run_scraper()
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
            listings = run_scraper()
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
