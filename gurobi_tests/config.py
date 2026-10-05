from pathlib import Path
import os
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str = "config/development.yaml") -> dict:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML configuration: {path}")
    return data


def instance_path(instance_name: str) -> Path:
    return ROOT / "instances" / instance_name


def configured_instances() -> list[str]:
    cfg = load_yaml()
    return list(cfg["tests"]["evrp_instances"])
