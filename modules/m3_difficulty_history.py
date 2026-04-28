"""Starter file for module M3."""

from datetime import UTC, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import (
    get_block,
    get_block_hash_by_height,
    get_latest_block,
)


@st.cache_data(ttl=300)
def get_recent_difficulty_periods(n_periods: int) -> pd.DataFrame:
    """Return recent completed Bitcoin difficulty adjustment periods."""
    latest = get_latest_block()
    latest_height = latest["height"]

    # Last fully completed 2016-block adjustment period
    last_completed_end = latest_height - (latest_height % 2016) - 1

    rows = []

    for i in range(n_periods):
        end_height = last_completed_end - (i * 2016)
        start_height = end_height - 2015

        if start_height < 0:
            break

        start_hash = get_block_hash_by_height(start_height)
        end_hash = get_block_hash_by_height(end_height)

        start_block = get_block(start_hash)
        end_block = get_block(end_hash)

        actual_timespan = end_block["timestamp"] - start_block["timestamp"]
        avg_block_time = actual_timespan / 2016
        ratio_to_target = avg_block_time / 600

        rows.append(
            {
                "period_label": f"{start_height:,}-{end_height:,}",
                "start_height": start_height,
                "end_height": end_height,
                "adjustment_date": datetime.fromtimestamp(end_block["timestamp"], UTC),
                "difficulty": start_block["difficulty"],
                "actual_timespan_seconds": actual_timespan,
                "avg_block_time_seconds": avg_block_time,
                "ratio_to_target": ratio_to_target,
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df = df.sort_values("end_height").reset_index(drop=True)
    return df


def render() -> None:
    """Render the M3 panel."""
    st.header("M3 - Difficulty History")
    st.write(
        "Visualize Bitcoin difficulty across recent completed adjustment periods "
        "and compare the real average block time with the 600-second target."
    )

    n_periods = st.slider(
        "Number of completed adjustment periods",
        min_value=4,
        max_value=12,
        value=8,
        step=1,
        key="m3_periods",
    )

    try:
        df = get_recent_difficulty_periods(n_periods)

        if df.empty:
            st.warning("No difficulty history data available.")
            return

        st.subheader("Difficulty over adjustment periods")

        fig_difficulty = px.line(
            df,
            x="adjustment_date",
            y="difficulty",
            markers=True,
            title="Bitcoin Difficulty by Adjustment Period",
            labels={
                "adjustment_date": "Adjustment date",
                "difficulty": "Difficulty",
            },
            hover_data={
                "period_label": True,
                "difficulty": ":,.2f",
                "adjustment_date": True,
            },
        )
        st.plotly_chart(fig_difficulty, use_container_width=True)

        st.subheader("Average block time vs 600-second target")

        fig_ratio = px.bar(
            df,
            x="period_label",
            y="ratio_to_target",
            title="Actual Average Block Time / 600 Seconds",
            labels={
                "period_label": "Adjustment period",
                "ratio_to_target": "Ratio to target",
            },
            hover_data={
                "avg_block_time_seconds": ":,.2f",
                "ratio_to_target": ":,.4f",
            },
        )
        st.plotly_chart(fig_ratio, use_container_width=True)

        st.subheader("Adjustment period details")

        table_df = df.copy()
        table_df["difficulty"] = table_df["difficulty"].round(2)
        table_df["avg_block_time_seconds"] = table_df["avg_block_time_seconds"].round(2)
        table_df["ratio_to_target"] = table_df["ratio_to_target"].round(4)

        st.dataframe(
            table_df[
                [
                    "period_label",
                    "adjustment_date",
                    "difficulty",
                    "avg_block_time_seconds",
                    "ratio_to_target",
                ]
            ],
            use_container_width=True,
        )

        latest_ratio = df.iloc[-1]["ratio_to_target"]
        latest_avg = df.iloc[-1]["avg_block_time_seconds"]
        latest_diff = df.iloc[-1]["difficulty"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest completed period difficulty", f"{latest_diff:,.2f}")
        col2.metric("Latest avg block time (s)", f"{latest_avg:.2f}")
        col3.metric("Latest ratio vs target", f"{latest_ratio:.4f}")

        st.info(
            "A ratio above 1 means blocks were slower than the 10-minute target "
            "during that adjustment period. A ratio below 1 means they were faster."
        )

    except Exception as exc:
        st.error(f"Error loading difficulty history: {exc}")