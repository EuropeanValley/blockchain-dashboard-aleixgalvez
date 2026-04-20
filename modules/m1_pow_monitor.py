"""Starter file for module M1."""

import streamlit as st
from api.blockchain_client import (
    get_latest_block,
    get_block,
    get_current_difficulty,
)


def count_leading_zero_hex(hash_value: str) -> int:
    return len(hash_value) - len(hash_value.lstrip("0"))


def render() -> None:
    """Render the M1 panel."""
    st.header("M1 - Proof of Work Monitor")
    st.write("Live Bitcoin mining data from public blockchain APIs.")

    try:
        latest = get_latest_block()
        block = get_block(latest["hash"])
        difficulty = get_current_difficulty()
        leading_zeros = count_leading_zero_hex(latest["hash"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Block Height", latest["height"])
        col2.metric("Difficulty", f"{difficulty:.2f}")
        col3.metric("Transaction Count", block["tx_count"])

        st.write(f"**Hash:** `{latest['hash']}`")
        st.write(f"**Nonce:** {block['nonce']}")
        st.write(f"**Bits:** {block['bits']}")
        st.write(f"**Leading zero hex digits:** {leading_zeros}")

        st.info(
            "The leading zeros in the block hash reflect the Proof of Work condition: "
            "the hash must be below a target threshold encoded by the bits field."
        )

    except Exception as exc:
        st.error(f"Error fetching blockchain data: {exc}")