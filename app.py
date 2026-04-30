from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
from main import SunriseDemandSystem

app = Flask(__name__)

os.makedirs("data", exist_ok=True)
os.makedirs("reports", exist_ok=True)


@app.route('/')
def home():
    return send_file("index.html")


# Monday Morning Report API
@app.route('/api/report')
def report():
    try:
        df = pd.read_csv("reports/D4_Monday_Morning_Report.csv")
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])


# Weekly Forecast API
@app.route('/api/forecast')
def forecast():
    try:
        df = pd.read_csv("reports/D1_6_Week_Forecast.csv")
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])


# Download Monday Report
@app.route('/download-report')
def download_report():
    return send_file(
        "reports/D4_Monday_Morning_Report.csv",
        as_attachment=True
    )


# Download Forecast
@app.route('/download-forecast')
def download_forecast():
    return send_file(
        "reports/D1_6_Week_Forecast.csv",
        as_attachment=True
    )


# Run Forecast
@app.route('/run-forecast', methods=['POST'])
def run_forecast():

    request.files['sales'].save(
        "data/sales_history.csv"
    )

    request.files['inventory'].save(
        "data/inventory_snapshot.csv"
    )

    request.files['sku'].save(
        "data/sku_master.csv"
    )

    request.files['outlet'].save(
        "data/outlet_master.csv"
    )

    system = SunriseDemandSystem()
    system.run_pipeline()

    return jsonify({
        "message": "Forecast Completed Successfully!"
    })


if __name__ == "__main__":
    app.run(debug=True)