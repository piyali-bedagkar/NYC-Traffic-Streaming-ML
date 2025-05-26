import os
import osmnx as ox
import geopandas as gpd

print("📂 Current directory:", os.getcwd())

# Load street segments
G = ox.graph_from_place('Manhattan, New York City, New York, USA', network_type='drive')
edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

# Add segment_id column
edges = edges.reset_index(drop=True)
edges['segment_id'] = edges.index

# Save GeoJSON
out_file = "segments.geojson"
print(f"💾 Saving to {out_file}...")
edges[['segment_id', 'geometry']].to_file(out_file, driver="GeoJSON")
print("✅ Saved segments.geojson")
