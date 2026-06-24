import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ========== 修复云端Linux中文乱码核心配置（优先级调整） ==========
# 优先使用Streamlit云端预装的文泉驿微米黑，本地Windows兼容兜底
plt.rcParams['font.sans-serif'] = [
    'WenQuanYi Micro Hei',
    'SimHei',
    'Microsoft YaHei',
    'Heiti TC',
    'DejaVu Sans'
]
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'

# ===================== 常量与工具函数（代码规范化） =====================
FIG_WIDTH = 11
FIG_HEIGHT = 5.5
SAMPLE_NUM = 300  # 轨迹采样点数
COLOR_THROW = "#2ca02c"    # 抛出点绿色
COLOR_RANGE = "#d62728"    # 落地点红色
COLOR_VX = "#1f77b4"       # 水平分速度蓝色
COLOR_VY = "#ff7f0e"       # 竖直分速度橙色
COLOR_VSUM = "#9467bd"     # 合速度紫色

@st.cache_data
def calc_projectile(v0, h, g, t):
    """封装平抛运动单时刻物理量计算，缓存加速"""
    x = v0 * t
    y = h - 0.5 * g * t ** 2
    vx = v0
    vy = g * t
    v_sum = np.sqrt(vx**2 + vy**2)
    theta = np.arctan2(vy, vx) * 180 / np.pi  # 速度偏角 角度制
    return x, y, vx, vy, v_sum, theta


@st.cache_data
def get_full_trajectory(v0, h, g):
    """计算完整轨迹全部坐标"""
    t_total = np.sqrt(2 * h / g)
    t_arr = np.linspace(0, t_total, SAMPLE_NUM)
    x_arr = v0 * t_arr
    y_arr = h - 0.5 * g * t_arr ** 2
    return t_total, t_arr, x_arr, y_arr

# ===================== 页面基础配置 =====================
st.set_page_config(page_title="平抛运动仿真｜大学物理演示", layout="wide")
st.title("📐 大学物理交互式平抛运动仿真平台")
st.markdown(r"""
### 平抛运动核心分解公式
水平匀速：$x = v_0 t,\quad v_x = v_0$
竖直自由下落：$y = h - \dfrac12 g t^2,\quad v_y = g t$
""")

# ===================== 侧边栏交互面板 =====================
with st.sidebar:
    st.header("⚙️ 物理参数调节")
    v0 = st.slider("初速度 v₀ (m/s)", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
    h = st.slider("抛出高度 h (m)", min_value=1.0, max_value=50.0, value=10.0, step=0.5)
    g = st.slider("重力加速度 g (m/s²)", min_value=1.0, max_value=20.0, value=9.8, step=0.2)
    
    st.divider()
    st.header("🎛️ 演示控制")
    use_drag = st.checkbox("开启时间滑块，动态观察速度矢量", value=True)
    show_multi = st.checkbox("对比第二组轨迹（多初速度对照）", value=False)
    air_resist = st.checkbox("引入线性空气阻力（拓展思考题）", value=False)
    
    if show_multi:
        v0_2 = st.slider("对比组初速度", min_value=1.0, max_value=30.0, value=15.0)
    
    st.divider()
    st.info("教学提示：\n1. 增大初速度，水平射程变大\n2. 高度越高，落地时间越长\n3. g越大，下落越快")

# ===================== 基础轨迹计算 =====================
t_total, t_list, x, y = get_full_trajectory(v0, h, g)
x_max = v0 * t_total

# ===================== 绘图画布 =====================
fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
# 绘制地面
ax.axhline(y=0, color="black", linewidth=1.5, label="地面 y=0")
# 主轨迹
ax.plot(x, y, color="#1f77b4", linewidth=2.5, label=f"v₀={v0} m/s 轨迹")
# 多轨迹对比
if show_multi:
    _, t2, x2, y2 = get_full_trajectory(v0_2, h, g)
    ax.plot(x2, y2, color="#ff7f0e", linewidth=2, linestyle="--", label=f"对比 v₀={v0_2} m/s")

# 标记抛出点、落地点
ax.scatter(x[0], y[0], color=COLOR_THROW, s=100, zorder=5, label="抛出点")
ax.scatter(x[-1], y[-1], color=COLOR_RANGE, s=100, zorder=5, label="落地点")

# 自适应坐标轴
ax.set_xlim(left=0, right=max(x_max, x_max*1.1))
ax.set_ylim(bottom=-1, top=h*1.1)

# 图像美化（投影清晰化）
ax.set_xlabel("水平位移 X (m)", fontsize=13)
ax.set_ylabel("竖直高度 Y (m)", fontsize=13)
ax.set_title("平抛运动完整轨迹", fontsize=14, pad=10)
ax.grid(True, alpha=0.4, linestyle="-.")
ax.legend(fontsize=11)
plt.tight_layout()

# ===================== 动态时间滑块与速度矢量 =====================
if use_drag:
    st.subheader("⏱️ 定格任意时刻分析速度")
    t_now = st.slider("当前运动时刻 t (s)", min_value=0.0, max_value=float(t_total), value=t_total/2, step=t_total/200)
    x_t, y_t, vx_t, vy_t, v_t, theta_t = calc_projectile(v0, h, g, t_now)
    
    # 在图上绘制当前小球与速度箭头
    ax.scatter(x_t, y_t, color="black", s=120, marker="o", zorder=6)
    # 分速度矢量
    ax.arrow(x_t, y_t, vx_t/2, 0, width=0.15, color=COLOR_VX, label="水平分速度 vₓ")
    ax.arrow(x_t, y_t, 0, -vy_t/2, width=0.15, color=COLOR_VY, label="竖直分速度 vᵧ")
    ax.arrow(x_t, y_t, vx_t/2, -vy_t/2, width=0.15, color=COLOR_VSUM, label="合速度 v")
    
    # 强制刷新画布字体缓存，解决云端中文不渲染
    fig.canvas.draw()
    st.pyplot(fig)
    
    # 实时瞬时数据
    st.success(f"当前时刻 t = {t_now:.2f} s")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("水平坐标 X", f"{x_t:.2f} m")
        st.metric("水平分速度 vₓ", f"{vx_t:.2f} m/s")
    with col2:
        st.metric("竖直坐标 Y", f"{y_t:.2f} m")
        st.metric("竖直分速度 vᵧ", f"{vy_t:.2f} m/s")
    with col3:
        st.metric("合速度大小", f"{v_t:.2f} m/s")
        st.metric("速度俯角 θ", f"{theta_t:.1f} °")
else:
    # 无滑块时同样刷新画布
    fig.canvas.draw()
    st.pyplot(fig)

# ===================== 落地总结果面板 =====================
st.divider()
st.subheader("📊 落地总运动参数")
vy_end = g * t_total
v_end = np.sqrt(v0**2 + vy_end**2)
theta_end = np.arctan2(vy_end, v0) * 180 / np.pi

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("总落地时间", f"{t_total:.2f} s")
with c2:
    st.metric("最大水平射程", f"{x_max:.2f} m")
with c3:
    st.metric("落地竖直分速度", f"{vy_end:.2f} m/s")
with c4:
    st.metric("落地合速度", f"{v_end:.2f} m/s")
st.write(f"落地速度与水平方向夹角：θ = {theta_end:.1f} °")

# ===================== 拓展思考题（课堂作业） =====================
if air_resist:
    st.warning("拓展思考：空气阻力会使射程、落地速度如何变化？轨迹还是抛物线吗？")
st.divider()
st.markdown("### 课堂思考问题")
st.markdown("""
1. 同一高度下，初速度加倍，水平射程如何变化？
2. 初速度不变，抛出高度提升4倍，落地时间变为原来几倍？
3. 月球上g≈1.63 m/s²，相同初速度高度，平抛射程和地球相比更大还是更小？
""")