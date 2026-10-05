import os
import gurobipy as gp

REQUIRED = ("GRB_WLSACCESSID", "GRB_WLSSECRET", "GRB_LICENSEID")


def credentials_from_env() -> dict:
    values = {k: os.getenv(k, "").strip() for k in REQUIRED}
    missing = [k for k, v in values.items() if not v]
    if missing:
        raise RuntimeError(
            "Missing Gurobi WLS environment variables: " + ", ".join(missing)
        )
    try:
        values["GRB_LICENSEID"] = int(values["GRB_LICENSEID"])
    except ValueError as exc:
        raise RuntimeError("GRB_LICENSEID must be an integer") from exc
    return values


def new_env() -> gp.Env:
    c = credentials_from_env()
    return gp.Env(
        params={
            "WLSACCESSID": c["GRB_WLSACCESSID"],
            "WLSSECRET": c["GRB_WLSSECRET"],
            "LICENSEID": c["GRB_LICENSEID"],
            "OutputFlag": 0,
        }
    )
