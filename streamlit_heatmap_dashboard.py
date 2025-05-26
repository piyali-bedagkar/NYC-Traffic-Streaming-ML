import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Constants
DATA_FILE = "nyc_traffic_data.csv"
PRED_FILE = "predictions.csv"
SEGMENT_FILE = "segments.geojson"
CENTER_LAT, CENTER_LON = 40.7831, -73.9712

st.set_page_config(page_title="🚖 NYC Traffic Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>🚦 NYC Live Traffic Dashboard</h1>", unsafe_allow_html=True)

# Session state
if "refresh_clicked" not in st.session_state:
    st.session_state["refresh_clicked"] = False
    st.session_state["df"] = None
    st.session_state["pred_df"] = None

# Refresh button
if st.button("🔄 Refresh Data + Predict"):
    subprocess.run(["python", "predict_live_travel_time.py"])
    st.session_state["df"] = pd.read_csv(DATA_FILE, on_bad_lines='skip')
    st.session_state["pred_df"] = pd.read_csv(PRED_FILE)
    st.session_state["refresh_clicked"] = True

if not st.session_state["refresh_clicked"]:
    st.info("Click 'Refresh Data + Predict' to load and display traffic information.")
    st.stop()

df = st.session_state["df"]
pred_df = st.session_state["pred_df"]

tab1, tab2 = st.tabs(["📊 Traffic Overview", "🧠 ML Predictions"])

# ------------------ TAB 1 ------------------
with tab1:
    st.subheader("📈 Real-Time Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Vehicles", f"{len(df)}")
        st.metric("Routes Processed", f"{len(pred_df)}")
    with col2:
        avg_speed = df.get("speed_kmph", pd.Series()).mean()
        st.metric("Avg Speed", f"{avg_speed:.2f} kmph" if not pd.isna(avg_speed) else "N/A")
    with col3:
        try:
            latest_time = pd.to_datetime(df['timestamp']).max()
            st.metric("Last Update", latest_time.strftime('%Y-%m-%d %H:%M:%S'))
        except:
            st.metric("Last Update", "Unavailable")

    # Map View Switcher
    st.subheader("🗺️ Map View")
    view_mode = st.radio("Choose Map View:", ["🗺️ Vehicle Points", "🛣️ Segment Heatmap"], horizontal=True)

    if view_mode == "🗺️ Vehicle Points":
        fig = px.scatter_mapbox(
            pred_df,
            lat="start_lat",
            lon="start_lon",
            color="predicted_travel_time_sec",
            color_continuous_scale="Turbo",
            zoom=12.5,
            center={"lat": CENTER_LAT, "lon": CENTER_LON},
            mapbox_style="carto-positron",
            height=600,
            hover_data=["vehicle_id", "total_segments", "red_count", "yellow_count", "green_count"]
        )
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "🛣️ Segment Heatmap":
        try:
            segments_gdf = gpd.read_file(SEGMENT_FILE)
            segments_gdf["segment_id"] = segments_gdf["segment_id"].astype(int)

            if "segment_ids" not in df.columns:
                st.warning("No 'segment_ids' in traffic data. Overlay won't display.")
            else:
                avg_speed_df = df[["segment_ids", "speed_kmph"]].copy()
                avg_speed_df["segment_ids"] = avg_speed_df["segment_ids"].apply(lambda x: eval(x) if isinstance(x, str) else x)
                exploded = avg_speed_df.explode("segment_ids")
                exploded.rename(columns={"segment_ids": "segment_id"}, inplace=True)
                exploded["segment_id"] = exploded["segment_id"].astype(int)

                segment_avg = exploded.groupby("segment_id")["speed_kmph"].mean().reset_index()
                merged = segments_gdf.merge(segment_avg, on="segment_id")

                def get_color(speed):
                    if speed < 30: return "red"
                    elif speed < 60: return "orange"
                    else: return "green"

                merged["color"] = merged["speed_kmph"].apply(get_color)

                m = folium.Map(location=[CENTER_LAT, CENTER_LON], zoom_start=13, tiles="cartodbpositron")
                for _, row in merged.iterrows():
                    if row["geometry"] and hasattr(row["geometry"], "coords"):
                        coords = list(row["geometry"].coords)
                        folium.PolyLine(
                            locations=[(y, x) for x, y in coords],
                            color=row["color"],
                            weight=5,
                            opacity=0.85,
                            tooltip=f"Speed: {row['speed_kmph']:.1f} kmph"
                        ).add_to(m)

                st_folium(m, width=1000, height=600)
        except Exception as e:
            st.error(f"🚫 Could not load segment-level overlay: {e}")

# ------------------ TAB 2 ------------------
with tab2:
    st.subheader("📋 Travel Time Predictions Table")
    st.dataframe(pred_df)

    st.subheader("📍 Destination Points Map")
    fig2 = px.scatter_mapbox(
        pred_df,
        lat="end_lat",
        lon="end_lon",
        color="predicted_travel_time_sec",
        color_continuous_scale="Turbo",
        zoom=12.5,
        center={"lat": CENTER_LAT, "lon": CENTER_LON},
        mapbox_style="carto-positron",
        height=600,
        hover_data=["vehicle_id", "total_segments", "red_count", "yellow_count", "green_count"]
    )
    st.plotly_chart(fig2, use_container_width=True)
