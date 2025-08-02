import streamlit as st
import folium
from streamlit_folium import st_folium

# Set up page
st.set_page_config(page_title="DORRT: Disaster Orbit Response & Relief Tool")
st.title("🌍 DORRT: Disaster Orbit Response & Relief Tool")

# Disaster selection
disaster = st.selectbox("Select Disaster Type", ["Wildfire", "Flood", "Hurricane", "Earthquake", "Tornado"])
radius_km = st.slider("Disaster Impact Radius (km)", 10, 300, 80)

disaster_styles = {
    "Wildfire": {"color": "red"},
    "Flood": {"color": "blue"},
    "Hurricane": {"color": "gray"},
    "Earthquake": {"color": "orange"},
    "Tornado": {"color": "purple"}
}

# Initial map
m = folium.Map(location=[20.0, 0.0], zoom_start=2)
folium.LatLngPopup().add_to(m)

# Show map and capture click
st.markdown("Click on the map to set the disaster center.")
map_data = st_folium(m, width=700, height=500)

# If user clicked the map
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    st.success(f"Disaster Center Set At: ({lat:.4f}, {lon:.4f})")

    # Redraw map centered on clicked point
    m = folium.Map(location=[lat, lon], zoom_start=6)

    # Add circle and marker
    folium.Circle(
        location=[lat, lon],
        radius=radius_km * 1000,
        color=disaster_styles[disaster]["color"],
        fill=True,
        fill_opacity=0.4,
        popup=f"{disaster} Simulation"
    ).add_to(m)

    folium.Marker([lat, lon], popup="Disaster Center").add_to(m)

    st_folium(m, width=700, height=500)
else:
    st.warning("Click on the map above to begin the simulation.")
