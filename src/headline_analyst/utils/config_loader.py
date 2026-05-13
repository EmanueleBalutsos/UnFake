import os
import re
import yaml
from dotenv import load_dotenv
from pathlib import Path

"""Utility to load and resolve configuration from a YAML file, supporting environment variable substitution 
(used for API keys associated to AI models providers)."""

load_dotenv()

# Go from src/headline_analyst/config/loader.py
#  up to project root where config.yaml is located
CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.yaml"

def _resolve_env_vars(value: str) -> str:
    """Replace ${VAR_NAME} with the actual env variable."""

    return re.sub(
        r"\$\{(\w+)\}",
        lambda m: os.environ.get(m.group(1), m.group(0)),
        value
    )

def _resolve_dict(d: dict) -> dict:
    resolved = {}
    for k, v in d.items():
        if isinstance(v, str):
            resolved[k] = _resolve_env_vars(v)
        elif isinstance(v, dict):
            resolved[k] = _resolve_dict(v)
        else:
            resolved[k] = v
    return resolved

def load_config(path: str = CONFIG_PATH) -> dict:
    """
    Load a config dictionary in the config.yaml file, specifying which models to use for which task at run time.
    """
    with open(path) as f:
        raw = yaml.safe_load(f)
    return _resolve_dict(raw)