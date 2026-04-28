"""Starter file for module M2."""

from datetime import UTC, datetime
import hashlib

import streamlit as st

from api.blockchain_client import get_block, get_latest_block


def int_to_little_endian(value: int, length: int) -> bytes:
    """Convert an integer to little-endian bytes."""
    return value.to_bytes(length, byteorder="little", signed=False)


def hex_to_little_endian(hex_string: str) -> bytes:
    """Convert a hex string to little-endian bytes."""
    return bytes.fromhex(hex_string)[::-1]


def bits_to_target(bits: int) -> int:
    """Decode Bitcoin compact bits representation into the full target integer."""
    exponent = bits >> 24
    coefficient = bits & 0xFFFFFF
    return coefficient * (1 << (8 * (exponent - 3)))


def build_block_header(block: dict) -> bytes:
    """Build the 80-byte Bitcoin block header."""
    version = int_to_little_endian(block["version"], 4)
    prev_hash = hex_to_little_endian(block["previousblockhash"])
    merkle_root = hex_to_little_endian(block["merkle_root"])
    timestamp = int_to_little_endian(block["timestamp"], 4)
    bits = int_to_little_endian(block["bits"], 4)
    nonce = int_to_little_endian(block["nonce"], 4)

    return version + prev_hash + merkle_root + timestamp + bits + nonce


def double_sha256(data: bytes) -> bytes:
    """Return SHA256(SHA256(data))."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def count_leading_zero_bits(hash_hex: str) -> int:
    """Count leading zero bits in a 256-bit hash represented as hex."""
    binary = bin(int(hash_hex, 16))[2:].zfill(256)
    return len(binary) - len(binary.lstrip("0"))


def render() -> None:
    """Render the M2 panel."""
    st.header("M2 - Block Header Analyzer")
    st.write("Inspect the six fields of a Bitcoin block header and verify Proof of Work locally.")

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

        with st.spinner("Fetching data and verifying Proof of Work..."):
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
                st.write(f"**Block hash from API:** {block['id']}")
                st.write(f"**Height:** {block['height']}")
                st.write(f"**Transaction count:** {block['tx_count']}")
                st.write(f"**Difficulty:** {block['difficulty']}")

                header_bytes = build_block_header(block)
                hash_bytes = double_sha256(header_bytes)
                computed_hash = hash_bytes[::-1].hex()

                target = bits_to_target(block["bits"])
                hash_int = int.from_bytes(hash_bytes, byteorder="little")
                pow_valid = hash_int <= target
                hash_matches_api = computed_hash == block["id"]
                leading_zero_bits = count_leading_zero_bits(computed_hash)

                st.subheader("Local Proof of Work verification")
                st.write(f"**80-byte header (hex):** `{header_bytes.hex()}`")
                st.write(f"**Computed double SHA-256 hash:** `{computed_hash}`")
                st.write(f"**Hash matches API block id:** {hash_matches_api}")
                st.write(f"**Decoded target:** `{target:064x}`")
                st.write(f"**Hash below target:** {pow_valid}")
                st.write(f"**Leading zero bits in hash:** {leading_zero_bits}")

                if hash_matches_api and pow_valid:
                    st.success(
                        "Local verification successful: the reconstructed header produces the same block hash and satisfies the Proof of Work target."
                    )
                else:
                    st.error(
                        "Local verification failed: the computed hash does not match the API hash or does not satisfy the target."
                    )

                st.info(
                    "Bitcoin stores several header fields in little-endian format. "
                    "To verify Proof of Work correctly, we must rebuild the 80-byte header in the right byte order before applying double SHA-256."
                )

            except Exception as exc:
                st.error(f"Error fetching block: {exc}")