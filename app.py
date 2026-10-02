import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from pytrends.request import TrendReq

# ---------------------------------------------------------
# 1. Page Configuration & Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="Macro Stability & Market Demand Radar",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌐 Macro Societal Radar: Stability, Threat & Market Demand")
st.caption(
    "Predictive socio-economic engine tracking structural unrest risk "
    "and emerging consumer demands via World Bank macro-data and Google Trends signals."
)

# ---------------------------------------------------------
# 2. Geography Mapping (ISO-2 Codes)
# ---------------------------------------------------------
COUNTRIES = {
    "India": {"wb": "IN", "geo": "IN"},
    "United States": {"wb": "US", "geo": "US"},
    "United Kingdom": {"wb": "GB", "geo": "GB"},
    "Germany": {"wb": "DE", "geo": "DE"},
    "South Africa": {"wb": "ZA", "geo": "ZA"},
    "Brazil": {"wb": "BR", "geo": "BR"},
    "Kenya": {"wb": "KE", "geo": "KE"},
    "World Aggregate": {"wb": "WLD", "geo": ""}
}

st.sidebar.header("🕹️ Regional Parameter Controls")
selected_country = st.sidebar.selectbox("Select Target Nation", list(COUNTRIES.keys()), index=0)
country_meta = COUNTRIES[selected_country]

# ---------------------------------------------------------
# 3. Live World Bank Multi-Indicator Ingestion Engine
# ---------------------------------------------------------
INDICATOR_REGISTRY = {
    "Inflation (CPI %)": "FP.CPI.TOTL.ZG",
    "GDP Growth (Annual %)": "NY.GDP.MKTP.KD.ZG",
    "Youth Unemployment (% ages 15-24)": "SL.UEM.1524.ZS",
    "Total Unemployment (% of total labor force)": "SL.UEM.TOTL.ZS",
    "Food Production Index (2014-2016 = 100)": "AG.PRD.FOOD.XD"
}

@st.cache_data(ttl=86400)  # Cached for 24 hours to ensure high speed
def fetch_world_bank_series(country_iso, indicator_code, num_years=12):
    """Fetches clean longitudinal observations from the World Bank API."""
    url = f"https://api.worldbank.org/v2/country/{country_iso}/indicator/{indicator_code}?format=json&mrv={num_years}"
    try:
        res = requests.get(url, timeout=12)
        payload = res.json()
        if len(payload) > 1 and payload[1]:
            records = [
                {"Year": int(row["date"]), "Value": float(row["value"])}
                for row in payload[1]
                if row["value"] is not None
            ]
            df = pd.DataFrame(records)
            return df.sort_values("Year", ascending=True)
        return pd.DataFrame(columns=["Year", "Value"])
    except Exception:
        return pd.DataFrame(columns=["Year", "Value"])

# Ingest all indicators
with st.spinner(f"Ingesting live macro-series for {selected_country}..."):
    macro_datasets = {}
    for label, code in INDICATOR_REGISTRY.items():
        macro_datasets[label] = fetch_world_bank_series(country_meta["wb"], code)

# ---------------------------------------------------------
# 4. Live High-Frequency Digital Sentiment (Google Trends)
# ---------------------------------------------------------
@st.cache_data(ttl=7200)  # 2-hour cache for search signals
def fetch_societal_search_velocity(geo_code):
    """Pulls search trend velocities for anxiety and economic search terms."""
    if not geo_code:
        return pd.DataFrame()
    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        keywords = ["stress", "layoff", "debt", "cheap food"]
        pytrends.build_payload(keywords, timeframe="today 3-m", geo=geo_code)
        interest_df = pytrends.interest_over_time()
        if not interest_df.empty:
            return interest_df.drop(columns=["isPartial"], errors="ignore")
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

search_trends_df = fetch_societal_search_velocity(country_meta["geo"])

# ---------------------------------------------------------
# 5. Composite Societal Instability Index (CSII) Calculation
# ---------------------------------------------------------
# Extract most recent data points
def get_latest_metric(df):
    if not df.empty:
        return df.iloc[-1]["Value"], int(df.iloc[-1]["Year"])
    return 0.0, 0

latest_inf, year_inf = get_latest_metric(macro_datasets["Inflation (CPI %)"])
latest_gdp, _ = get_latest_metric(macro_datasets["GDP Growth (Annual %)"])
latest_youth_unemp, year_unemp = get_latest_metric(macro_datasets["Youth Unemployment (% ages 15-24)"])
latest_total_unemp, _ = get_latest_metric(macro_datasets["Total Unemployment (% of total labor force)"])
latest_food_idx, _ = get_latest_metric(macro_datasets["Food Production Index (2014-2016 = 100)"])

# Structural Risk Algorithm (Heuristic based on conflict research):
# Base = (Youth Unemployment * 1.5) + (Inflation * 1.2) - (GDP Growth * 0.8)
raw_risk_score = (latest_youth_unemp * 1.5) + (latest_inf * 1.2) - (latest_gdp * 0.8)
normalized_risk = max(5, min(95, int(raw_risk_score + 15)))

# ---------------------------------------------------------
# 6. Top Executive Overview KPI Cards
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Societal Friction Score",
        value=f"{normalized_risk}/100",
        delta="High Fragility" if normalized_risk > 50 else "Equilibrium",
        delta_color="inverse"
    )

with kpi2:
    st.metric(
        label=f"Youth Unemployment ({year_unemp})",
        value=f"{latest_youth_unemp:.1f}%",
        help="Primary statistical driver of social volatility and radicalization."
    )

with kpi3:
    st.metric(
        label=f"Consumer Inflation ({year_inf})",
        value=f"{latest_inf:.2f}%",
        help="Annual CPI growth - direct driver of real-wage contraction."
    )

with kpi4:
    st.metric(
        label="Real GDP Trajectory",
        value=f"{latest_gdp:.2f}%",
        help="Annual economic absorption capacity."
    )

st.divider()

# ---------------------------------------------------------
# 7. Multi-Domain Dashboard Views
# ---------------------------------------------------------
tab_radar, tab_charts, tab_opportunities = st.tabs([
    "🛡️ Societal Threat & Friction Analysis",
    "📈 Longitudinal Data Streams",
    "🛍️ Market Opportunities & Well-Being Solutions"
])

# TAB 1: THREAT & CONFLICT PREDICTION
with tab_radar:
    st.subheader(f"Predictive Threat Analysis: {selected_country}")
    
    col_threat_a, col_threat_b = st.columns([1.2, 1])
    
    with col_threat_a:
        st.markdown("#### Structural Conflict Vectors")
        
        threat_factors = []
        if latest_youth_unemp > 20.0:
            threat_factors.append(
                f"🔴 **Acute Youth Marginalization ({latest_youth_unemp:.1f}%):** "
                "Significant cohorts of educated or semi-skilled youth without labor absorption. "
                "Historical models identify this as the strongest baseline for organized civil unrest, "
                "vandalism, and political polarization."
            )
        if latest_inf > 7.0:
            threat_factors.append(
                f"🔴 **Purchasing Power Shock ({latest_inf:.1f}%):** "
                "Rapid basic necessity cost escalation. Triggers wildcat strikes, transport shutdowns, "
                "and consumer boycott movements."
            )
        if latest_gdp < 1.5:
            threat_factors.append(
                f"🟡 **Economic Stagnation Trap ({latest_gdp:.1f}%):** "
                "Limited fiscal flexibility and slow job creation."
            )
        
        if not threat_factors:
            st.success("✅ **No Extreme Structural Warnings Active:** All macro parameters remain within historically balanced operating bands.")
        else:
            for factor in threat_factors:
                st.write(factor)
                
        st.info(
            "**Intelligence Note:** Macro-structural indicators do not cause immediate violence on their own; "
            "they define societal vulnerability. A sudden political event, price hike, or scandal acts as the "
            "trigger within high-friction environments."
        )

    with col_threat_b:
        # Radar Chart of Pressure Points
        radar_df = pd.DataFrame({
            "Pillar": ["Youth Friction", "Inflation Strain", "Labor Dislocation", "Growth Deficit", "Food Stability Risk"],
            "Intensity": [
                min(100, latest_youth_unemp * 3),
                min(100, latest_inf * 5),
                min(100, latest_total_unemp * 4),
                max(0, min(100, (6 - latest_gdp) * 15)),
                max(0, min(100, (120 - latest_food_idx) * 2)) if latest_food_idx > 0 else 30
            ]
        })
        fig_radar = px.line_polar(radar_df, r="Intensity", theta="Pillar", line_close=True, title="Societal Vulnerability Pentagon")
        fig_radar.update_traces(fill="toself", line_color="#EF4444" if normalized_risk > 50 else "#3B82F6")
        st.plotly_chart(fig_radar, use_container_width=True)

# TAB 2: LONGITUDINAL CHARTS
with tab_charts:
    st.subheader("Historical 12-Year Macro Trends (World Bank)")
    
    chart_row1_col1, chart_row1_col2 = st.columns(2)
    chart_row2_col1, chart_row2_col2 = st.columns(2)
    
    with chart_row1_col1:
        if not macro_datasets["Inflation (CPI %)"].empty:
            f1 = px.line(macro_datasets["Inflation (CPI %)"], x="Year", y="Value", title="Consumer Price Inflation (%)", markers=True)
            f1.update_traces(line_color="#E11D48")
            st.plotly_chart(f1, use_container_width=True)
            
    with chart_row1_col2:
        if not macro_datasets["Youth Unemployment (% ages 15-24)"].empty:
            f2 = px.bar(macro_datasets["Youth Unemployment (% ages 15-24)"], x="Year", y="Value", title="Youth Unemployment Rate (%)")
            f2.update_traces(marker_color="#F59E0B")
            st.plotly_chart(f2, use_container_width=True)

    with chart_row2_col1:
        if not macro_datasets["GDP Growth (Annual %)"].empty:
            f3 = px.bar(macro_datasets["GDP Growth (Annual %)"], x="Year", y="Value", title="Annual GDP Growth Rate (%)")
            f3.update_traces(marker_color="#10B981")
            st.plotly_chart(f3, use_container_width=True)
            
    with chart_row2_col2:
        if not search_trends_df.empty:
            st.markdown("**Public Interest Trends (Last 90 Days - Google Trends)**")
            st.line_chart(search_trends_df)
        else:
            st.info("Google Trends search velocity not indexed for this selected territory.")

# TAB 3: MARKETING, PRODUCT & SERVICE DEMANDS
with tab_opportunities:
    st.subheader("Actionable Business, Service & Well-Being Recommendations")
    st.write("Using societal stress dynamics to design high-demand, high-impact products and interventions.")
    
    opp_col1, opp_col2 = st.columns(2)
    
    with opp_col1:
        st.markdown("### 🛒 Consumer Product & Service Directions")
        if latest_inf > 5.0 or latest_youth_unemp > 18.0:
            st.error(
                "**Market Dynamic: The Value-First & Micro-Income Shift**\n\n"
                "- **High-Demand Product Profiles:**\n"
                "  1. **Essential Micro-Sachet / Bulk Sharing:** Smaller pack sizes or neighborhood pooling tools to lower ticket costs.\n"
                "  2. **Alternative Protein & Staple Swaps:** Products that replace expensive staples with nutritious, affordable alternatives.\n"
                "  3. **Gig & Secondary Skill Monetization:** Tools that help young adults generate immediate freelance income.\n"
                "- **Messaging Strategy:** Direct, functional, transparent; avoid luxury elitism."
            )
        else:
            st.success(
                "**Market Dynamic: Premium Convenience & Self-Optimization**\n\n"
                "- **High-Demand Product Profiles:**\n"
                "  1. **Cognitive & Physical Health Upgrades:** Specialized nutrition, ergonomic setups, preventive screening.\n"
                "  2. **Automated Efficiency:** Time-saving meal kits, smart home routines, personal financial planners.\n"
                "- **Messaging Strategy:** Focus on self-actualization, long-term health, and quality of life."
            )

    with opp_col2:
        st.markdown("### 🧘 Societal Well-Being & Mental Health Solutions")
        if normalized_risk > 50:
            st.warning(
                "**Societal Friction State: High Collective Anxiety**\n\n"
                "- **Service Interventions Needed:**\n"
                "  1. **Low-Cost / Free Emotional First Aid:** Tele-counseling hotlines, community group therapy circles.\n"
                "  2. **Physical Stress-Release Outlets:** Free community sports programs, group running clubs, public recreation events.\n"
                "  3. **Financial De-Stigmatization Content:** Educational workshops on handling debt and building emergency cushions."
            )
        else:
            st.info(
                "**Societal Friction State: Baseline Equilibrium**\n\n"
                "- **Service Interventions Needed:**\n"
                "  1. **Longevity & Habit Building:** Structured fitness communities, holistic mental hygiene habits.\n"
                "  2. **Social Cohesion Initiatives:** Cultural festivals, localized creative workshops, mentorship ecosystems."
            )
