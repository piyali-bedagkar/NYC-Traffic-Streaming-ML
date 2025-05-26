import pandas as pd
import joblib
import numpy as np
import ast

# File paths
MODEL_FILE = "travel_model.joblib"
INPUT_FILE = "nyc_traffic_data.csv"
OUTPUT_FILE = "predictions.csv"

# ✅ Load trained model
try:
    model = joblib.load(MODEL_FILE)
    print("✅ Loaded model:", MODEL_FILE)
except Exception as e:
    print("❌ Failed to load model:", e)
    exit(1)

# ✅ Load input data
try:
    df = pd.read_csv(INPUT_FILE)
    print("✅ Loaded live input data:", INPUT_FILE)
except Exception as e:
    print("❌ Failed to load input data:", e)
    exit(1)

# ✅ Parse segment_ids as lists
df["segment_ids"] = df["segment_ids"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# ✅ Explode to per-segment rows
exploded_df = df[["vehicle_id", "segment_ids", "speed_kmph"]].explode("segment_ids")
exploded_df.rename(columns={"segment_ids": "segment_id"}, inplace=True)

# ✅ Calculate average speed per segment_id
avg_speed_df = exploded_df.groupby("segment_id")["speed_kmph"].mean().reset_index()
avg_speed_df.rename(columns={"speed_kmph": "avg_segment_speed"}, inplace=True)

# ✅ Classify segment color
def classify_color(speed):
    if speed < 30:
        return "red"
    elif speed < 60:
        return "yellow"
    else:
        return "green"

avg_speed_df["color"] = avg_speed_df["avg_segment_speed"].apply(classify_color)

# ✅ Map color to each segment for each vehicle
exploded_df = exploded_df.merge(avg_speed_df, on="segment_id", how="left")

# ✅ Count red/yellow/green segments per vehicle
counts = exploded_df.groupby("vehicle_id")["color"].value_counts().unstack().fillna(0).astype(int)
counts = counts.rename(columns=lambda x: f"{x}_count")
counts["total_segments"] = counts.sum(axis=1)

# ✅ Merge back with original df
df = df.merge(counts, on="vehicle_id", how="left").fillna(0)

# ✅ Predict travel time
try:
    features = ["red_count", "yellow_count", "green_count", "total_segments"]
    df["predicted_travel_time_sec"] = model.predict(df[features])
    print("✅ Prediction successful.")
except Exception as e:
    print("❌ Prediction failed:", e)
    exit(1)

# ✅ Save prediction output
output_cols = [
    "vehicle_id", "start_lat", "start_lon", "end_lat", "end_lon",
    "red_count", "yellow_count", "green_count", "total_segments",
    "predicted_travel_time_sec", "segment_ids", "speed_kmph", "timestamp"
]
df[output_cols].to_csv(OUTPUT_FILE, index=False)
print(f"📁 Saved predictions to {OUTPUT_FILE}")
