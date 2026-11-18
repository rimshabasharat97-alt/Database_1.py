
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SmartVest | Robo Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }
    [data-testid="stSidebar"] {
        background-color: #10243a;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    .hero {
        padding: 35px;
        background: linear-gradient(120deg, #10243a, #176b60);
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
    }
    .hero h1 {
        color: white;
        font-size: 42px;
    }
    .hero p {
        color: #e0f2ed;
        font-size: 17px;
    }
    .disclaimer {
        padding: 15px;
        background: #fff3cd;
        border-radius: 10px;
        color: #664d03;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# ASSET CONFIGURATION
# --------------------------------------------------

ASSET_CLASSES = [
    "Pakistan equities",
    "Government securities",
    "Mutual funds",
    "Money market / cash",
    "Gold",
]

ASSET_ASSUMPTIONS = {
    "Pakistan equities": {"return": 0.14, "volatility": 0.25},
    "Government securities": {"return": 0.10, "volatility": 0.07},
    "Mutual funds": {"return": 0.12, "volatility": 0.14},
    "Money market / cash": {"return": 0.08, "volatility": 0.02},
    "Gold": {"return": 0.09, "volatility": 0.16},
}

MODEL_PORTFOLIOS = {
    "Conservative": {
        "Pakistan equities": 10,
        "Government securities": 40,
        "Mutual funds": 15,
        "Money market / cash": 25,
        "Gold": 10,
    },
    "Moderate": {
        "Pakistan equities": 30,
        "Government securities": 30,
        "Mutual funds": 20,
        "Money market / cash": 10,
        "Gold": 10,
    },
    "Aggressive": {
        "Pakistan equities": 50,
        "Government securities": 15,
        "Mutual funds": 20,
        "Money market / cash": 5,
        "Gold": 10,
    },
}

ISLAMIC_LABELS = {
    "Pakistan equities": "Shariah-screened equities",
    "Government securities": "Islamic sovereign / Sukuk alternatives",
    "Mutual funds": "Shariah-compliant mutual funds",
    "Money market / cash": "Islamic money-market alternatives",
    "Gold": "Gold",
}

# --------------------------------------------------
# CORE FUNCTIONS
# --------------------------------------------------

def assess_risk(age, horizon, tolerance, experience, stability, goal):

    score = 0

    score += 25 if horizon >= 10 else 16 if horizon >= 5 else 5

    score += {
        "Low": 5,
        "Medium": 18,
        "High": 30,
    }[tolerance]

    score += {
        "Beginner": 5,
        "Some experience": 12,
        "Experienced": 18,
    }[experience]

    score += {
        "Unstable": 3,
        "Moderate": 8,
        "Stable": 15,
    }[stability]

    score += 10 if age < 30 else 7 if age < 50 else 3

    if goal == "Capital preservation":
        score -= 15
    elif goal == "Long-term growth":
        score += 8

    score = int(np.clip(score, 0, 100))

    if tolerance == "Low" or goal == "Capital preservation" or score < 35:
        profile = "Conservative"
    elif score < 68:
        profile = "Moderate"
    else:
        profile = "Aggressive"

    return profile, score


def expected_return(allocation):
    return sum(
        allocation[a] / 100 * ASSET_ASSUMPTIONS[a]["return"]
        for a in allocation
    )


def portfolio_volatility(allocation):
    variance = sum(
        (
            allocation[a] / 100
            * ASSET_ASSUMPTIONS[a]["volatility"]
        ) ** 2
        for a in allocation
    )
    return np.sqrt(variance)


def create_allocation_table(amount, allocation, islamic):
    rows = []

    for asset, weight in allocation.items():
        label = ISLAMIC_LABELS[asset] if islamic else asset

        rows.append({
            "Asset Class": label,
            "Allocation (%)": weight,
            "Investment Amount (PKR)": amount * weight / 100,
        })

    return pd.DataFrame(rows)


def simulate_portfolio(amount, allocation, years):
    rate = expected_return(allocation)

    values = [amount]

    for year in range(years):
        values.append(values[-1] * (1 + rate))

    return pd.DataFrame({
        "Year": range(years + 1),
        "Portfolio Value (PKR)": values,
    })


def normalize_weights(weights):
    total = sum(weights.values())

    if total <= 0:
        return {asset: 0 for asset in weights}

    return {
        asset: weight / total * 100
        for asset, weight in weights.items()
    }


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "investor": {
        "name": "Investor",
        "amount": 100000.0,
        "age": 25,
        "horizon": 8,
        "goal": "Long-term growth",
        "tolerance": "Medium",
        "experience": "Some experience",
        "stability": "Moderate",
        "islamic": False,
    },
    "risk_profile": "Moderate",
    "risk_score": 50,
    "allocation": dict(MODEL_PORTFOLIOS["Moderate"]),
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("📈 SmartVest")
st.sidebar.caption("Educational Robo-Advisory Platform")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Investor Profile & Risk",
        "Portfolio Recommendation",
        "Dashboard & Performance",
        "Risk Analysis",
        "What-If Simulator",
        "Portfolio Rebalancing",
        "About & Disclaimer",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Pakistan-focused educational prototype")
st.sidebar.caption(f"Date: {date.today()}")

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "Home":

    st.markdown("""
    <div class="hero">
        <h1>Welcome to SmartVest 📈</h1>
        <p>Smart Investments. Personalized Portfolios.
        Better Financial Decisions.</p>
        <p>Your educational robo-advisory portfolio platform.</p>
    </div>
    """, unsafe_allow_html=True)

    inv = st.session_state.investor

    c1, c2, c3 = st.columns(3)

    c1.metric("Risk Profile", st.session_state.risk_profile)
    c2.metric("Investment", f"PKR {inv['amount']:,.0f}")
    c3.metric("Risk Score", f"{st.session_state.risk_score}/100")

    st.subheader("Explore SmartVest")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **Investor Profiling**

        - Risk assessment
        - Investment goals
        - Investment horizon
        - Risk tolerance
        """)

        st.info("""
        **Portfolio Recommendation**

        - Asset allocation
        - Diversification
        - Conventional investments
        - Islamic exploration mode
        """)

    with col2:
        st.success("""
        **Portfolio Dashboard**

        - Investment tracking
        - Performance simulation
        - Portfolio visualization
        - Expected return assumptions
        """)

        st.success("""
        **Financial Tools**

        - Risk analysis
        - What-if simulation
        - Portfolio rebalancing
        """)

    st.warning(
        "This is an educational demonstration, not personalized financial advice."
    )

# --------------------------------------------------
# INVESTOR PROFILE
# --------------------------------------------------

elif page == "Investor Profile & Risk":

    st.title("👤 Investor Profile & Risk Assessment")

    inv = st.session_state.investor

    with st.form("investor_form"):

        name = st.text_input("Investor Name", inv["name"])

        amount = st.number_input(
            "Investment Amount (PKR)",
            min_value=1000.0,
            max_value=1_000_000_000.0,
            value=float(inv["amount"]),
            step=5000.0,
        )

        col1, col2 = st.columns(2)

        with col1:

            age = st.slider(
                "Age",
                18,
                80,
                int(inv["age"]),
            )

            horizon = st.selectbox(
                "Investment Horizon",
                [1, 2, 3, 5, 8, 10, 15, 20],
                index=[1, 2, 3, 5, 8, 10, 15, 20].index(
                    inv["horizon"]
                ),
            )

            goal = st.selectbox(
                "Investment Goal",
                [
                    "Capital preservation",
                    "Regular income",
                    "Balanced growth",
                    "Long-term growth",
                ],
                index=[
                    "Capital preservation",
                    "Regular income",
                    "Balanced growth",
                    "Long-term growth",
                ].index(inv["goal"]),
            )

        with col2:

            tolerance = st.selectbox(
                "Risk Tolerance",
                ["Low", "Medium", "High"],
                index=["Low", "Medium", "High"].index(
                    inv["tolerance"]
                ),
            )

            experience = st.selectbox(
                "Investment Experience",
                ["Beginner", "Some experience", "Experienced"],
                index=[
                    "Beginner",
                    "Some experience",
                    "Experienced",
                ].index(inv["experience"]),
            )

            stability = st.selectbox(
                "Income Stability",
                ["Unstable", "Moderate", "Stable"],
                index=[
                    "Unstable",
                    "Moderate",
                    "Stable",
                ].index(inv["stability"]),
            )

        islamic = st.checkbox(
            "Enable Islamic Investment Mode",
            value=inv["islamic"],
        )

        submitted = st.form_submit_button(
            "Assess My Risk Profile",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        profile, score = assess_risk(
            age,
            horizon,
            tolerance,
            experience,
            stability,
            goal,
        )

        st.session_state.investor = {
            "name": name.strip() or "Investor",
            "amount": amount,
            "age": age,
            "horizon": horizon,
            "goal": goal,
            "tolerance": tolerance,
            "experience": experience,
            "stability": stability,
            "islamic": islamic,
        }

        st.session_state.risk_profile = profile
        st.session_state.risk_score = score
        st.session_state.allocation = dict(
            MODEL_PORTFOLIOS[profile]
        )

        st.success("Risk assessment completed!")

        st.metric("Your Risk Score", f"{score}/100")

        st.subheader(f"Recommended Risk Profile: {profile}")

        st.progress(score / 100)

        st.write(
            "This is a simplified educational score, "
            "not a validated suitability assessment."
        )

# --------------------------------------------------
# PORTFOLIO RECOMMENDATION
# --------------------------------------------------

elif page == "Portfolio Recommendation":

    st.title("💼 Portfolio Recommendation")

    inv = st.session_state.investor

    allocation = st.session_state.allocation

    st.subheader(
        f"Recommended Portfolio: {st.session_state.risk_profile}"
    )

    st.write(
        f"Investor: {inv['name']} | "
        f"Investment: PKR {inv['amount']:,.2f}"
    )

    if inv["islamic"]:

        st.info(
            "Islamic exploration mode is enabled. Verify "
            "individual products, screening and certification "
            "independently."
        )

    df = create_allocation_table(
        inv["amount"],
        allocation,
        inv["islamic"],
    )

    st.dataframe(
        df.style.format({
            "Allocation (%)": "{:.2f}%",
            "Investment Amount (PKR)": "PKR {:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    chart_df = pd.DataFrame({
        "Asset Class": list(allocation.keys()),
        "Allocation": list(allocation.values()),
    })

    fig = px.pie(
        chart_df,
        names="Asset Class",
        values="Allocation",
        hole=0.45,
        title="Portfolio Asset Allocation",
    )

    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)

    c1.metric(
        "Expected Return Assumption",
        f"{expected_return(allocation) * 100:.2f}%",
    )

    c2.metric(
        "Simplified Volatility",
        f"{portfolio_volatility(allocation) * 100:.2f}%",
    )

    st.caption(
        "All return and volatility figures are illustrative "
        "assumptions, not forecasts."
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Portfolio CSV",
        csv,
        "smartvest_portfolio.csv",
        "text/csv",
    )

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

elif page == "Dashboard & Performance":

    st.title("📊 Portfolio Dashboard")

    inv = st.session_state.investor

    allocation = st.session_state.allocation

    amount = float(inv["amount"])
    years = int(inv["horizon"])

    performance = simulate_portfolio(
        amount,
        allocation,
        years,
    )

    ending = performance.iloc[-1]["Portfolio Value (PKR)"]

    gain = ending - amount

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Initial Investment",
        f"PKR {amount:,.0f}",
    )

    c2.metric(
        "Hypothetical Ending Value",
        f"PKR {ending:,.0f}",
    )

    c3.metric(
        "Hypothetical Gain",
        f"PKR {gain:,.0f}",
        f"{gain / amount * 100:.2f}%",
    )

    fig = px.line(
        performance,
        x="Year",
        y="Portfolio Value (PKR)",
        markers=True,
        title="Hypothetical Portfolio Growth",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        performance.style.format({
            "Portfolio Value (PKR)": "PKR {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.warning(
        "This simulation assumes a constant annual return. "
        "It excludes fees, taxes, inflation and market volatility."
    )

# --------------------------------------------------
# RISK ANALYSIS
# --------------------------------------------------

elif page == "Risk Analysis":

    st.title("⚖️ Portfolio Risk Analysis")

    allocation = st.session_state.allocation

    expected = expected_return(allocation)

    volatility = portfolio_volatility(allocation)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Risk Profile",
        st.session_state.risk_profile,
    )

    c2.metric(
        "Expected Return Assumption",
        f"{expected * 100:.2f}%",
    )

    c3.metric(
        "Portfolio Volatility",
        f"{volatility * 100:.2f}%",
    )

    risk_data = []

    for asset, weight in allocation.items():

        risk_data.append({
            "Asset Class": asset,
            "Allocation (%)": weight,
            "Return Assumption (%)":
                ASSET_ASSUMPTIONS[asset]["return"] * 100,
            "Volatility (%)":
                ASSET_ASSUMPTIONS[asset]["volatility"] * 100,
        })

    risk_df = pd.DataFrame(risk_data)

    st.subheader("Asset-Level Risk Indicators")

    st.dataframe(
        risk_df,
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        risk_df,
        x="Asset Class",
        y="Volatility (%)",
        color="Asset Class",
        title="Illustrative Asset Volatility",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "The volatility calculation assumes zero correlation "
        "between asset classes. Actual investments can move "
        "together, particularly during market stress."
    )

# --------------------------------------------------
# WHAT-IF SIMULATOR
# --------------------------------------------------

elif page == "What-If Simulator":

    st.title("🔮 What-If Investment Simulator")

    inv = st.session_state.investor

    amount = st.number_input(
        "Investment Amount (PKR)",
        min_value=1000.0,
        value=float(inv["amount"]),
        step=5000.0,
        key="sim_amount",
    )

    years = st.slider(
        "Investment Period (Years)",
        1,
        30,
        int(inv["horizon"]),
        key="sim_years",
    )

    annual_return = st.slider(
        "Assumed Annual Return (%)",
        -20.0,
        30.0,
        float(expected_return(st.session_state.allocation) * 100),
        0.5,
    )

    rate = annual_return / 100

    values = [amount]

    for year in range(years):
        values.append(values[-1] * (1 + rate))

    sim_df = pd.DataFrame({
        "Year": range(years + 1),
        "Value (PKR)": values,
    })

    final_value = values[-1]

    change = final_value - amount

    c1, c2 = st.columns(2)

    c1.metric(
        "Ending Value",
        f"PKR {final_value:,.2f}",
    )

    c2.metric(
        "Gain / Loss",
        f"PKR {change:,.2f}",
        f"{change / amount * 100:.2f}%",
    )

    fig = px.line(
        sim_df,
        x="Year",
        y="Value (PKR)",
        markers=True,
        title="Investment Scenario",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        sim_df.style.format({
            "Value (PKR)": "PKR {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "This is a hypothetical constant-return scenario, not a forecast."
    )

# --------------------------------------------------
# PORTFOLIO REBALANCING
# --------------------------------------------------

elif page == "Portfolio Rebalancing":

    st.title("🔄 Portfolio Rebalancing")

    target = st.session_state.allocation

    st.write(
        f"Target Profile: {st.session_state.risk_profile}"
    )

    portfolio_value = st.number_input(
        "Current Portfolio Value (PKR)",
        min_value=0.0,
        value=float(st.session_state.investor["amount"]),
        step=5000.0,
    )

    st.subheader("Current Asset Allocation")

    cols = st.columns(2)

    current = {}

    for i, asset in enumerate(ASSET_CLASSES):

        with cols[i % 2]:

            current[asset] = st.number_input(
                f"{asset} (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(target[asset]),
                step=1.0,
                key=f"rebalance_{asset}",
            )

    total = sum(current.values())

    st.write(f"Entered Allocation: {total:.2f}%")

    if total <= 0:

        st.error("Enter a total allocation greater than zero.")

    else:

        normalized = normalize_weights(current)

        rows = []

        for asset in ASSET_CLASSES:

            current_value = (
                portfolio_value * normalized[asset] / 100
            )

            target_value = (
                portfolio_value * target[asset] / 100
            )

            rows.append({
                "Asset Class": asset,
                "Current Weight (%)": normalized[asset],
                "Target Weight (%)": target[asset],
                "Difference (%)": normalized[asset] - target[asset],
                "Adjustment (PKR)": target_value - current_value,
            })

        result = pd.DataFrame(rows)

        st.subheader("Rebalancing Report")

        st.dataframe(
            result.style.format({
                "Current Weight (%)": "{:.2f}%",
                "Target Weight (%)": "{:.2f}%",
                "Difference (%)": "{:.2f}%",
                "Adjustment (PKR)": "PKR {:,.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            "Positive adjustment indicates an increase in a category; "
            "negative adjustment indicates a decrease. "
            "These are mathematical illustrations, not trade instructions."
        )

        st.download_button(
            "Download Rebalancing Report",
            result.to_csv(index=False).encode("utf-8"),
            "smartvest_rebalancing.csv",
            "text/csv",
        )

# --------------------------------------------------
# ABOUT & DISCLAIMER
# --------------------------------------------------

elif page == "About & Disclaimer":

    st.title("ℹ️ About SmartVest")

    st.markdown("""
    ### SmartVest – Educational Robo-Advisory Portfolio App

    SmartVest is a student-friendly fintech application that
    demonstrates how digital investment advisory platforms work.

    ### Main Features

    - Investor profile assessment
    - Risk profiling
    - Portfolio recommendations
    - Asset allocation visualization
    - Portfolio performance simulation
    - Risk analysis
    - What-if investment simulation
    - Portfolio rebalancing
    - Islamic investment exploration mode
    - CSV report downloads

    ### Technology Stack

    - Python
    - Streamlit
    - NumPy
    - Pandas
    - Plotly

    ### Future Improvements

    - Secure authentication
    - Database integration
    - Verified historical market data
    - More advanced portfolio risk models
    - Fees, taxes and inflation calculations
    - Shariah screening verification
    """)

    st.error("""
    DISCLAIMER:

    SmartVest is an educational demonstration only.

    It does not provide personalized financial advice,
    actual investment recommendations or live market prices.

    It does not connect to brokers or execute trades.

    All portfolio allocations, assumptions and projections
    are illustrative. Investments can lose value.
    """)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.sidebar.divider()

st.sidebar.caption(
    "SmartVest © 2026 | Educational FinTech Project"
)

st.sidebar.caption(
    "No live financial data or trading functionality."
)
