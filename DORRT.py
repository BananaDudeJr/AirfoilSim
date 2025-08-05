import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import requests

# === Helper function for projecting spread ===
def project_coordinates(lat, lon, distance_km, bearing_degrees):
    R = 6371.0
    bearing = math.radians(bearing_degrees)

    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(math.sin(lat1) * math.cos(distance_km / R) +
                     math.cos(lat1) * math.sin(distance_km / R) * math.cos(bearing))

    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat1),
                             math.cos(distance_km / R) - math.sin(lat1) * math.sin(lat2))

    return math.degrees(lat2), math.degrees(lon2)

# === Get real wind data ===
def get_wind_data(lat, lon, api_key):
    import requests

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    wind_data = data.get("wind", {})  # use empty dict if "wind" is missing
    speed = wind_data.get("speed", 0)
    deg = wind_data.get("deg", 0)

    return speed, deg


# === App setup ===
st.set_page_config(page_title="DORRT: Disaster Orbit Response & Relief Tool")
st.title("🌍 DORRT: Disaster Orbit Response & Relief Tool")

# === Disaster settings ===
disaster = st.selectbox("Select Disaster Type", ["Wildfire", "Flood", "Hurricane", "Earthquake", "Tornado", "Blizzard", "Drought", "Tsunami"])
radius_km = st.slider("Disaster Impact Radius (km)", 10, 300, 80)

# === Disaster color settings ===
disaster_styles = {
    "Wildfire": {"color": "red"},
    "Flood": {"color": "blue"},
    "Hurricane": {"color": "teal"},
    "Earthquake": {"color": "orange"},
    "Tornado": {"color": "gray"},
    "Blizzard": {"color": "white"},
    "Drought": {"color": "tan"},
    "Tsunami": {"color": "purple"}
}

# === Satellite database ===
satellites = {
    "Landsat 8": {"orbit": "Sun-synchronous", "altitude_km": 705, "resolution": "15m", "revisit_time": "16 days", "best_for": ["Wildfire", "Flood", "Hurricane"]},
    "Sentinel-1": {"orbit": "Polar", "altitude_km": 693, "resolution": "5–20m", "revisit_time": "6–12 days", "best_for": ["Flood", "Earthquake", "Tsunami"]},
    "GOES-16": {"orbit": "Geostationary", "altitude_km": 35786, "resolution": "500m–2km", "revisit_time": "Real-time", "best_for": ["Hurricane", "Blizzard", "Tornado"]},
    "Aqua": {"orbit": "Sun-synchronous", "altitude_km": 705, "resolution": "1km", "revisit_time": "Daily", "best_for": ["Drought", "Wildfire"]},
}

recommended = [name for name, data in satellites.items() if disaster in data["best_for"]]
auto_selected = recommended[0] if recommended else None

st.markdown("---")
st.subheader("🚁️ Satellite Selection")

override = st.checkbox("Override Recommended Satellite")

if override:
    selected_sat = st.selectbox("Select Satellite", list(satellites.keys()))
else:
    if auto_selected:
        st.success(f"Recommended Satellite: {auto_selected}")
        selected_sat = auto_selected
    else:
        st.warning("No satellite recommendation available for this disaster.")
        selected_sat = st.selectbox("Select Satellite", list(satellites.keys()))

if selected_sat:
    data = satellites[selected_sat]
    st.markdown(f"**Orbit Type:** {data['orbit']}")
    st.markdown(f"**Altitude:** {data['altitude_km']} km")
    st.markdown(f"**Resolution:** {data['resolution']}")
    st.markdown(f"**Revisit Time:** {data['revisit_time']}")
    st.markdown(f"**Best For:** {', '.join(data['best_for'])}")

# === Initial map ===
m = folium.Map(location=[20.0, 0.0], zoom_start=2)
folium.LatLngPopup().add_to(m)

st.markdown("Click on the map to set the disaster center.")
map_data = st_folium(m, width=700, height=500)

if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"Disaster Center Set At: ({lat:.4f}, {lon:.4f})")

    m = folium.Map(location=[lat, lon], zoom_start=6)

    # Fetch wind data
    wind_api_key = st.secrets["OPENWEATHER_API_KEY"] if "OPENWEATHER_API_KEY" in st.secrets else "YOUR_API_KEY"
    wind_speed, wind_deg = get_wind_data(lat, lon, wind_api_key)
    st.markdown(f"**Wind Speed:** {wind_speed} m/s")
    st.markdown(f"**Wind Direction:** {wind_deg}°")

    # Disaster center + radius
    folium.Circle(
        location=[lat, lon],
        radius=radius_km * 1000,
        color=disaster_styles[disaster]["color"],
        fill=True,
        fill_opacity=0.4,
        popup=f"{disaster} Simulation"
    ).add_to(m)
    folium.Marker([lat, lon], popup="Disaster Center").add_to(m)

    # === AI spread logic with arrows ===
    directions = {
        "North": 0,
        "East": 90,
        "South": 180,
        "West": 270
    }

    for dir_name, bearing in directions.items():
        end_lat, end_lon = project_coordinates(lat, lon, radius_km * 1.5, bearing)

        # Wind-based spread estimation
        angle_diff = abs(bearing - wind_deg) % 360
        angle_diff = min(angle_diff, 360 - angle_diff)  # Shortest distance around circle

        if angle_diff < 30:
            wind_spread = "High"
        elif angle_diff < 90:
            wind_spread = "Medium"
        else:
            wind_spread = "Low"

        # Placeholder slope logic (replace with elevation API later)
        slope = 0.05
        if slope > 0.1:
            terrain_spread = "High"
        elif slope > 0.03:
            terrain_spread = "Medium"
        else:
            terrain_spread = "Low"

        # Combine both
        final_spread = max(wind_spread, terrain_spread)
        color = "red" if final_spread == "High" else "orange" if final_spread == "Medium" else "yellow"

        folium.PolyLine(
            locations=[[lat, lon], [end_lat, end_lon]],
            color=color,
            weight=4,
            tooltip=f"Spread: {final_spread} toward {dir_name}"
        ).add_to(m)

    st_folium(m, width=700, height=500)
else:
    st.warning("Click on the map above to begin the simulation.")
