"""Optional file for module M6."""

import math

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_current_difficulty, get_latest_block


def difficulty_to_hashrate_hs(difficulty: float) -> float:
    """Estimate Bitcoin network hash rate in hashes per second."""
    return difficulty * (2**32) / 600


def nakamoto_catchup_probability(attacker_share: float, confirmations: int) -> float:
    """
    Probability that an attacker with share q eventually catches up from z blocks behind,
    using the formula from Nakamoto's Bitcoin whitepaper (Section 11).
    """
    q = attacker_share
    p = 1.0 - q

    if q >= p:
        return 1.0

    lam = confirmations * (q / p)
    total = 1.0

    for k in range(confirmations + 1):
        poisson = math.exp(-lam) * (lam**k) / math.factorial(k)
        total -= poisson * (1 - (q / p) ** (confirmations - k))

    return max(0.0, min(1.0, total))


def build_confirmation_curve(attacker_share: float, max_confirmations: int) -> pd.DataFrame:
    """Build confirmation-depth risk curve."""
    rows = []

    for z in range(1, max_confirmations + 1):
        rows.append(
            {
                "confirmations": z,
                "attack_success_probability": nakamoto_catchup_probability(attacker_share, z),
            }
        )

    return pd.DataFrame(rows)


def render() -> None:
    """Render the M6 panel."""
    st.header("M6 - Security Score")
    st.write(
        "Estimate the hourly cost of a 51% attack using live Bitcoin difficulty, "
        "and visualize how confirmation depth affects attack success probability."
    )

    try:
        latest = get_latest_block()
        difficulty = get_current_difficulty()
        network_hashrate_hs = difficulty_to_hashrate_hs(difficulty)
        attacker_hashrate_hs = 0.51 * network_hashrate_hs

        st.subheader("Assumptions")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            efficiency_j_per_th = st.slider(
                "ASIC efficiency (J/TH)",
                min_value=10.0,
                max_value=40.0,
                value=18.0,
                step=1.0,
                key="m6_efficiency",
            )

        with c2:
            electricity_price = st.slider(
                "Electricity price (USD/kWh)",
                min_value=0.03,
                max_value=0.30,
                value=0.08,
                step=0.01,
                key="m6_electricity",
            )

        with c3:
            asic_hashrate_ths = st.slider(
                "ASIC unit hash rate (TH/s)",
                min_value=50,
                max_value=300,
                value=200,
                step=10,
                key="m6_asic_rate",
            )

        with c4:
            attacker_share = st.slider(
                "Attacker share for confirmation-risk curve",
                min_value=0.10,
                max_value=0.49,
                value=0.30,
                step=0.01,
                key="m6_attacker_share",
            )

        power_watts = (attacker_hashrate_hs / 1e12) * efficiency_j_per_th
        power_gw = power_watts / 1e9
        cost_per_hour_usd = (power_watts / 1000) * electricity_price
        asic_units_needed = attacker_hashrate_hs / (asic_hashrate_ths * 1e12)

        st.subheader("51% attack cost estimate")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Latest block height", latest["height"])
        m2.metric("Estimated network hash rate", f"{network_hashrate_hs / 1e18:,.2f} EH/s")
        m3.metric("Required attacker hash rate", f"{attacker_hashrate_hs / 1e18:,.2f} EH/s")
        m4.metric("Estimated attack cost/hour", f"${cost_per_hour_usd:,.2f}")

        m5, m6, m7 = st.columns(3)
        m5.metric("Estimated power demand", f"{power_gw:,.2f} GW")
        m6.metric("Approx. ASIC units needed", f"{asic_units_needed:,.0f}")
        m7.metric("Current difficulty", f"{difficulty:,.2f}")

        st.info(
            "This hourly cost estimate is based on energy consumption only. "
            "It does not include hardware acquisition, cooling, maintenance, logistics, or market constraints."
        )

        st.subheader("Confirmation depth vs attack probability")

        max_confirmations = st.slider(
            "Maximum number of confirmations to display",
            min_value=3,
            max_value=20,
            value=12,
            step=1,
            key="m6_max_confirmations",
        )

        curve_df = build_confirmation_curve(attacker_share, max_confirmations)

        fig = px.line(
            curve_df,
            x="confirmations",
            y="attack_success_probability",
            markers=True,
            title="Attack Success Probability vs Confirmation Depth",
            labels={
                "confirmations": "Number of confirmations",
                "attack_success_probability": "Probability of attacker catching up",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

        risk_6_conf = nakamoto_catchup_probability(attacker_share, 6)
        risk_3_conf = nakamoto_catchup_probability(attacker_share, 3)

        r1, r2 = st.columns(2)
        r1.metric("Attack success probability at 3 confirmations", f"{risk_3_conf:.6f}")
        r2.metric("Attack success probability at 6 confirmations", f"{risk_6_conf:.6f}")

        st.write(
            f"With an attacker share of **{attacker_share:.2%}**, the probability of eventually catching up "
            f"drops as the transaction receives more confirmations."
        )

        st.warning(
            "If an attacker truly controls 51% or more of the total hash rate, the long-run catch-up probability becomes 1. "
            "In that case, confirmations no longer provide permanent protection."
        )

    except Exception as exc:
        st.error(f"Error computing security score: {exc}")