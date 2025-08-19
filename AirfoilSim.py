# Before running enter: "cd "C:\Users\hanis\New folder\Websites""
# Then enter: "python -m streamlit run AirfoilSim.py"

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# === 1. Airfoil Data ===
airfoil_files = {
    "NACA 2412": "airfoils/naca2412.dat.txt",
    
}

    # Add remaining 8 airfoils here


def load_airfoil(filename):
    data = np.loadtxt(filename, skiprows=1)
    return data[:,0], data[:,1]

# === 2. Rotate Airfoil for AoA ===
def rotate_airfoil(x, y, alpha_deg, x_ref=0.25):
    alpha = np.radians(alpha_deg)
    x_shifted = x - x_ref
    y_shifted = y
    xr = x_shifted*np.cos(alpha) - y_shifted*np.sin(alpha) + x_ref
    yr = x_shifted*np.sin(alpha) + y_shifted*np.cos(alpha)
    return xr, yr

# === 3. UI ===
st.title("Airfoil Simulator")

selected_airfoil = st.selectbox("Select Airfoil", list(airfoil_files.keys()))
aoa = st.slider("Angle of Attack (°)", -90, 90, 5)
cg_pos = st.radio("Center of Gravity", ["Front", "Middle", "Back"])
U = st.slider("Airflow speed", 10, 100, 30)

# === 4. Load Airfoil ===
x, y = load_airfoil(airfoil_files[selected_airfoil])
x, y = rotate_airfoil(x, y, aoa)

# === 5. Determine CG location ===
if cg_pos=="Front":
    x_cg = np.min(x) + 0.05*(np.max(x)-np.min(x))
elif cg_pos=="Middle":
    x_cg = 0.5*(np.max(x)+np.min(x))
else:
    x_cg = np.max(x) - 0.05*(np.max(x)-np.min(x))
# CG y-coordinate: interpolate along chord
y_cg = np.interp(x_cg, x, y)

# === 6. Airflow field ===
X, Y = np.meshgrid(np.linspace(-0.2,1.2,150), np.linspace(-0.5,0.5,100))
Vx = U*np.ones_like(X)
Vy = np.zeros_like(X)

# Simple mask to avoid arrows inside airfoil
mask = np.zeros_like(X, dtype=bool)
for xi, yi in zip(x, y):
    mask |= (np.abs(X - xi) < 0.02) & (np.abs(Y - yi) < 0.02)
Vx = np.ma.masked_where(mask, Vx)
Vy = np.ma.masked_where(mask, Vy)

# === 7. Pressure blobs ===
pressure_high = np.exp(-50*((Y - 0.05)**2 + (X-0.5)**2))  # above airfoil
pressure_low = np.exp(-50*((Y + 0.05)**2 + (X-0.5)**2))   # below airfoil

# === 8. Plot ===
fig, ax = plt.subplots(figsize=(8,4))
ax.contourf(X, Y, pressure_high, levels=20, cmap="Reds", alpha=0.5)
ax.contourf(X, Y, pressure_low, levels=20, cmap="Blues", alpha=0.5)
ax.streamplot(X, Y, Vx, Vy, color="white", density=1.2, linewidth=0.7)

ax.plot(x, y, 'k', linewidth=2)
ax.plot(x_cg, y_cg, 'ro', label="CG")
ax.set_aspect('equal')
ax.set_title(f"{selected_airfoil} at {aoa}° AoA")
ax.legend()
st.pyplot(fig)

