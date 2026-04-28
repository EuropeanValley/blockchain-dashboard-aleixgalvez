"""Starter file for module M4."""

from datetime import UTC, datetime
import math

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_block, get_latest_block


@st.cache_data(ttl=300)
def get_recent_blocks(count: int) -> pd.DataFrame:
    """Fetch recent Bitcoin blocks by walking backwards from the latest block."""
    latest = get_latest_block()
    current_hash = latest["hash"]

    rows = []

    for _ in range(count):
        block = get_block(current_hash)

        rows.append(
            {
                "height": block["height"],
                "hash": block["id"],
                "timestamp": block["timestamp"],
                "timestamp_utc": datetime.fromtimestamp(block["timestamp"], UTC),
                "difficulty": block["difficulty"],
                "tx_count": block["tx_count"],
            }
        )

        prev_hash = block.get("previousblockhash")
        if not prev_hash:
            break

        current_hash = prev_hash

    df = pd.DataFrame(rows)
    df = df.sort_values("height").reset_index(drop=True)
    return df


def exponential_bounds(mean_seconds: float, alpha: float) -> tuple[float, float]:
    """Return lower and upper two-sided quantile bounds for an exponential model."""
    lower = -mean_seconds * math.log(1 - alpha / 2)
    upper = -mean_seconds * math.log(alpha / 2)
    return lower, upper


def tail_probability_exponential(t: float, mean_seconds: float) -> float | None:
    """Return a simple two-sided tail probability under an exponential baseline."""
    if t < 0:
        return None

    cdf = 1 - math.exp(-t / mean_seconds)
    return min(cdf, 1 - cdf) * 2


def classify_interval(t: float, lower_bound: float, upper_bound: float) -> str:
    """Classify an inter-block interval."""
    if t < 0:
        return "Timestamp anomaly"
    if t < lower_bound or t > upper_bound:
        return "Anomalous"
    return "Expected range"


def anomaly_score_from_interval(t: float, mean_seconds: float) -> float:
    """Convert interval rarity into a simple anomaly score."""
    if t < 0:
        return 12.0

    p = tail_probability_exponential(t, mean_seconds)
    if p is None:
        return 12.0

    return -math.log10(max(p, 1e-12))


def build_interarrival_dataset(n_blocks: int, alpha: float) -> pd.DataFrame:
    """Create a dataset of inter-block times and anomaly labels."""
    df = get_recent_blocks(n_blocks)

    df["inter_arrival_seconds"] = df["timestamp"].diff()
    df = df.dropna().copy()

    expected_mean = 600.0
    lower_bound, upper_bound = exponential_bounds(expected_mean, alpha)

    df["lower_bound"] = lower_bound
    df["upper_bound"] = upper_bound
    df["tail_probability"] = df["inter_arrival_seconds"].apply(
        lambda t: tail_probability_exponential(float(t), expected_mean)
    )
    df["anomaly_score"] = df["inter_arrival_seconds"].apply(
        lambda t: anomaly_score_from_interval(float(t), expected_mean)
    )
    df["status"] = df["inter_arrival_seconds"].apply(
        lambda t: classify_interval(float(t), lower_bound, upper_bound)
    )

    return df


def render() -> None:
    """Render the M4 panel."""
    st.header("M4 - AI Component")
    st.write(
        "Detect unusually short or long inter-block times using an exponential "
        "baseline, which is the expected distribution for Bitcoin block arrivals."
    )

    col1, col2 = st.columns(2)
    with col1:
        n_blocks = st.slider(
            "Number of recent blocks to analyze",
            min_value=30,
            max_value=150,
            value=80,
            step=10,
            key="m4_blocks",
        )
    with col2:
        alpha = st.slider(
            "Anomaly sensitivity (alpha)",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01,
            key="m4_alpha",
        )

    try:
        df = build_interarrival_dataset(n_blocks, alpha)

        if df.empty:
            st.warning("Not enough block data available.")
            return

        lower_bound = df["lower_bound"].iloc[0]
        upper_bound = df["upper_bound"].iloc[0]
        anomaly_count = int((df["status"] != "Expected range").sum())
        anomaly_rate = anomaly_count / len(df)

        st.subheader("Anomaly detection summary")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Intervals analyzed", len(df))
        c2.metric("Detected anomalies", anomaly_count)
        c3.metric("Lower expected bound (s)", f"{lower_bound:.2f}")
        c4.metric("Upper expected bound (s)", f"{upper_bound:.2f}")

        st.write(
            f"**Anomaly rate:** {anomaly_rate:.2%}  \n"
            f"Intervals outside the expected exponential range, or negative timestamp jumps, are labelled as anomalous."
        )

        st.subheader("Inter-block times")

        fig = px.scatter(
            df,
            x="timestamp_utc",
            y="inter_arrival_seconds",
            color="status",
            hover_data={
                "height": True,
                "hash": True,
                "inter_arrival_seconds": ":.2f",
                "tail_probability": True,
                "anomaly_score": ":.4f",
            },
            title="Recent Inter-Block Times and Detected Anomalies",
            labels={
                "timestamp_utc": "Block time (UTC)",
                "inter_arrival_seconds": "Inter-arrival time (seconds)",
                "status": "Classification",
            },
        )

        fig.add_hline(
            y=600,
            line_dash="dash",
            annotation_text="Expected mean = 600 s",
        )
        fig.add_hline(
            y=lower_bound,
            line_dash="dot",
            annotation_text="Lower anomaly bound",
        )
        fig.add_hline(
            y=upper_bound,
            line_dash="dot",
            annotation_text="Upper anomaly bound",
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Most anomalous intervals")

        anomaly_df = df[df["status"] != "Expected range"].copy()
        anomaly_df = anomaly_df.sort_values(
            "anomaly_score", ascending=False
        ).reset_index(drop=True)

        if anomaly_df.empty:
            st.success("No anomalous intervals were detected in the selected sample.")
        else:
            show_df = anomaly_df[
                [
                    "height",
                    "timestamp_utc",
                    "inter_arrival_seconds",
                    "tail_probability",
                    "anomaly_score",
                    "status",
                    "difficulty",
                    "tx_count",
                ]
            ].copy()

            show_df["inter_arrival_seconds"] = show_df["inter_arrival_seconds"].round(2)
            show_df["anomaly_score"] = show_df["anomaly_score"].round(4)
            show_df["difficulty"] = show_df["difficulty"].round(2)

            st.dataframe(show_df, use_container_width=True)

        st.info(
            "This anomaly detector uses an exponential baseline with mean 600 seconds. "
            "It is a simple statistical model, not a neural network, but it is appropriate "
            "because Bitcoin block arrivals are expected to follow a Poisson process. "
            "Negative inter-block times are treated separately as timestamp anomalies."
        )

    except Exception as exc:
        st.error(f"Error running anomaly detector: {exc}")