import osmnx as ox
import networkx as nx
import pandas as pd
import random
from shapely.geometry import LineString

# Constants
NUM_TRIPS = 5000
SPEED_THRESHOLDS = {"red": 30, "yellow": 60}

# Load street graph
print("📦 Loading street graph for Manhattan...")
G = ox.graph_from_place("Manhattan, New York City, New York, USA", network_type="drive")

# Generate SEGMENT_SPEEDS using osmid keys
edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
SEGMENT_SPEEDS = {}

for _, row in edges.iterrows():
    osmid = row.get("osmid")
    speed = random.choices([20, 40, 70], weights=[0.4, 0.4, 0.2])[0]

    if isinstance(osmid, list):
        for sid in osmid:
            SEGMENT_SPEEDS[sid] = speed
    else:
        SEGMENT_SPEEDS[osmid] = speed

print("✅ Speeds assigned to all segment IDs.")

# Generate training data
nodes = list(G.nodes)
training_data = []

print("🚦 Generating trips...")
for _ in range(NUM_TRIPS):
    try:
        start_node, end_node = random.sample(nodes, 2)
        path = nx.shortest_path(G, start_node, end_node, weight="length")

        red, yellow, green = 0, 0, 0
        trip_time_sec = 0
        segment_count = 0

        for u, v in zip(path[:-1], path[1:]):
            try:
                edge_data = G[u][v][0]
                geom = edge_data.get("geometry", None)
                osmids = edge_data.get("osmid", None)

                if not osmids:
                    continue

                if not isinstance(osmids, list):
                    osmids = [osmids]

                for sid in osmids:
                    speed = SEGMENT_SPEEDS.get(sid, 40)
                    length_m = geom.length * 100000 if geom else 50
                    time = length_m / (speed * 1000 / 3600)
                    trip_time_sec += time

                    if speed < SPEED_THRESHOLDS["red"]:
                        red += 1
                    elif speed < SPEED_THRESHOLDS["yellow"]:
                        yellow += 1
                    else:
                        green += 1
                    segment_count += 1

            except:
                continue

        if segment_count == 0:
            continue

        origin = G.nodes[start_node]
        dest = G.nodes[end_node]

        training_data.append({
            "start_lat": origin["y"],
            "start_lon": origin["x"],
            "end_lat": dest["y"],
            "end_lon": dest["x"],
            "red_count": red,
            "yellow_count": yellow,
            "green_count": green,
            "total_segments": segment_count,
            "true_travel_time_sec": trip_time_sec
        })

    except Exception:
        continue

# Save to CSV
df = pd.DataFrame(training_data)
df.to_csv("training_data.csv", index=False)
print("📁 Saved training_data.csv with", len(df), "trips.")
