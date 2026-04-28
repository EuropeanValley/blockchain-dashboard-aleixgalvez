"""Starter file for module M2."""

from datetime import datetime, UTC

import streamlit as st

from api.blockchain_client import get_block, get_latest_block


def render() -> None:
    """Render the M2 panel."""
    st.header("M2 - Block Header Analyzer")
    st.write("Inspect the six fields of a Bitcoin block header.")

    use_latest = st.checkbox("Use latest block", value=True, key="m2_latest")

    if use_latest:
        latest = get_latest_block()
        block_hash = latest["hash"]
        st.write(f"**Selected block hash:** `{block_hash}`")
    else:
        block_hash = st.text_input(
            "Block hash",
            placeholder="Enter a block hash",
            key="m2_hash",
        )

    if st.button("Analyze block", key="m2_lookup"):
        if not block_hash:
            st.warning("Please enter a block hash.")
            return

        with st.spinner("Fetching data..."):
            try:
                block = get_block(block_hash)

                timestamp_utc = datetime.fromtimestamp(
                    block["timestamp"], UTC
                ).strftime("%Y-%m-%d %H:%M:%S UTC")

                st.subheader("Block header fields")

                st.write(f"**Version:** {block['version']}")
                st.write(f"**Previous hash:** {block['previousblockhash']}")
                st.write(f"**Merkle root:** {block['merkle_root']}")
                st.write(f"**Timestamp:** {timestamp_utc}")
                st.write(f"**Bits:** {block['bits']}")
                st.write(f"**Nonce:** {block['nonce']}")

                st.subheader("Extra block information")
                st.write(f"**Block hash:** {block['id']}")
                st.write(f"**Height:** {block['height']}")
                st.write(f"**Transaction count:** {block['tx_count']}")
                st.write(f"**Difficulty:** {block['difficulty']}")

                st.info(
                    "This first version of M2 displays the six main header fields. "
                    "Next, we will add local Proof of Work verification with double SHA-256."
                )

            except Exception as exc:
                st.error(f"Error fetching block: {exc}")