from __future__ import annotations

import os
import gurobipy as gp


def _wls_values() -> dict[str, str]:
    keys = ("GRB_WLSACCESSID", "GRB_WLSSECRET", "GRB_LICENSEID")
    return {key: os.getenv(key, "").strip() for key in keys}


def new_env() -> gp.Env:
    values = _wls_values()

    present = [bool(value) for value in values.values()]
    if any(present) and not all(present):
        missing = [key for key, value in values.items() if not value]
        raise RuntimeError(
            "Incomplete WLS configuration. Missing: " + ", ".join(missing)
        )

    # CI uses explicit WLS environment variables.
    if all(present):
        try:
            license_id = int(values["GRB_LICENSEID"])
        except ValueError as exc:
            raise RuntimeError("GRB_LICENSEID must be an integer.") from exc

        return gp.Env(
            params={
                "WLSACCESSID": values["GRB_WLSACCESSID"],
                "WLSSECRET": values["GRB_WLSSECRET"],
                "LICENSEID": license_id,
                "OutputFlag": 0,
            }
        )

    # Local development can rely on ~/gurobi.lic or GRB_LICENSE_FILE.
    return gp.Env(params={"OutputFlag": 0})


def describe_license(env: gp.Env) -> str:
    try:
        return str(env.getParamInfo("LicenseID"))
    except gp.GurobiError:
        return "License information unavailable"
