"""
Blockchain API client.

Provides helper functions to fetch blockchain data from public APIs.
"""

import requests

BLOCKSTREAM_URL = "https://blockstream.info/api"
BLOCKCHAIN_INFO_URL = "https://blockchain.info"


def get_latest_block() -> dict:
    """Return the latest block summary."""
    height_response = requests.get(f"{BLOCKSTREAM_URL}/blocks/tip/height", timeout=10)
    height_response.raise_for_status()
    height = int(height_response.text)

    hash_response = requests.get(f"{BLOCKSTREAM_URL}/block-height/{height}", timeout=10)
    hash_response.raise_for_status()
    block_hash = hash_response.text.strip()

    return {"height": height, "hash": block_hash}


def get_block(block_hash: str) -> dict:
    """Return full details for a block identified by *block_hash*."""
    response = requests.get(f"{BLOCKSTREAM_URL}/block/{block_hash}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_block_hash_by_height(height: int) -> str:
    """Return the block hash for a given block height."""
    response = requests.get(f"{BLOCKSTREAM_URL}/block-height/{height}", timeout=10)
    response.raise_for_status()
    return response.text.strip()

def get_block_txids(block_hash: str) -> list[str]:
    """Return all transaction IDs for a given block."""
    response = requests.get(f"{BLOCKSTREAM_URL}/block/{block_hash}/txids", timeout=20)
    response.raise_for_status()
    return response.json()


def get_current_difficulty() -> float:
    """Return the current Bitcoin network difficulty."""
    response = requests.get(f"{BLOCKCHAIN_INFO_URL}/q/getdifficulty", timeout=10)
    response.raise_for_status()
    return float(response.text)



def get_difficulty_history(n_points: int = 100) -> list[dict]:
    """Return the last *n_points* difficulty values as a list of dicts."""
    response = requests.get(
        f"{BLOCKCHAIN_INFO_URL}/charts/difficulty",
        params={"timespan": "1year", "format": "json", "sampled": "true"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("values", [])[-n_points:]


if __name__ == "__main__":
    latest = get_latest_block()
    block = get_block(latest["hash"])
    difficulty = get_current_difficulty()

    print("Height:", latest["height"])
    print("Hash:", latest["hash"])
    print("Difficulty:", difficulty)
    print("Nonce:", block["nonce"])
    print("Tx count:", block["tx_count"])
    print("Bits:", block["bits"])
    # Leading zeros in the hash are a consequence of the PoW target.
    # The bits field is the compact representation of that target threshold.