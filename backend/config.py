import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config() -> dict:
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"config.json not found at {_CONFIG_PATH}. "
            "Copy config.json.example to config.json and fill in your keys."
        )
    with open(_CONFIG_PATH) as f:
        config = json.load(f)

    if not config.get("gemini_api_key") or config["gemini_api_key"] == "YOUR_GEMINI_API_KEY_HERE":
        raise ValueError("gemini_api_key must be set in config.json")

    return config
