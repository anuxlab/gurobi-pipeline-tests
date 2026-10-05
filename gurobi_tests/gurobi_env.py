from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import gurobipy as gp

REQUIRED = ("GRB_WLSACCESSID", "GRB_WLSSECRET", "GRB_LICENSEID")


def credentials_from_env() -> dict[str, str | int]:
    values = {key: os.getenv(key, "").strip() for key in REQUIRED}
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing Gurobi WLS environment variables: " + ", ".join(missing)
        )
    try:
        license_id = int(str(values["GRB_LICENSEID"]))
    except ValueError as exc:
        raise RuntimeError("GRB_LICENSEID must be an integer") from exc
    if license_id <= 0:
        raise RuntimeError("GRB_LICENSEID must be a positive integer")
    return {
        "GRB_WLSACCESSID": str(values["GRB_WLSACCESSID"]),
        "GRB_WLSSECRET": str(values["GRB_WLSSECRET"]),
        "GRB_LICENSEID": license_id,
    }


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


@contextmanager
def gurobi_env() -> Iterator[gp.Env]:
    env = new_env()
    try:
        yield env
    finally:
        env.dispose()
