import streamlit as st
import plotly.graph_objects as go
import numpy as np

# === Step 1: Define airfoils ===
airfoils = {
    "NACA 2412": "Classic general-purpose airfoil, used in Cessna 172. Good balance of lift and drag.",
    "NACA 4412": "Higher camber than 2412 → more lift at low speeds. Common in older light aircraft.",
    "NACA 0012": "Symmetrical → widely used in aerobatic aircraft and horizontal stabilizers.",
    "NACA 4415": "Higher thickness → better low-speed lift. Used in some trainer aircraft.",
    "Clark Y": "Very common training airfoil, forgiving stall, widely used in small planes.",
    "NASA SC(2)-0714": "Supercritical airfoil → designed for transonic cruise efficiency (jets).",
    "NACA 63-215": "Laminar flow airfoil, designed to reduce drag in gliders and racers.",
    "NACA 64-212": "Used on P-51 Mustang → optimized for laminar flow and high efficiency.",
    "Eppler 387": "Popular for model airplanes & gliders. High lift, gentle stall.",
    "MH 32": "Modern sailplane airfoil, excellent low drag at high Reynolds numbers."
}

# === Streamlit UI ===
st.title("Airfoil Selection Simulator (with Visualization)")
st.write("Choose from 10 common airfoils and see airflow + pressure distribution.")

# Dropdown
selected_airfoil = st.selectbox("Select an Airfoil:", list(airfoils.keys()))
st.subheader(f"📘 {selected_airfoil}")
st.write(airfoils[selected_airfoil])

# === Visualization ===
x = np.linspace(-1, 2, 200)
y = np.linspace(-1, 1, 100)
X, Y = np.meshgrid(x, y)

# Fake velocity field: faster flow over the top
U = 1.0
Vx = U * np.ones_like(X)
Vy = -0.5 * np.exp(-20*((X-0.5)**2 + Y**2))  # "circulation" bump

# Streamlines (airflow)
fig = go.Figure()

fig.add_trace(go.Streamtube(
    x=X.flatten(),
    y=Y.flatten(),
    z=np.zeros_like(X).flatten(),
    u=Vx.flatten(),
    v=Vy.flatten(),
    w=np.zeros_like(X).flatten(),
    sizeref=0.3,
    colorscale="Blues",
    showscale=False,
    opacity=0.6
))

# Pressure blob (red = high, blue = low)
pressure = np.exp(-20*((X-0.5)**2 + Y**2))  # fake pressure bump
fig.add_trace(go.Contour(
    z=pressure,
    x=x,
    y=y,
    colorscale="RdBu",
    contours_coloring="fill",
    opacity=0.4
))

# Layout
fig.update_layout(
    title="Airflow & Pressure Visualization",
    xaxis_title="Chordwise (x)",
    yaxis_title="Vertical (y)",
    height=500
)

st.plotly_chart(fig)
