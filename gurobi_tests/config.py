from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str | None = None) -> dict[str, Any]:
    raw = path or os.getenv("GUROBI_CONFIG", "config/development.yaml")
    cfg_path = Path(raw)
    if not cfg_path.is_absolute():
        cfg_path = ROOT / cfg_path
    if not cfg_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def instance_path(name: str, config_path: str | None = None) -> Path:
    cfg = load_config(config_path)
    directory = cfg.get("tests", {}).get("evrp_instance_dir", "instances")
    return ROOT / directory / name
