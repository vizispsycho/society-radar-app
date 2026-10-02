import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.set_page_config(page_title="Global Social & Market Radar", layout="wide")

st.title("🌐 Global Social Radar & Market Opportunity Engine")
st.caption("Tracking macro societal stress, collective stability, and emerging service demands.")

# 1. Sidebar Controls
st.sidebar.header("Filter & Controls")
region = st.sidebar.selectbox("Select Region", ["Global", "North America", "South Asia", "Europe", "Latin America"])
risk_threshold = st.sidebar.slider("Instability Sensitivity", min_value=1, max_value=10, value=6)

# 2. Simulated Macro Indicators (Replaceable by automated API pipelines)
data = {
    "Domain": ["Economic Friction", "Polarization / Discourse", "Health & Well-being", "Resource Access", "Digital Sentiment"],
    "Stress_Index": [random.randint(40, 85), random.randint(30, 90), random.randint(20, 75), random.randint(15, 60), random.randint(35, 80)],
    "Trend_Velocity": ["+12%", "+5%", "-3%", "+8%", "+15%"]
}
df = pd.DataFrame(data)

# 3. Main Dashboard Layout
col1, col2, col3 = st.columns(3)
composite_risk = int(df["Stress_Index"].mean())

with col1:
    st.metric("Composite Volatility Score", f"{composite_risk}/100", delta="+4% this week", delta_color="inverse")
with col2:
    status = "Elevated Caution" if composite_risk > 50 else "Stable Baseline"
    st.metric("Stability State", status)
with col3:
    st.metric("Primary Demand Vector", "Mental Resilience & Essentials")

st.divider()

# 4. Two Primary Tabs: Security/Unrest vs Marketing/Product Needs
tab1, tab2 = st.tabs(["🛡️ Societal Stability & Group Risk", "🛍️ Market Demands & Well-Being Opportunities"])

with tab1:
    st.subheader("Societal Stress Trajectory")
    st.write("Aggregated tension metrics across public sentiment and structural indicators.")
    
    fig = px.bar(df, x="Domain", y="Stress_Index", color="Stress_Index", 
                 color_continuous_scale="Reds" if composite_risk > 50 else "Blues",
                 title=f"Current Societal Stress Pressure Points ({region})")
    st.plotly_chart(fig, use_container_width=True)
    
    if composite_risk > 55:
        st.warning("⚠️ High social friction detected. Collective unrest likelihood increases in urban hubs over 30-day horizon.")
    else:
        st.success("✅ Macro stability metrics remain within manageable equilibrium.")

with tab2:
    st.subheader("Actionable Product & Service Opportunities")
    st.write("Translating societal friction into ethical, high-need market services.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("### 1. Essential Resource Optimization\n"
                "- **Trend Signal:** High search activity around budget staples.\n"
                "- **Opportunity:** Community bulk-buying platforms, localized discount alerts.\n"
                "- **Impact Target:** Lowers household anxiety and immediate living friction.")
    with col_b:
        st.info("### 2. Psychological & Well-Being Support\n"
                "- **Trend Signal:** Rising burnout and anxiety language in public forums.\n"
                "- **Opportunity:** Low-cost group therapy apps, workplace calm spaces, sleep optimization products.\n"
                "- **Impact Target:** Directly counteracts societal agitation.")
