"""Optional file for module M5."""

import hashlib

import pandas as pd
import streamlit as st

from api.blockchain_client import get_block, get_latest_block, get_block_txids


def double_sha256(data: bytes) -> bytes:
    """Return SHA256(SHA256(data))."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def merkle_parent(hash1_hex: str, hash2_hex: str) -> str:
    """
    Compute the Merkle parent of two txids.
    Bitcoin txids are displayed big-endian, but hashing is done on little-endian bytes.
    """
    h1 = bytes.fromhex(hash1_hex)[::-1]
    h2 = bytes.fromhex(hash2_hex)[::-1]
    parent = double_sha256(h1 + h2)
    return parent[::-1].hex()


def build_merkle_proof(txids: list[str], target_index: int) -> tuple[str, list[dict]]:
    """Build the Merkle proof path for one transaction index."""
    if not txids:
        raise ValueError("Empty txid list.")
    if target_index < 0 or target_index >= len(txids):
        raise ValueError("Invalid transaction index.")

    current_level = txids[:]
    current_index = target_index
    proof_steps = []
    current_hash = current_level[current_index]

    level_number = 0

    while len(current_level) > 1:
        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])

        sibling_index = current_index - 1 if current_index % 2 else current_index + 1
        sibling_hash = current_level[sibling_index]

        if current_index % 2 == 0:
            left_hash = current_level[current_index]
            right_hash = sibling_hash
            position = "left"
        else:
            left_hash = sibling_hash
            right_hash = current_level[current_index]
            position = "right"

        parent_hash = merkle_parent(left_hash, right_hash)

        proof_steps.append(
            {
                "level": level_number,
                "current_hash": current_hash,
                "sibling_hash": sibling_hash,
                "position": position,
                "left_hash_used": left_hash,
                "right_hash_used": right_hash,
                "parent_hash": parent_hash,
            }
        )

        next_level = []
        for i in range(0, len(current_level), 2):
            next_level.append(merkle_parent(current_level[i], current_level[i + 1]))

        current_level = next_level
        current_index //= 2
        current_hash = parent_hash
        level_number += 1

    merkle_root = current_level[0]
    return merkle_root, proof_steps


def render() -> None:
    """Render the M5 panel."""
    st.header("M5 - Merkle Proof Verifier")
    st.write(
        "Pick a transaction from the latest block and verify its Merkle proof "
        "step by step until the computed root matches the block Merkle root."
    )

    try:
        latest = get_latest_block()
        block = get_block(latest["hash"])
        txids = get_block_txids(latest["hash"])

        st.write(f"**Latest block hash:** `{latest['hash']}`")
        st.write(f"**Block height:** {block['height']}")
        st.write(f"**Merkle root from block:** `{block['merkle_root']}`")
        st.write(f"**Transaction count:** {len(txids)}")

        tx_index = st.slider(
            "Transaction index inside the block",
            min_value=0,
            max_value=max(len(txids) - 1, 0),
            value=0,
            step=1,
            key="m5_tx_index",
        )

        selected_txid = txids[tx_index]
        st.write(f"**Selected transaction txid:** `{selected_txid}`")

        if st.button("Verify Merkle proof", key="m5_verify"):
            computed_root, proof_steps = build_merkle_proof(txids, tx_index)

            st.subheader("Proof steps")

            if proof_steps:
                step_df = pd.DataFrame(proof_steps)
                st.dataframe(step_df, use_container_width=True)
            else:
                st.info("The block has only one transaction, so the txid itself is the Merkle root.")

            st.subheader("Verification result")
            st.write(f"**Computed Merkle root:** `{computed_root}`")
            st.write(f"**Official block Merkle root:** `{block['merkle_root']}`")
            st.write(f"**Match:** {computed_root == block['merkle_root']}")

            if computed_root == block["merkle_root"]:
                st.success(
                    "Merkle proof verified successfully: the selected transaction is included in the block."
                )
            else:
                st.error(
                    "Merkle proof verification failed: the computed root does not match the block Merkle root."
                )

            st.info(
                "Each step combines the selected hash with its sibling hash, applies double SHA-256, "
                "and moves one level up the Merkle tree until the root is reached."
            )

    except Exception as exc:
        st.error(f"Error verifying Merkle proof: {exc}")