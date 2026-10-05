from pathlib import Path
import os
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str | None = None) -> dict:
    path = path or os.getenv("GUROBI_CONFIG", "config/development.yaml")
    cfg_path = ROOT / path
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def instance_path(name: str) -> Path:
    cfg = load_config()
    return ROOT / cfg["tests"].get("evrp_instance_dir", "instances") / name
