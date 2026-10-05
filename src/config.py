from pathlib import Path
import os
import yaml


ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "config" / "config.yaml"


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


config = load_config()


def get_gurobi_credentials():
    license_cfg = config["gurobi"]["license"]

    access_id = os.environ[license_cfg["access_id_env"]]
    secret = os.environ[license_cfg["secret_env"]]
    license_id = int(os.environ[license_cfg["license_id_env"]])

    return access_id, secret, license_id