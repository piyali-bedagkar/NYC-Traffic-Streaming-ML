from confluent_kafka import Producer
import osmnx as ox
from shapely.geometry import LineString
from datetime import datetime
import random
import json
import time
import networkx as nx

# Kafka Config
conf = {
    'bootstrap.servers': 'pkc-619z3.us-east1.gcp.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'CWI6F64GWDVWBPJW',
    'sasl.password': 'RZE8DhS0Q+rei92kP9+WpJwS7hL/yb3g4QflgaFlBjNyMSa4l0UuQWrdYkSkeMLv',
    'client.id': 'nyc-traffic-producer'
}
producer = Producer(conf)

# Load Manhattan road network
print("⏳ Downloading Manhattan street network...")
G = ox.graph_from_place("Manhattan, New York City, New York, USA", network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
street_segments = edges['geometry'].tolist()
print(f"✅ Loaded {len(street_segments)} street segments.")

# Map geometry to segment index
segment_id_map = {str(geom): idx for idx, geom in enumerate(street_segments)}

# Simulate vehicle data
def generate_vehicle_data(vehicle_id, G, node_start, node_end):
    try:
        route = nx.shortest_path(G, node_start, node_end, weight="length")
    except Exception:
        raise ValueError("No path between selected nodes.")

    edge_geoms = []
    segment_indices = []

    for u, v in zip(route[:-1], route[1:]):
        try:
            edge_data = G[u][v][0]  # Get the first edge if multiple exist
        except:
            continue

        # Get geometry or create fallback
        if 'geometry' in edge_data:
            geom = edge_data['geometry']
        else:
            point_u = G.nodes[u]
            point_v = G.nodes[v]
            geom = LineString([(point_u['x'], point_u['y']), (point_v['x'], point_v['y'])])

        edge_geoms.append(geom)

        # Use string version of geometry to find index
        segment_idx = segment_id_map.get(str(geom), None)
        if segment_idx is not None:
            segment_indices.append(segment_idx)

    if not edge_geoms or not segment_indices:
        raise ValueError("No usable geometry or segment found in route.")

    # Start and end coordinates
    start_point = edge_geoms[0].coords[0]
    end_point = edge_geoms[-1].coords[-1]

    # Estimate route distance in kilometers
    total_distance_km = sum(geom.length for geom in edge_geoms) / 1000

    # Assign a natural driving speed
    speed_kmph = round(random.uniform(20, 80), 2)

    return {
        "vehicle_id": vehicle_id,
        "start_lat": start_point[1],
        "start_lon": start_point[0],
        "end_lat": end_point[1],
        "end_lon": end_point[0],
        "segment_ids": segment_indices,
        "speed_kmph": speed_kmph,
        "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }

if __name__ == "__main__":
    print("🚕 Kafka Producer for Manhattan Traffic Started!")
    vehicle_id_counter = 1
    all_nodes = list(G.nodes)

    while True:
        for _ in range(1000):  # Simulate 1000 vehicles/sec
            node_start, node_end = random.sample(all_nodes, 2)
            try:
                vehicle_data = generate_vehicle_data(vehicle_id_counter, G, node_start, node_end)
                producer.produce("nyc_traffic", value=json.dumps(vehicle_data))
                print(f"🚗 Sent: {vehicle_data}")
                vehicle_id_counter += 1
            except Exception as e:
                print(f"⚠️ Skipping invalid route: {e}")
                continue

        producer.flush()
        time.sleep(1)
