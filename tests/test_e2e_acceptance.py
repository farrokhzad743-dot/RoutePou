import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'windows'))
from e2e_acceptance import evaluate, AcceptanceError, State, REQUIRED

def complete():
    return {"checks": {key: True for key in REQUIRED}}

def test_handshake_alone_is_not_full_tunnel():
    r = evaluate({"checks": {"handshake_recent": True}})
    assert r.state == State.HANDSHAKE_ONLY
    assert "tcp_through_phone" in r.missing

def test_all_gates_are_required():
    report = complete(); report["checks"]["udp_through_phone"] = False
    r = evaluate(report)
    assert r.state == State.HANDSHAKE_ONLY
    assert "udp_through_phone" in r.failed

def test_full_acceptance_requires_every_gate():
    assert evaluate(complete()).state == State.ACCEPTED

def test_missing_handshake_blocks():
    assert evaluate({"checks": {}}).state == State.BLOCKED

def test_private_key_is_rejected():
    report = complete(); report["clientPrivateKey"] = "secret"
    try: evaluate(report)
    except AcceptanceError: pass
    else: assert False, "secret-bearing report accepted"

def test_qr_pairing_and_endpoint_are_required_even_if_data_plane_passes():
    report = complete(); report["checks"]["pairing_fresh"] = False
    assert evaluate(report).state == State.DATA_PLANE_PARTIAL
