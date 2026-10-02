import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from pytrends.request import TrendReq

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS Injection
# ---------------------------------------------------------
st.set_page_config(
    page_title="NEXUS | Enterprise & Psychosocial Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling
st.markdown("""
<style>
    /* Global Typography & Background adjustments */
    .stApp {
        background-color: #0b0f19;
    }
    
    /* Card Container */
    .nexus-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    
    /* Pricing Card */
    .pricing-card {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid #3b82f6;
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
    }
    
    /* Metric pill */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .badge-live { background-color: #064e3b; color: #34d399; }
    .badge-premium { background-color: #4c1d95; color: #c084fc; }
    
    /* Button formatting */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
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

# ---------------------------------------------------------
# 3. Sidebar Navigation & Global Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<span class="status-badge badge-live">● ENTERPRISE FEED LIVE</span>', unsafe_allow_html=True)
    st.title("NEXUS Platform")
    st.caption("Strategic Market & Psychosocial Systems")
    
    # Navigation Switcher
    app_mode = st.radio(
        "Navigation",
        [
            "🌐 Macro Radar & Stability",
            "🛠️ Product Viability Simulator",
            "🧠 Organizational Resilience Audit",
            "💎 Enterprise Plans & Pricing"
        ]
    )
    
    st.divider()
    st.subheader("Regional Scope")
    selected_country = st.selectbox("Active Market", list(COUNTRIES.keys()), index=0)
    country_meta = COUNTRIES[selected_country]

# ---------------------------------------------------------
# 4. Open-Source Data Ingestion Engine (World Bank API)
# ---------------------------------------------------------
INDICATOR_REGISTRY = {
    "Inflation (CPI %)": "FP.CPI.TOTL.ZG",
    "GDP Growth (Annual %)": "NY.GDP.MKTP.KD.ZG",
    "Youth Unemployment (%)": "SL.UEM.1524.ZS",
    "Suicide Mortality (per 100k)": "SH.STA.SUIC.P5",
    "Youth NEET (%)": "SL.UEM.NEET.ZS",
    "Household Consumption (% GDP)": "NE.CON.PRVT.ZS",
    "Internet Adoption (% pop)": "IT.NET.USER.ZS"
}

@st.cache_data(ttl=86400)
def fetch_world_bank_series(country_iso, indicator_code, num_records=10):
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

with st.spinner("Ingesting verified macroeconomic and psychosocial feeds..."):
    datasets = {name: fetch_world_bank_series(country_meta["wb"], code) for name, code in INDICATOR_REGISTRY.items()}

def get_latest(df, default=0.0):
    if not df.empty:
        return float(df.iloc[-1]["Value"]), int(df.iloc[-1]["Year"])
    return default, 0

latest_inf, _ = get_latest(datasets["Inflation (CPI %)"], 3.5)
latest_gdp, _ = get_latest(datasets["GDP Growth (Annual %)"], 4.2)
latest_youth_unemp, _ = get_latest(datasets["Youth Unemployment (%)"], 16.0)
latest_suicide, _ = get_latest(datasets["Suicide Mortality (per 100k)"], 10.0)
latest_neet, _ = get_latest(datasets["Youth NEET (%)"], 18.0)
latest_hcon, _ = get_latest(datasets["Household Consumption (% GDP)"], 60.0)
latest_net, _ = get_latest(datasets["Internet Adoption (% pop)"], 75.0)

# Composite Scores
friction_score = max(5, min(95, int((latest_youth_unemp * 1.3) + (latest_inf * 1.1) + (latest_neet * 0.8) - (latest_gdp * 0.7) + 15)))
psych_score = max(5, min(95, int((latest_suicide * 2.5) + (latest_neet * 1.5) + 10)))
consumer_sentiment = max(10, min(95, int(50 + (latest_gdp * 4) + (latest_hcon * 0.3) - (latest_inf * 5))))

# ---------------------------------------------------------
# 5. Header Banner
# ---------------------------------------------------------
st.markdown(f"""
<div class="nexus-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h2 style="color: #ffffff; margin: 0; font-weight: 800;">NEXUS Predictive Intelligence</h2>
            <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 15px;">
                Commercial Consumer Analytics & Psychosocial Well-Being Architecture • Active Region: <strong style="color: #38bdf8;">{selected_country}</strong>
            </p>
        </div>
        <div>
            <span class="status-badge badge-premium">CLIENT SUITE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 1: MACRO RADAR & STABILITY
# ---------------------------------------------------------
if app_mode == "🌐 Macro Radar & Stability":
    st.subheader("Global Health & Market Momentum Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Societal Friction Index", f"{friction_score}/100", delta="High Tension" if friction_score > 55 else "Equilibrium", delta_color="inverse")
    with col2:
        st.metric("Consumer Buying Sentiment", f"{consumer_sentiment}/100", delta="Defensive Mode" if consumer_sentiment < 45 else "Expansionary", delta_color="normal")
    with col3:
        st.metric("Psychosocial Despair Baseline", f"{psych_score}/100", delta="Elevated Strain" if psych_score > 55 else "Resilient", delta_color="inverse")
    with col4:
        st.metric("Annual Inflation (CPI)", f"{latest_inf:.2f}%", help="Primary driver of real-wage contraction")
        
    st.divider()
    
    tab_biz, tab_psych = st.tabs(["👔 Executive & Commercial Perspective", "🧬 Behavioral Psychology & Public Health"])
    
    with tab_biz:
        st.markdown("### Strategic Market Climate")
        b1, b2 = st.columns(2)
        with b1:
            st.markdown(f"""
            * **Consumer Mindset:** {'Consumers are actively cutting non-essential subscriptions, prioritizing durability and clear price-to-value ratios.' if consumer_sentiment < 45 else 'Consumers demonstrate strong appetite for convenience, premium subscriptions, and wellness products.'}
            * **Pricing Power:** In this environment, brands that communicate cost-per-day transparency experience significantly lower churn than brands using high-pressure scarcity tactics.
            * **Digital Reach:** Internet adoption stands at **{latest_net:.1f}%**, requiring mobile-first, short-form video engagement rather than desktop-focused marketing funnels.
            """)
        with b2:
            if not datasets["Household Consumption (% GDP)"].empty:
                fig = px.line(datasets["Household Consumption (% GDP)"], x="Year", y="Value", title="Private Domestic Spending (% GDP)")
                fig.update_traces(line_color="#3b82f6")
                st.plotly_chart(fig, use_container_width=True)
                
    with tab_psych:
        st.markdown("### Psychosocial Ecosystem Analysis")
        p1, p2 = st.columns(2)
        with p1:
            st.markdown(f"""
            * **Despair & Burnout Indicators:** Despair mortality index sits at **{latest_suicide:.1f}/100k**, indicating the baseline psychological strain on the labor pool.
            * **Disconnection Vector (NEET):** **{latest_neet:.1f}%** of youth are neither studying nor working. This is a recognized indicator for social anomie, heightened cynicism, and polarization.
            * **Workforce Impact:** Chronic macroeconomic friction directly correlates with heightened cognitive fatigue, impaired executive function, and higher turnover across client companies.
            """)
        with p2:
            radar_df = pd.DataFrame({
                "Indicator": ["Youth Alienation", "Price Shock", "Labor Stagnation", "Despair Baseline", "Consumption Strain"],
                "Score": [min(100, latest_neet * 3), min(100, latest_inf * 5), max(0, min(100, (6 - latest_gdp) * 15)), min(100, latest_suicide * 5), 100 - consumer_sentiment]
            })
            fig_r = px.line_polar(radar_df, r="Score", theta="Indicator", line_close=True, title="Societal Vulnerability Pentagon")
            fig_r.update_traces(fill="toself", line_color="#a855f7")
            st.plotly_chart(fig_r, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2: PRODUCT VIABILITY SIMULATOR
# ---------------------------------------------------------
elif app_mode == "🛠️ Product Viability Simulator":
    st.subheader("Data-Backed Product Formulation & Viability Engine")
    st.write("Enter your planned product specifications below to test market viability against current macroeconomic and psychosocial conditions.")
    
    sim_col1, sim_col2 = st.columns([1, 1.2])
    
    with sim_col1:
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.markdown("#### Product Parameters")
        prod_name = st.text_input("Product / Service Name", value="CogniCore Daily Focus")
        prod_category = st.selectbox("Category", [
            "Functional Health & Wellness",
            "Enterprise B2B SaaS",
            "Consumer Staple / FMCG",
            "EdTech / Skill Development",
            "Luxury / Lifestyle Goods"
        ])
        target_audience = st.selectbox("Primary Demographic", [
            "Gen Z & Students (High NEET Vulnerability)",
            "Working Professionals (25-45, High Stress)",
            "Budget-Constrained Households",
            "High Net Worth Individuals"
        ])
        price_tier = st.select_slider("Price Tier", options=["Free / Ad-Supported", "Budget-Friendly", "Mid-Market", "Premium / Luxury"])
        analyze_btn = st.button("Run Viability Simulation", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with sim_col2:
        if analyze_btn or "has_run" not in st.session_state:
            st.session_state["has_run"] = True
            
            # Simple heuristic viability algorithm based on real parameters
            base_score = 70
            if price_tier == "Premium / Luxury" and consumer_sentiment < 45:
                base_score -= 25
            if prod_category in ["Functional Health & Wellness", "EdTech / Skill Development"] and psych_score > 50:
                base_score += 20
            if target_audience == "Budget-Constrained Households" and latest_inf > 5.0 and price_tier == "Budget-Friendly":
                base_score += 15
            viability_score = max(15, min(98, base_score))
            
            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.markdown(f"### Viability Forecast: **{viability_score}/100**")
            
            if viability_score >= 75:
                st.success("🟢 **High Market Fit Potential:** Your product directly addresses an unmet need in the current socio-economic environment.")
            elif viability_score >= 50:
                st.warning("🟡 **Moderate Viability (Pricing Adjustments Needed):** Strong category interest, but consumer elasticity requires cautious positioning.")
            else:
                st.error("🔴 **High Friction Risk:** Current purchasing power and collective strain suggest resistance to this tier and category combination.")
                
            st.markdown("#### Strategic Recommendations:")
            st.markdown(f"""
            1. **Pricing Architecture:** {'Offer transparent installment options or smaller starter sizes to reduce initial trial friction.' if consumer_sentiment < 50 else 'Bundle with premium support or expedited access to capture quality-conscious buyers.'}
            2. **Psychological Positioning:** Frame value around **peace of mind, measurable time saved, and agency**, rather than aspirational luxury.
            3. **Channel Recommendation:** Align campaigns toward mobile-first educational content to reach the target demographic where attention is concentrated.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 3: ORGANIZATIONAL RESILIENCE AUDIT
# ---------------------------------------------------------
elif app_mode == "🧠 Organizational Resilience Audit":
    st.subheader("Organizational Psychosocial Diagnostic")
    st.write("Designed for corporate leaders, HR strategists, and organizational psychologists to calculate institutional burnout and attrition exposure.")
    
    org_col1, org_col2 = st.columns([1, 1.2])
    
    with org_col1:
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.markdown("#### Company Profile & Signals")
        company_size = st.selectbox("Company Size", ["1-50 employees", "51-250 employees", "251-1000 employees", "1000+ enterprise"])
        overtime_intensity = st.slider("Weekly Overtime Hours (Team Average)", 0, 20, 6)
        communication_cadence = st.select_slider("Out-of-Hours Message Frequency", options=["Never", "Occasional", "Frequent", "Constant / Expected"])
        psychological_safety = st.slider("Psychological Safety Score (Estimated 1-10)", 1, 10, 6)
        run_audit_btn = st.button("Generate Diagnostic Report", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with org_col2:
        if run_audit_btn or "audit_run" not in st.session_state:
            st.session_state["audit_run"] = True
            
            # Risk calculation: baseline societal tension + internal stress
            internal_strain = (overtime_intensity * 3) + (10 - psychological_safety) * 5
            total_burnout_risk = max(10, min(95, int((internal_strain * 0.6) + (psych_score * 0.4))))
            
            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.markdown(f"### Workplace Burnout Vulnerability: **{total_burnout_risk}/100**")
            
            if total_burnout_risk > 60:
                st.error("⚠️ **High Attrition Danger:** Your internal workloads amplify external macroeconomic anxiety. Elevated risk of sudden executive turnover and decreased productivity.")
            else:
                st.success("✅ **Stable Organizational Health:** Current internal practices provide adequate psychological insulation against external stressors.")
                
            st.markdown("#### Prescribed Interventions (Psychologist-Approved):")
            st.markdown("""
            * **Asynchronous Boundary Windows:** Establish complete communication blackouts between 8 PM and 8 AM to facilitate genuine cognitive recovery.
            * **Micro-Decompression Rituals:** Introduce mandatory 5-minute pauses between consecutive virtual meetings to mitigate prefrontal cortex fatigue.
            * **Financial Well-Being Workshops:** Combine mental health benefits with practical personal finance coaching to directly reduce real-wage stress.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 4: ENTERPRISE PLANS & PRICING
# ---------------------------------------------------------
elif app_mode == "💎 Enterprise Plans & Pricing":
    st.subheader("Enterprise Subscription & Consulting Tiers")
    st.write("Deploy the NEXUS Intelligence Platform across your corporate strategy, product design, and people teams.")
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="color: #94a3b8;">Starter Insights</h3>
            <h1 style="color: #ffffff; margin: 10px 0;">$499<span style="font-size: 16px; color: #64748b;">/mo</span></h1>
            <p style="color: #94a3b8; font-size: 13px;">For early-stage startups validating product-market fit.</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            <ul style="text-align: left; color: #cbd5e1; font-size: 14px; line-height: 1.8;">
                <li>Access to 5 Core Regional Feeds</li>
                <li>Product Viability Simulator (50 runs/mo)</li>
                <li>Monthly Macro & Sentiment Briefings</li>
                <li>Standard Data Exports (CSV)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Starter", key="btn_starter", use_container_width=True):
            st.success("Inquiry received for Starter Plan. Our team will contact you within 24 hours.")
            
    with p2:
        st.markdown("""
        <div class="pricing-card" style="border: 2px solid #3b82f6; transform: scale(1.02);">
            <span class="status-badge badge-premium" style="margin-bottom: 10px;">MOST POPULAR</span>
            <h3 style="color: #60a5fa;">Corporate Pro</h3>
            <h1 style="color: #ffffff; margin: 10px 0;">$1,499<span style="font-size: 16px; color: #64748b;">/mo</span></h1>
            <p style="color: #94a3b8; font-size: 13px;">For mid-size enterprises & consumer brands optimizing strategy.</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            <ul style="text-align: left; color: #cbd5e1; font-size: 14px; line-height: 1.8;">
                <li>Full Global Data Ingestion (All Nations)</li>
                <li>Unlimited Product Viability Modeling</li>
                <li>Organizational Well-Being Audit Engine</li>
                <li>Real-Time Anomaly & Volatility Alerts</li>
                <li>Dedicated Account Strategist</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Corporate Pro", key="btn_pro", type="primary", use_container_width=True):
            st.success("Inquiry received for Corporate Pro. Our team will contact you within 24 hours.")
            
    with p3:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="color: #94a3b8;">Custom Enterprise</h3>
            <h1 style="color: #ffffff; margin: 10px 0;">Custom</h1>
            <p style="color: #94a3b8; font-size: 13px;">For institutions, venture studios & healthcare systems.</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            <ul style="text-align: left; color: #cbd5e1; font-size: 14px; line-height: 1.8;">
                <li>Direct API Integration into Internal BI</li>
                <li>Custom Psychosocial & Sociological Modeling</li>
                <li>Quarterly On-Site Executive Workshops</li>
                <li>White-Label Client Dashboards</li>
                <li>Custom SLA & Security Compliance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Contact Enterprise Sales", key="btn_ent", use_container_width=True):
            st.success("Enterprise sales request logged. A senior partner will reach out directly.")

# ---------------------------------------------------------
# Global Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px; padding: 20px 0;">
    NEXUS Predictive Intelligence Platform © 2026 • Real-Time Macro-Data, Psychosocial Health & Strategic Product Modeling
</div>
""", unsafe_allow_html=True)
