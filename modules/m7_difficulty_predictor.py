"""Optional file for module M7."""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from modules.m3_difficulty_history import get_recent_difficulty_periods


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute MAE."""
    return float(np.mean(np.abs(y_true - y_pred)))


def fit_linear_regression(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Fit a linear regression with intercept using least squares."""
    X_design = np.column_stack([np.ones(len(X)), X])
    coeffs, _, _, _ = np.linalg.lstsq(X_design, y, rcond=None)
    return coeffs


def predict_linear_regression(X: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    """Predict using fitted coefficients."""
    X_design = np.column_stack([np.ones(len(X)), X])
    return X_design @ coeffs


def build_supervised_dataset(n_periods: int) -> pd.DataFrame:
    """
    Build a supervised dataset where each row predicts the next period difficulty
    from the current period statistics.
    """
    df = get_recent_difficulty_periods(n_periods).copy()

    if df.empty or len(df) < 4:
        return pd.DataFrame()

    df["next_difficulty"] = df["difficulty"].shift(-1)
    df["next_adjustment_date"] = df["adjustment_date"].shift(-1)
    df = df.dropna().reset_index(drop=True)

    return df


def render() -> None:
    """Render the M7 panel."""
    st.header("M7 - Second AI Approach")
    st.write(
        "Predict the next Bitcoin difficulty adjustment using a simple regression model "
        "and compare it against a naive baseline."
    )

    n_periods = st.slider(
        "Number of recent adjustment periods to use",
        min_value=8,
        max_value=24,
        value=16,
        step=1,
        key="m7_periods",
    )

    try:
        df = build_supervised_dataset(n_periods)

        if df.empty or len(df) < 4:
            st.warning("Not enough historical periods available to train and evaluate the model.")
            return

        feature_cols = ["difficulty", "avg_block_time_seconds", "ratio_to_target"]
        target_col = "next_difficulty"

        X = df[feature_cols].to_numpy(dtype=float)
        y = df[target_col].to_numpy(dtype=float)

        split_idx = max(2, int(len(df) * 0.7))
        split_idx = min(split_idx, len(df) - 1)

        train_df = df.iloc[:split_idx].copy()
        test_df = df.iloc[split_idx:].copy()

        X_train = train_df[feature_cols].to_numpy(dtype=float)
        y_train = train_df[target_col].to_numpy(dtype=float)

        X_test = test_df[feature_cols].to_numpy(dtype=float)
        y_test = test_df[target_col].to_numpy(dtype=float)

        # Baseline: predict next difficulty as current difficulty
        baseline_pred = test_df["difficulty"].to_numpy(dtype=float)

        # Linear regression model
        coeffs = fit_linear_regression(X_train, y_train)
        model_pred = predict_linear_regression(X_test, coeffs)

        baseline_mae = mean_absolute_error(y_test, baseline_pred)
        model_mae = mean_absolute_error(y_test, model_pred)

        st.subheader("Model evaluation")

        c1, c2, c3 = st.columns(3)
        c1.metric("Training periods", len(train_df))
        c2.metric("Test periods", len(test_df))
        c3.metric("Model better than baseline", str(model_mae < baseline_mae))

        c4, c5 = st.columns(2)
        c4.metric("Baseline MAE", f"{baseline_mae:,.2f}")
        c5.metric("Regression MAE", f"{model_mae:,.2f}")

        results_df = test_df.copy()
        results_df["baseline_prediction"] = baseline_pred
        results_df["model_prediction"] = model_pred
        results_df["actual_next_difficulty"] = y_test

        st.subheader("Actual vs predicted next difficulty")

        plot_df = results_df[
            [
                "next_adjustment_date",
                "actual_next_difficulty",
                "baseline_prediction",
                "model_prediction",
            ]
        ].copy()

        plot_df = plot_df.melt(
            id_vars="next_adjustment_date",
            value_vars=[
                "actual_next_difficulty",
                "baseline_prediction",
                "model_prediction",
            ],
            var_name="series",
            value_name="difficulty_value",
        )

        fig = px.line(
            plot_df,
            x="next_adjustment_date",
            y="difficulty_value",
            color="series",
            markers=True,
            title="Next Difficulty: Actual vs Baseline vs Regression",
            labels={
                "next_adjustment_date": "Adjustment date",
                "difficulty_value": "Difficulty",
                "series": "Series",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Prediction for the next unseen period")

        latest_row = df.iloc[-1]
        latest_features = np.array(
            [[
                latest_row["difficulty"],
                latest_row["avg_block_time_seconds"],
                latest_row["ratio_to_target"],
            ]],
            dtype=float,
        )

        next_baseline = float(latest_row["difficulty"])
        next_model_pred = float(predict_linear_regression(latest_features, coeffs)[0])

        p1, p2, p3 = st.columns(3)
        p1.metric("Latest known difficulty", f"{latest_row['difficulty']:,.2f}")
        p2.metric("Naive next prediction", f"{next_baseline:,.2f}")
        p3.metric("Model next prediction", f"{next_model_pred:,.2f}")

        st.subheader("Model input data")
        show_df = df[
            [
                "period_label",
                "adjustment_date",
                "difficulty",
                "avg_block_time_seconds",
                "ratio_to_target",
                "next_difficulty",
            ]
        ].copy()

        show_df["difficulty"] = show_df["difficulty"].round(2)
        show_df["avg_block_time_seconds"] = show_df["avg_block_time_seconds"].round(2)
        show_df["ratio_to_target"] = show_df["ratio_to_target"].round(4)
        show_df["next_difficulty"] = show_df["next_difficulty"].round(2)

        st.dataframe(show_df, use_container_width=True)

        st.info(
            "This second AI approach is a simple supervised regression model. "
            "It predicts the next difficulty adjustment from the current period difficulty, "
            "average block time, and ratio to the 600-second target. "
            "Its performance is compared with a naive baseline that assumes the next difficulty "
            "will be equal to the current one."
        )

    except Exception as exc:
        st.error(f"Error running difficulty predictor: {exc}")