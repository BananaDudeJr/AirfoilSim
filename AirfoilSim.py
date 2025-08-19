import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# === NACA generator ===
def naca4(m, p, t, c=1, n=200):
    x = np.linspace(0, c, n)
    yt = 5*t*c*(0.2969*np.sqrt(x/c) - 0.1260*(x/c) - 0.3516*(x/c)**2 
                 + 0.2843*(x/c)**3 - 0.1015*(x/c)**4)
    yc = np.where(x < p*c, m/p**2*(2*p*(x/c)-(x/c)**2),
                            m/(1-p)**2*((1-2*p)+2*p*(x/c)-(x/c)**2))
    dyc_dx = np.where(x < p*c, 2*m/p**2*(p-(x/c)),
                                   2*m/(1-p)**2*(p-(x/c)))
    theta = np.arctan(dyc_dx)
    xu = x - yt*np.sin(theta)
    yu = yc + yt*np.cos(theta)
    xl = x + yt*np.sin(theta)
    yl = yc - yt*np.cos(theta)
    return np.concatenate([xu, xl[::-1]]), np.concatenate([yu, yl[::-1]])

# === Rotate points ===
def rotate(x, y, alpha_deg):
    alpha = np.radians(alpha_deg)
    x_r = x*np.cos(alpha) - y*np.sin(alpha)
    y_r = x*np.sin(alpha) + y*np.cos(alpha)
    return x_r, y_r

# === UI ===
st.title("Airfoil Flow Simulator")

airfoil_choice = st.selectbox("Choose Airfoil", ["NACA 2412", "NACA 4412", "NACA 0012", "NACA 4415"])
aoa = st.slider("Angle of Attack (°)", -10, 15, 5)
U = st.slider("Freestream Speed", 10, 100, 30)
cg_choice = st.radio("Center of Gravity Position", ["Front", "Middle", "Back"])

# === Airfoil Shape ===
if airfoil_choice.startswith("NACA"):
    digits = airfoil_choice.split()[1]
    m, p, t = int(digits[0])/100, int(digits[1])/10, int(digits[2:])/100
    x, y = naca4(m, p, t)
else:
    st.error("Non-NACA airfoils need .dat loader")
    x, y = [0,1], [0,0]

# Rotate for AoA
x, y = rotate(x, y, aoa)

# === Flow field ===
X, Y = np.meshgrid(np.linspace(-1, 2, 200), np.linspace(-1, 1, 150))
Vx = U * np.ones_like(X)
Vy = -0.5*U*np.exp(-20*((X-0.5)**2 + Y**2))
pressure = np.exp(-20*((X-0.5)**2 + Y**2))

# === Plot ===
fig, ax = plt.subplots(figsize=(8,4))
ax.contourf(X, Y, pressure, levels=30, cmap="RdBu_r", alpha=0.7)
ax.streamplot(X, Y, Vx, Vy, color="white", density=2, linewidth=0.8)

ax.plot(x, y, "k", linewidth=2)

# CG marker
if cg_choice == "Front":
    ax.plot(x.min()+0.1, 0, "ro", label="CG")
elif cg_choice == "Middle":
    ax.plot(0.5, 0, "ro", label="CG")
else:
    ax.plot(x.max()-0.1, 0, "ro", label="CG")

ax.set_aspect("equal")
ax.set_title(f"{airfoil_choice} at {aoa}°")
ax.legend()
st.pyplot(fig)
