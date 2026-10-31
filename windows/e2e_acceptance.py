"""Evidence-based RoutePou end-to-end acceptance gate (read-only).

This module never changes routes, DNS, firewall, adapters, or services. It only
classifies a supplied, sanitized test report. A handshake alone is insufficient.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any
import json

class AcceptanceError(ValueError):
    pass

class State(str, Enum):
    BLOCKED = "BLOCKED"
    HANDSHAKE_ONLY = "HANDSHAKE_ONLY"
    DATA_PLANE_PARTIAL = "DATA_PLANE_PARTIAL"
    ACCEPTED = "ACCEPTED"

REQUIRED = (
    "pairing_fresh", "endpoint_reachable", "handshake_recent",
    "tcp_through_phone", "udp_through_phone", "dns_through_tunnel",
    "ipv6_no_leak", "fail_closed_on_peer_loss", "recovery_clean",
    "disconnect_rollback_clean",
)

@dataclass(frozen=True)
class AcceptanceResult:
    state: State
    passed: tuple[str, ...]
    failed: tuple[str, ...]
    missing: tuple[str, ...]
    reason: str


def evaluate(report: dict[str, Any]) -> AcceptanceResult:
    if not isinstance(report, dict):
        raise AcceptanceError("report must be a JSON object")
    # Reject accidental secret-bearing reports instead of copying them through.
    forbidden = {"private_key", "clientPrivateKey", "serverPrivateKey", "qr", "pairing_token", "token"}
    def walk(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if str(k).lower() in {x.lower() for x in forbidden}:
                    raise AcceptanceError("secret-bearing evidence is not accepted")
                walk(v)
        elif isinstance(value, list):
            for v in value: walk(v)
    walk(report)
    checks = report.get("checks")
    if not isinstance(checks, dict):
        raise AcceptanceError("checks object is required")
    passed = tuple(k for k in REQUIRED if checks.get(k) is True)
    failed = tuple(k for k in REQUIRED if checks.get(k) is False)
    missing = tuple(k for k in REQUIRED if k not in checks)
    if checks.get("handshake_recent") is not True:
        state, reason = State.BLOCKED, "A recent WireGuard handshake has not been proven."
    elif any(checks.get(k) is not True for k in REQUIRED[3:]):
        state, reason = State.HANDSHAKE_ONLY, "Handshake exists, but full-tunnel data-plane and safety gates are incomplete."
    elif any(checks.get(k) is not True for k in REQUIRED[:2]):
        state, reason = State.DATA_PLANE_PARTIAL, "Traffic tests passed but pairing/endpoint acceptance is incomplete."
    else:
        state, reason = State.ACCEPTED, "All defined end-to-end acceptance checks passed in the supplied test report."
    return AcceptanceResult(state, passed, failed, missing, reason)


def main():
    import argparse, pathlib, sys
    p = argparse.ArgumentParser(description="Classify a sanitized RoutePou E2E test report (read-only).")
    p.add_argument("report", help="Path to sanitized JSON report; do not include secrets")
    p.add_argument("--json", action="store_true", help="Print machine-readable result")
    a = p.parse_args()
    try:
        data = json.loads(pathlib.Path(a.report).read_text(encoding="utf-8"))
        result = evaluate(data)
    except (OSError, json.JSONDecodeError, AcceptanceError) as exc:
        print(f"خطا: {exc}", file=sys.stderr); return 2
    payload = {"state": result.state.value, "passed": result.passed, "failed": result.failed,
               "missing": result.missing, "reason": result.reason}
    if a.json: print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        labels = {"BLOCKED":"مسدود", "HANDSHAKE_ONLY":"فقط Handshake", "DATA_PLANE_PARTIAL":"داده ناقص", "ACCEPTED":"تأییدشده"}
        print(f"وضعیت RoutePou: {labels[result.state.value]}\n{result.reason}")
        if result.failed: print("ناموفق: " + ", ".join(result.failed))
        if result.missing: print("ثبت‌نشده: " + ", ".join(result.missing))
    return 0 if result.state == State.ACCEPTED else 1

if __name__ == "__main__": raise SystemExit(main())
