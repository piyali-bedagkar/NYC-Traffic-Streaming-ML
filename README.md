# 🚦 NYC Traffic Streaming & Travel Time Prediction

A real-time, end-to-end traffic monitoring and travel time prediction system built using Kafka, machine learning, and interactive dashboards. Simulates thousands of vehicle trips across Manhattan, classifies congestion severity, predicts travel time, and visualizes traffic patterns dynamically.

---

### 📌 Overview

This project addresses the problem of delayed traffic responsiveness in urban areas like Manhattan. By simulating live vehicle data, processing it through a streaming pipeline, and applying predictive analytics, the system provides city planners with real-time operational insights — all visualized on a live dashboard.

---

### ⚙️ System Architecture

- **📊 Data Simulation:** 5,000+ vehicle trips generated using OpenStreetMap data (via OSMNX).
- **📡 Kafka Producer/Consumer:** Simulates real-time vehicle movement and streams JSON route data.
- **📁 Data Aggregation:** Batches stored in `nyc_traffic_data.csv` every 5,000 records.
- **🧠 Machine Learning Model:** Linear Regression predicts route-level travel time using segment speeds.
- **📈 Streamlit Dashboard:** Visualizes route congestion, predicted travel times, and live stats.

[Vehicle Simulation] → [Kafka Producer] → [Kafka Consumer] → [Model Prediction] → [Live Dashboard]

---

### 🛠️ Technologies Used

| Component            | Tools / Libraries                                |
|----------------------|--------------------------------------------------|
| Data Streaming       | Apache Kafka (Confluent Cloud)                   |
| Geospatial Mapping   | OSMNX, Shapely, GeoPandas                        |
| ML & Data Science    | Pandas, scikit-learn, joblib                     |
| Web Dashboard        | Streamlit, Plotly, Folium, Mapbox               |
| Programming Language | Python                                           |

---

### 🚀 How to Run

1. Generate Training Data & Train Model - 
   python generate_training_data.py,
   python train_model.py

2. Start Kafka Producer (Simulate Vehicles) - 
   python kafka_producer_nyc.py
   
3. Start Kafka Consumer (Receive Data) - 
   python kafka_consumer_nyc.py
   
4. Predict Travel Times - 
   python predict_live_travel_time.py
   
5. Launch Streamlit Dashboard - 
   streamlit run streamlit_heatmap_dashboard.py

---

### 📊 Dashboard Features

📍 Tab 1: Traffic Overview
- Vehicle counts, route stats, average speed
- Live map showing congestion as:
   🔴 Red (speed < 30 kmph)
   🟡 Yellow (30–60 kmph)
   🟢 Green (> 60 kmph)

🧠 Tab 2: ML Predictions
- Table of predicted travel times
- Destination point maps colored by delay
