# train_model.py

import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Load training data
df = pd.read_csv("training_data.csv")

# Define features and label
features = ["red_count", "yellow_count", "green_count", "total_segments"]
X = df[features]
y = df["true_travel_time_sec"]

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LinearRegression())
])

# Train model
pipeline.fit(X, y)

# Save model
joblib.dump(pipeline, "travel_model.joblib")
print("✅ Model trained and saved as travel_model.joblib")
