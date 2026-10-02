import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from pytrends.request import TrendReq
import io

# ---------------------------------------------------------
# 1. UI Configuration & Branding
# ---------------------------------------------------------
st.set_page_config(
    page_title="NEXUS | Societal & Market Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Logo (Sidebar & Navigation)
st.logo(
    image="https://cdn-icons-png.flaticon.com/512/2099/2099149.png",
    icon_image="https://cdn-icons-png.flaticon.com/512/2099/2099149.png"
)

# Header Banner
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    padding: 22px;
    border-radius: 12px;
    border: 1px solid #334155;
    margin-bottom: 24px;
">
    <div style="display: flex; align-items: center; gap: 16px;">
        <span style="font-size: 40px;">🌐</span>
        <div>
            <h1 style="color: #F8FAFC; margin: 0; font-size: 26px; font-weight: 700;">
                NEXUS Macro & Societal Intelligence
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 13px;">
                Autonomous Socio-Economic Friction Forecasting & Strategic Market Demand Mapping
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Geography Registry
# ---------------------------------------------------------
COUNTRIES = {
    "India": {"wb": "IN", "geo": "IN"},
    "United States": {"wb": "US", "geo": "US"},
    "United Kingdom": {"wb": "GB", "geo": "GB"},
    "Germany": {"wb": "DE", "geo": "DE"},
    "South Africa": {"wb": "ZA", "geo": "ZA"},
    "Brazil": {"wb": "BR", "geo": "BR"},
    "Japan": {"wb": "JP", "geo": "JP"},
    "Global Aggregate": {"wb": "WLD", "geo": ""}
}

# Sidebar Live Status & Controls
st.sidebar.markdown("""
<div style="
    display: inline-block;
    background-color: #064E3B;
    color: #6EE7B7;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 14px;
">
    ● LIVE PIPELINE ACTIVE
</div>
""", unsafe_allow_html=True)

st.sidebar.header("Geography & Settings")
selected_country = st.sidebar.selectbox("Select Target Nation", list(COUNTRIES.keys()), index=0)
country_meta = COUNTRIES[selected_country]

# ---------------------------------------------------------
# 3. Live Data Ingestion Engine (World Bank API)
# ---------------------------------------------------------
INDICATOR_REGISTRY = {
    "Inflation (CPI %)": "FP.CPI.TOTL.ZG",
    "GDP Growth (Annual %)": "NY.GDP.MKTP.KD.ZG",
    "Youth Unemployment (%)": "SL.UEM.1524.ZS",
    "Suicide Mortality (per 100k)": "SH.STA.SUIC.P5",
    "Youth NEET (%)": "SL.UEM.NEET.ZS",
    "Alcohol Consumption (L/capita)": "SH.ALC.PCAP.LI",
    "Household Consumption (% GDP)": "NE.CON.PRVT.ZS",
    "Internet Adoption (% pop)": "IT.NET.USER.ZS",
    "Mobile Cellular Subscriptions (per 100)": "IT.CEL.SETS.P2"
}

@st.cache_data(ttl=86400)
def fetch_world_bank_series(country_iso, indicator_code, num_records=12):
    """Fetches longitudinal time-series data from the World Bank open API."""
    url = f"https://api.worldbank.org/v2/country/{country_iso}/indicator/{indicator_code}?format=json&mrv={num_records}"
    try:
        res = requests.get(url, timeout=10)
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

with st.spinner(f"Ingesting live macro-series for {selected_country}..."):
    datasets = {}
    for name, code in INDICATOR_REGISTRY.items():
        datasets[name] = fetch_world_bank_series(country_meta["wb"], code)

# ---------------------------------------------------------
# 4. Live Digital Intent Signals (Google Trends)
# ---------------------------------------------------------
@st.cache_data(ttl=7200)
def fetch_consumer_intent_trends(geo_code):
    """Fetches recent 90-day search velocity for economic and mental strain."""
    if not geo_code:
        return pd.DataFrame()
    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        keywords = ["discount", "layoff", "debt", "anxiety"]
        pytrends.build_payload(keywords, timeframe="today 3-m", geo=geo_code)
        df = pytrends.interest_over_time()
        if not df.empty:
            return df.drop(columns=["isPartial"], errors="ignore")
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

consumer_trends_df = fetch_consumer_intent_trends(country_meta["geo"])

# ---------------------------------------------------------
# 5. Core Metric Extraction & Risk Scoring
# ---------------------------------------------------------
def get_latest(df, default=0.0):
    if not df.empty:
        return float(df.iloc[-1]["Value"]), int(df.iloc[-1]["Year"])
    return default, 0

latest_inf, year_inf = get_latest(datasets["Inflation (CPI %)"])
latest_gdp, _ = get_latest(datasets["GDP Growth (Annual %)"])
latest_youth_unemp, year_unemp = get_latest(datasets["Youth Unemployment (%)"])
latest_suicide, _ = get_latest(datasets["Suicide Mortality (per 100k)"], default=9.5)
latest_neet, _ = get_latest(datasets["Youth NEET (%)"], default=16.0)
latest_alc, _ = get_latest(datasets["Alcohol Consumption (L/capita)"], default=4.0)
latest_hcon, _ = get_latest(datasets["Household Consumption (% GDP)"], default=58.0)
latest_net, _ = get_latest(datasets["Internet Adoption (% pop)"], default=70.0)
latest_mobile, _ = get_latest(datasets["Mobile Cellular Subscriptions (per 100)"], default=95.0)

# 1. Collective Societal Friction (Unrest / Stability Risk)
friction_raw = (latest_youth_unemp * 1.3) + (latest_inf * 1.1) + (latest_neet * 0.8) - (latest_gdp * 0.7)
friction_score = max(5, min(95, int(friction_raw + 15)))

# 2. Psychosocial Strain Score
psych_raw = (latest_suicide * 2.2) + (latest_neet * 1.5) + (latest_alc * 3.0)
psych_score = max(5, min(95, int(psych_raw)))

# 3. Consumer Spending Sentiment Score (0 = High Defense, 100 = Expansion)
consumer_sentiment = max(10, min(95, int(50 + (latest_gdp * 4) + (latest_hcon * 0.3) - (latest_inf * 5))))

# Recommended Channel Allocation
digital_share = int(min(90, max(20, latest_net)))
offline_share = 100 - digital_share

# ---------------------------------------------------------
# 6. Top Executive Overview KPI Cards
# ---------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        label="Societal Friction Index",
        value=f"{friction_score}/100",
        delta="Elevated Fragility" if friction_score > 55 else "Equilibrium",
        delta_color="inverse"
    )

with k2:
    st.metric(
        label="Psychosocial Strain Index",
        value=f"{psych_score}/100",
        delta="Severe Distress" if psych_score > 60 else "Manageable",
        delta_color="inverse"
    )

with k3:
    st.metric(
        label="Consumer Sentiment Score",
        value=f"{consumer_sentiment}/100",
        delta="Defensive Budgeting" if consumer_sentiment < 45 else "Expansive",
        delta_color="normal"
    )

with k4:
    st.metric(
        label=f"Youth Disconnection (NEET)",
        value=f"{latest_neet:.1f}%",
        help="Young cohort not in education, employment, or training."
    )

st.divider()

# ---------------------------------------------------------
# 7. Multi-Domain Navigation Tabs
# ---------------------------------------------------------
tab_threat, tab_marketing, tab_charts = st.tabs([
    "🛡️ Societal Threat & Friction Analysis",
    "🎯 Precision Marketing & Service Opportunities",
    "📈 Longitudinal Data & Intent Streams"
])

# TAB 1: STABILITY & CONFLICT PREDICTION
with tab_threat:
    st.subheader(f"Predictive Threat Analysis: {selected_country}")
    t_col1, t_col2 = st.columns([1.2, 1])
    
    with t_col1:
        st.markdown("#### Primary Structural Vulnerabilities")
        alerts = []
        if latest_youth_unemp > 20.0 or latest_neet > 20.0:
            alerts.append(f"🔴 **Youth Alienation Vector:** High youth unemployment ({latest_youth_unemp:.1f}%) and NEET rates ({latest_neet:.1f}%) indicate a disenfranchised cohort vulnerable to social unrest and extremist mobilization.")
        if latest_inf > 6.0:
            alerts.append(f"🔴 **Purchasing Power Shock:** CPI inflation ({latest_inf:.2f}%) reduces disposable liquidity, accelerating protests around transport, fuel, and food costs.")
        if latest_suicide > 13.0:
            alerts.append(f"🟡 **Elevated Despair Mortality:** Age-standardized suicide ({latest_suicide:.1f}/100k) signals gaps in social support infrastructure.")
        
        if not alerts:
            st.success("✅ Macro indicators show healthy social equilibrium with low baseline conflict triggers.")
        else:
            for alert in alerts:
                st.write(alert)

        st.info("**Analytical Note:** Macro indicators do not trigger immediate violence on their own; they define societal vulnerability. Sudden resource shocks or political controversies act as catalysts within high-friction environments.")

    with t_col2:
        radar_df = pd.DataFrame({
            "Dimension": ["Youth Alienation", "Price Strain", "Stagnation", "Despair Baseline", "Alcohol Coping"],
            "Value": [
                min(100, latest_youth_unemp * 3),
                min(100, latest_inf * 5),
                max(0, min(100, (6 - latest_gdp) * 15)),
                min(100, latest_suicide * 5),
                min(100, latest_alc * 8)
            ]
        })
        fig_r = px.line_polar(radar_df, r="Value", theta="Dimension", line_close=True, title="Societal Vulnerability Profile")
        fig_r.update_traces(fill="toself", line_color="#EF4444" if friction_score > 50 else "#3B82F6")
        st.plotly_chart(fig_r, use_container_width=True)

# TAB 2: MARKETING & PRODUCT OPPORTUNITIES
with tab_marketing:
    st.subheader(f"Market Strategy & Product Placement: {selected_country}")
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("### 🛒 Product Strategy & Value Design")
        if consumer_sentiment < 45 or latest_inf > 5.5:
            st.warning("**Market Phase: Defensive / Price-Sensitive Mode**")
            st.markdown("""
            * **Packaging & Pricing:** Emphasize refill packs, downsized packaging, and no-contract subscriptions.
            * **High-Growth Categories:**
              1. **Value Essentials & Functional Dupe Brands:** Cost-effective alternatives to branded household goods.
              2. **Recommerce & Second-Hand:** Platforms for refurbished electronics and certified pre-owned tools.
              3. **Micro-Income Tools:** Platforms enabling side freelance work and digital skills monetization.
            * **Tone:** Functional, grounded, practical; avoid luxury elitism or high-pressure FOMO.
            """)
        else:
            st.success("**Market Phase: Expansive / Quality-Driven Mode**")
            st.markdown("""
            * **Packaging & Pricing:** Open to premium service bundles and convenience-first additions.
            * **High-Growth Categories:**
              1. **Preventive Longevity:** Nutrition optimization, ergonomic tech, preventive diagnostics.
              2. **Time-Saving Automation:** Meal-kit deliveries, smart home integrations, on-demand services.
              3. **Experiential & Social:** Curated events, group athletics, creative learning cohorts.
            * **Tone:** Focus on self-actualization, performance, productivity, and lifestyle quality.
            """)

    with m_col2:
        st.markdown("### 📢 Media Channel & Growth Architecture")
        st.markdown(f"**Recommended Channel Mix:** Digital `{digital_share}%` | Traditional / Field `{offline_share}%`")
        st.markdown(f"""
        * **Digital Channel Deployment:** With internet adoption at **{latest_net:.1f}%** and mobile density at **{latest_mobile:.0f}/100**, mobile-first video campaigns (short-form formats, messaging commerce) deliver optimal conversion.
        * **Effective Campaign Hooks:**
          - *"Cost-per-day transparency"*, *"Built to last"*, *"Guaranteed warranty without hidden fees"*.
        * **Customer Retention:** Flexible refund policies, community-driven support, and localized customer care channels.
        """)

# TAB 3: LONGITUDINAL CHARTS & REAL-TIME INTENT
with tab_charts:
    st.subheader("Longitudinal Indicators & Live Sentiment")
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    
    with c1:
        if not datasets["Inflation (CPI %)"].empty:
            f1 = px.line(datasets["Inflation (CPI %)"], x="Year", y="Value", title="Consumer Price Inflation (%)", markers=True)
            f1.update_traces(line_color="#DC2626")
            st.plotly_chart(f1, use_container_width=True)
            
    with c2:
        if not datasets["Youth Unemployment (%)"].empty:
            f2 = px.bar(datasets["Youth Unemployment (%)"], x="Year", y="Value", title="Youth Unemployment Rate (%)", color_discrete_sequence=["#F59E0B"])
            st.plotly_chart(f2, use_container_width=True)

    with c3:
        if not datasets["Household Consumption (% GDP)"].empty:
            f3 = px.line(datasets["Household Consumption (% GDP)"], x="Year", y="Value", title="Household Consumption Expenditure (% of GDP)", markers=True)
            f3.update_traces(line_color="#2563EB")
            st.plotly_chart(f3, use_container_width=True)

    with c4:
        if not consumer_trends_df.empty:
            st.markdown("**Real-Time Search Trends (Last 90 Days - Google Trends)**")
            st.line_chart(consumer_trends_df)
        else:
            st.info("Google Trends search velocity not indexed for this selected territory.")

# ---------------------------------------------------------
# 8. Report Export Engines (Sidebar Downloads)
# ---------------------------------------------------------
def generate_text_briefing():
    return f"""================================================================================
EXECUTIVE SOCIETAL STABILITY & MARKET INTELLIGENCE REPORT
Target Geography: {selected_country}
Engine: NEXUS Macro & Societal Intelligence Platform
================================================================================

1. CORE INDEX SCORES
- Societal Friction Index        : {friction_score}/100 ({'Elevated Unrest Risk' if friction_score > 55 else 'Normal Equilibrium'})
- Psychosocial Strain Index      : {psych_score}/100 ({'Severe Distress' if psych_score > 60 else 'Manageable'})
- Consumer Spending Sentiment    : {consumer_sentiment}/100 ({'Defensive / Price-Sensitive' if consumer_sentiment < 45 else 'Expansive / Quality-Driven'})
- Annual Inflation Rate (CPI)    : {latest_inf:.2f}%
- Youth Unemployment Rate        : {latest_youth_unemp:.1f}%
- Youth Disconnection (NEET)     : {latest_neet:.1f}%

2. STRATEGIC MARKET RECOMMENDATIONS
- Operational Mode               : {'Defensive Value & Essential Substitutes' if consumer_sentiment < 45 or latest_inf > 5.5 else 'Premium Convenience & Quality Optimization'}
- Recommended Digital Share      : {digital_share}% (Based on {latest_net:.1f}% Internet Penetration)
- Recommended Offline / Field    : {offline_share}%

Tone & Messaging:
{'- Emphasize utility, transparent pricing, guaranteed durability. Avoid luxury ostentation.' if consumer_sentiment < 45 or latest_inf > 5.5 else '- Focus on self-actualization, performance optimization, and lifestyle refinement.'}
================================================================================
"""

def generate_combined_csv():
    combined_df = None
    for label, df in datasets.items():
        if not df.empty:
            temp = df.rename(columns={"Value": label})
            if combined_df is None:
                combined_df = temp
            else:
                combined_df = pd.merge(combined_df, temp, on="Year", how="outer")
    if combined_df is not None:
        return combined_df.sort_values("Year", ascending=False).to_csv(index=False).encode('utf-8')
    return b""

st.sidebar.divider()
st.sidebar.subheader("📥 Export Intelligence Reports")

st.sidebar.download_button(
    label="📄 Download Executive Briefing (.txt)",
    data=generate_text_briefing(),
    file_name=f"{selected_country}_intelligence_briefing.txt",
    mime="text/plain",
    use_container_width=True
)

st.sidebar.download_button(
    label="📊 Download Historical Data (.csv)",
    data=generate_combined_csv(),
    file_name=f"{selected_country}_macro_historical_data.csv",
    mime="text/csv",
    use_container_width=True
)
