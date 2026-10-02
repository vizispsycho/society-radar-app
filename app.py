import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="World Bank Macro & Stability Radar", layout="wide")

st.title("🌐 World Bank Macro Radar: Societal Stress & Market Signals")
st.caption("Live open-source economic indicators transformed into stability risk and service opportunities.")

# 2. Country Selector Mapping (Country Name -> ISO-2 Code)
COUNTRIES = {
    "United States": "US",
    "India": "IN",
    "United Kingdom": "GB",
    "Germany": "DE",
    "Brazil": "BR",
    "South Africa": "ZA",
    "Japan": "JP",
    "World Average": "WLD"
}

st.sidebar.header("Geography & Settings")
selected_country_name = st.sidebar.selectbox("Select Country / Region", list(COUNTRIES.keys()), index=1)
country_code = COUNTRIES[selected_country_name]

# 3. Cached Data Fetcher from World Bank API
@st.cache_data(ttl=3600)  # Caches data for 1 hour so the app stays fast
def fetch_world_bank_indicator(country_iso, indicator_code):
    """
    World Bank API Endpoint:
    Returns the last 15 recorded annual observations for an indicator.
    """
    url = f"https://api.worldbank.org/v2/country/{country_iso}/indicator/{indicator_code}?format=json&mrv=15"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # World Bank API returns a list where index [1] contains the actual records
        if len(data) > 1 and data[1]:
            records = [
                {"Year": int(item["date"]), "Value": item["value"]}
                for item in data[1]
                if item["value"] is not None
            ]
            df = pd.DataFrame(records)
            return df.sort_values("Year", ascending=True)
        return pd.DataFrame(columns=["Year", "Value"])
    except Exception as e:
        st.error(f"Error fetching indicator: {e}")
        return pd.DataFrame(columns=["Year", "Value"])

# Indicator Codes from World Bank:
# FP.CPI.TOTL.ZG = Inflation, consumer prices (annual %)
# NY.GDP.MKTP.KD.ZG = GDP growth (annual %)
with st.spinner(f"Fetching live World Bank data for {selected_country_name}..."):
    inflation_df = fetch_world_bank_indicator(country_code, "FP.CPI.TOTL.ZG")
    gdp_df = fetch_world_bank_indicator(country_code, "NY.GDP.MKTP.KD.ZG")

# 4. Metric Processing
if not inflation_df.empty:
    latest_inflation = inflation_df.iloc[-1]["Value"]
    latest_year = inflation_df.iloc[-1]["Year"]
    prev_inflation = inflation_df.iloc[-2]["Value"] if len(inflation_df) > 1 else latest_inflation
    inflation_delta = round(latest_inflation - prev_inflation, 2)
else:
    latest_inflation, latest_year, inflation_delta = 0.0, "N/A", 0.0

if not gdp_df.empty:
    latest_gdp = gdp_df.iloc[-1]["Value"]
    prev_gdp = gdp_df.iloc[-2]["Value"] if len(gdp_df) > 1 else latest_gdp
    gdp_delta = round(latest_gdp - prev_gdp, 2)
else:
    latest_gdp, gdp_delta = 0.0, 0.0

# 5. Top Overview Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"Inflation Rate ({latest_year})",
        value=f"{latest_inflation:.2f}%",
        delta=f"{inflation_delta:+.2f}% YoY",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label=f"GDP Growth ({latest_year})",
        value=f"{latest_gdp:.2f}%",
        delta=f"{gdp_delta:+.2f}% YoY",
        delta_color="normal"
    )

with col3:
    # Calculating Societal Economic Strain Index (Inflation vs Growth)
    strain_score = max(0, min(100, int((latest_inflation * 6) - (latest_gdp * 3) + 20)))
    status = "Elevated Strain" if strain_score > 50 else "Balanced / Low Stress"
    st.metric(label="Calculated Economic Strain Index", value=f"{strain_score}/100", delta=status)

st.divider()

# 6. Interactive Analysis Tabs
tab1, tab2 = st.tabs(["📊 Live Economic Dynamics", "💡 Societal Risk & Market Demands"])

with tab1:
    st.subheader(f"Historical Economic Volatility: {selected_country_name}")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if not inflation_df.empty:
            fig_inf = px.line(
                inflation_df, x="Year", y="Value",
                title="Consumer Inflation Rate (Annual %)",
                markers=True, line_shape="spline",
                labels={"Value": "Inflation (%)", "Year": "Year"}
            )
            fig_inf.update_traces(line_color="#EF4444")
            st.plotly_chart(fig_inf, use_container_width=True)
        else:
            st.warning("No inflation data available.")

    with chart_col2:
        if not gdp_df.empty:
            fig_gdp = px.bar(
                gdp_df, x="Year", y="Value",
                title="Annual GDP Growth Rate (%)",
                labels={"Value": "Growth (%)", "Year": "Year"}
            )
            fig_gdp.update_traces(marker_color="#3B82F6")
            st.plotly_chart(fig_gdp, use_container_width=True)
        else:
            st.warning("No GDP growth data available.")

with tab2:
    st.subheader("Societal Stress & Market Opportunity Engine")
    
    risk_col, opp_col = st.columns(2)
    
    with risk_col:
        st.markdown("### 🛡️ Societal Stability Assessment")
        if latest_inflation > 6.0:
            st.error(
                f"**High Discontent Alert:** High annual inflation ({latest_inflation:.2f}%) "
                "rapidly outpaces baseline real wages. Historical patterns show this environment "
                "correlates with higher propensity for strikes, organized labor friction, and price protests."
            )
        elif latest_gdp < 1.0:
            st.warning(
                f"**Economic Stagnation Risk:** Weak output growth ({latest_gdp:.2f}%) "
                "drives youth underemployment and increases vulnerability to political radicalization."
            )
        else:
            st.success(
                "**Stable Societal Equilibrium:** Macro parameters indicate healthy purchasing power "
                "and steady economic absorption, minimizing collective unrest triggers."
            )

    with opp_col:
        st.markdown("### 🛍️ Emerging Product & Service Demands")
        if latest_inflation > 5.0:
            st.info(
                "**Target: Budget Optimization & Friction Relief**\n\n"
                "- **High-Demand Concepts:** White-label staple distribution, micro-financing tools, bulk neighborhood grocery sharing apps.\n"
                "- **Messaging:** Emphasize security, transparent pricing, and cost predictability."
            )
        else:
            st.info(
                "**Target: Expansion & Wellness**\n\n"
                "- **High-Demand Concepts:** Preventive health services, career upskilling platforms, and lifestyle micro-upgrades.\n"
                "- **Messaging:** Focus on self-improvement, longevity, and convenience."
            )
