"""
Blockchain API client.

Provides helper functions to fetch blockchain data from public APIs.
"""

import requests

BASE_URL = "https://blockchain.info"


def get_latest_block() -> dict:
    """Return the latest block summary."""
    response = requests.get(f"{BASE_URL}/latestblock", timeout=10)
    response.raise_for_status()
    return response.json()


def get_block(block_hash: str) -> dict:
    """Return full details for a block identified by *block_hash*."""
    response = requests.get(
        f"{BASE_URL}/rawblock/{block_hash}", timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_difficulty_history(n_points: int = 100) -> list[dict]:
    """Return the last *n_points* difficulty values as a list of dicts."""
    response = requests.get(
        f"{BASE_URL}/charts/difficulty",
        params={"timespan": "1year", "format": "json", "sampled": "true"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("values", [])[-n_points:]


def get_current_difficulty() -> float:
    """Return the current Bitcoin network difficulty."""
    response = requests.get(f"{BASE_URL}/q/getdifficulty", timeout=10)
    response.raise_for_status()
    return float(response.text)


if __name__ == "__main__":
    latest = get_latest_block()
    block = get_block(latest["hash"])
    difficulty = get_current_difficulty()

    print("Height:", latest["height"])
    print("Hash:", latest["hash"])
    print("Difficulty:", difficulty)
    print("Nonce:", block["nonce"])
    print("Tx count:", block["n_tx"])
    print("Bits:", block["bits"])
    # Leading zeros in the hash are a consequence of the PoW target.
    # The bits field is the compact representation of that target threshold.