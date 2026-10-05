from __future__ import annotations
import os
import gurobipy as gp

def credentials_from_env():
    aid = os.environ.get("GRB_WLSACCESSID", "").strip()
    secret = os.environ.get("GRB_WLSSECRET", "").strip()
    lid = os.environ.get("GRB_LICENSEID", "").strip()
    if not aid or not secret or not lid:
        raise RuntimeError("Missing GRB_WLSACCESSID, GRB_WLSSECRET, or GRB_LICENSEID")
    try:
        lid_int = int(lid)
    except ValueError as exc:
        raise RuntimeError("GRB_LICENSEID must be numeric") from exc
    if lid_int <= 0:
        raise RuntimeError("GRB_LICENSEID must be positive")
    return aid, secret, lid_int

def new_env():
    aid, secret, lid = credentials_from_env()
    return gp.Env(params={
        "WLSACCESSID": aid,
        "WLSSECRET": secret,
        "LICENSEID": lid,
        "OutputFlag": 0,
    })
