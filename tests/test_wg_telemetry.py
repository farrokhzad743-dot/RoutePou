import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'windows'))
from wg_telemetry import parse_wg_dump

KEY='A'*43+'='

def dump(handshake='990', rx='1200', tx='3400'):
    return '\t'.join(['private','public','51820','off'])+'\n'+ '\t'.join([KEY,'(none)','192.168.43.1:51820','0.0.0.0/0',handshake,rx,tx,'25'])+'\n'

def test_fresh_handshake_and_counters():
    t=parse_wg_dump(dump(), now=1000)
    assert t.handshake_ok and t.received_bytes == 1200 and t.sent_bytes == 3400
    assert t.peers[0].handshake_age_seconds == 10

def test_stale_handshake_is_not_connected():
    t=parse_wg_dump(dump(handshake='1'), now=1000)
    assert not t.handshake_ok

def test_never_handshaken_is_not_connected():
    t=parse_wg_dump(dump(handshake='0'), now=1000)
    assert not t.handshake_ok and t.peers[0].handshake_age_seconds is None

def test_malformed_peer_rejected():
    with pytest.raises(ValueError): parse_wg_dump('a\tb\t51820\toff\nx\ty')

def test_empty_dump_rejected():
    with pytest.raises(ValueError): parse_wg_dump('')
