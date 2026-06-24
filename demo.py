import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 字体基础配置（仅兼容数字英文，无需中文渲染）
plt.rcParams['axes.unicode_minus'] = False

# ===================== 常量与工具函数 =====================
FIG_WIDTH = 11
FIG_HEIGHT = 5.5
SAMPLE_NUM = 300
COLOR_THROW = "#2ca02c"    # Launch point green
COLOR_RANGE = "#d62728"    # Landing point red
COLOR_VX = "#1f77b4"       # Horizontal velocity blue
COLOR_VY = "#ff7f0e"       # Vertical velocity orange
COLOR_VSUM = "#9467bd"     # Resultant velocity purple

@st.cache_data
def calc_projectile(v0, h, g, t):
    """Calculate physical quantities at a single moment of projectile motion"""
    x = v0 * t
    y = h - 0.5 * g * t ** 2
    vx = v0
    vy = g * t
    v_sum = np.sqrt(vx**2 + vy**2)
    theta = np.arctan2(vy, vx) * 180 / np.pi
    return x, y, vx, vy, v_sum, theta


@st.cache_data
def get_full_trajectory(v0, h, g):
    """Calculate all coordinates of the complete trajectory"""
    t_total = np.sqrt(2 * h / g)
    t_arr = np.linspace(0, t_total, SAMPLE_NUM)
    x_arr = v0 * t_arr
    y_arr = h - 0.5 * g * t_arr ** 2
    return t_total, t_arr, x_arr, y_arr

# ===================== Page Basic Config =====================
st.set_page_config(page_title="Projectile Motion Simulation | College Physics", layout="wide")
st.title("📐 Interactive Projectile Motion Simulation Platform")
st.markdown(r"""
### Core Decomposition Formulas of Projectile Motion
Horizontal uniform motion: $x = v_0 t,\quad v_x = v_0$
Vertical free fall: $y = h - \dfrac12 g t^2,\quad v_y = g t$
""")

# ===================== Sidebar Control Panel =====================
with st.sidebar:
    st.header("⚙️ Physical Parameter Settings")
    v0 = st.slider("Initial velocity v₀ (m/s)", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
    h = st.slider("Launch height h (m)", min_value=1.0, max_value=50.0, value=10.0, step=0.5)
    g = st.slider("Gravitational acceleration g (m/s²)", min_value=1.0, max_value=20.0, value=9.8, step=0.2)
    
    st.divider()
    st.header("🎛️ Demo Controls")
    use_drag = st.checkbox("Enable time slider to observe velocity vectors", value=True)
    show_multi = st.checkbox("Compare second trajectory (multiple initial velocity comparison)", value=False)
    air_resist = st.checkbox("Add linear air resistance (Extended thinking question)", value=False)
    
    if show_multi:
        v0_2 = st.slider("Comparison group initial velocity", min_value=1.0, max_value=30.0, value=15.0)
    
    st.divider()
    st.info("Tips:\n1. Larger initial velocity leads to longer horizontal range\n2. Higher launch height extends landing time\n3. Larger g accelerates falling speed")

# ===================== Basic Trajectory Calculation =====================
t_total, t_list, x, y = get_full_trajectory(v0, h, g)
x_max = v0 * t_total

# ===================== Plot Canvas =====================
fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
# Ground line
ax.axhline(y=0, color="black", linewidth=1.5, label="Ground y=0")
# Main trajectory
ax.plot(x, y, color="#1f77b4", linewidth=2.5, label=f"v₀={v0} m/s trajectory")
# Comparison trajectory
if show_multi:
    _, t2, x2, y2 = get_full_trajectory(v0_2, h, g)
    ax.plot(x2, y2, color="#ff7f0e", linewidth=2, linestyle="--", label=f"Compare v₀={v0_2} m/s")

# Mark launch & landing point
ax.scatter(x[0], y[0], color=COLOR_THROW, s=100, zorder=5, label="Launch point")
ax.scatter(x[-1], y[-1], color=COLOR_RANGE, s=100, zorder=5, label="Landing point")

# Adaptive axis range
ax.set_xlim(left=0, right=max(x_max, x_max*1.1))
ax.set_ylim(bottom=-1, top=h*1.1)

# Axis & title text (All English, no Chinese font issue)
ax.set_xlabel("Horizontal Displacement X (m)", fontsize=13)
ax.set_ylabel("Vertical Height Y (m)", fontsize=13)
ax.set_title("Complete Projectile Trajectory", fontsize=14, pad=10)
ax.grid(True, alpha=0.4, linestyle="-.")
ax.legend(fontsize=11)
plt.tight_layout()

# ===================== Time Slider & Velocity Vectors =====================
if use_drag:
    st.subheader("⏱️ Freeze any moment to analyze velocity")
    t_now = st.slider("Current motion time t (s)", min_value=0.0, max_value=float(t_total), value=t_total/2, step=t_total/200)
    x_t, y_t, vx_t, vy_t, v_t, theta_t = calc_projectile(v0, h, g, t_now)
    
    # Draw moving ball and velocity arrows
    ax.scatter(x_t, y_t, color="black", s=120, marker="o", zorder=6)
    ax.arrow(x_t, y_t, vx_t/2, 0, width=0.15, color=COLOR_VX, label="Horizontal vₓ")
    ax.arrow(x_t, y_t, 0, -vy_t/2, width=0.15, color=COLOR_VY, label="Vertical vᵧ")
    ax.arrow(x_t, y_t, vx_t/2, -vy_t/2, width=0.15, color=COLOR_VSUM, label="Resultant v")
    
    fig.canvas.draw()
    st.pyplot(fig)
    
    st.success(f"Current time t = {t_now:.2f} s")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Horizontal X", f"{x_t:.2f} m")
        st.metric("Horizontal vₓ", f"{vx_t:.2f} m/s")
    with col2:
        st.metric("Vertical Y", f"{y_t:.2f} m")
        st.metric("Vertical vᵧ", f"{vy_t:.2f} m/s")
    with col3:
        st.metric("Resultant Speed", f"{v_t:.2f} m/s")
        st.metric("Velocity Angle θ", f"{theta_t:.1f} °")
else:
    fig.canvas.draw()
    st.pyplot(fig)

# ===================== Landing Total Parameters =====================
st.divider()
st.subheader("📊 Total Motion Parameters On Landing")
vy_end = g * t_total
v_end = np.sqrt(v0**2 + vy_end**2)
theta_end = np.arctan2(vy_end, v0) * 180 / np.pi

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Flight Time", f"{t_total:.2f} s")
with c2:
    st.metric("Max Horizontal Range", f"{x_max:.2f} m")
with c3:
    st.metric("Vertical Speed On Landing", f"{vy_end:.2f} m/s")
with c4:
    st.metric("Resultant Speed On Landing", f"{v_end:.2f} m/s")
st.write(f"Angle between landing velocity and horizontal axis: θ = {theta_end:.1f} °")

# ===================== Extended Questions =====================
if air_resist:
    st.warning("Extended Question: How will air resistance affect range and landing speed? Is the trajectory still a parabola?")
st.divider()
st.markdown("### Class Discussion Questions")
st.markdown("""
1. At the same height, if initial velocity doubles, how will horizontal range change?
2. Initial velocity unchanged, launch height increased 4 times, how many times longer is flight time?
3. On the Moon g≈1.63 m/s², with same initial velocity & height, is the range larger than on Earth?
""")