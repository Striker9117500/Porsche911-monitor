from flask import Flask, render_template, jsonify
from scraper import run_scraper

app = Flask(__name__)
data_store = {"cars": []}

@app.route("/")
def index():
    return render_template("index.html", cars=data_store["cars"])

@app.route("/api/cars")
def api_cars():
    listings = run_scraper()
    return jsonify({"cars": listings})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
