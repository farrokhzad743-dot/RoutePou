import ast
from pathlib import Path

SOURCE = Path(__file__).parents[1] / "windows" / "wintun_session.py"


def test_wintun_session_module_parses():
    ast.parse(SOURCE.read_text(encoding="utf-8"))


def test_packet_io_and_cleanup_contract_present():
    source = SOURCE.read_text(encoding="utf-8")
    for symbol in ("WintunCreateAdapter", "WintunStartSession", "WintunReceivePacket",
                   "WintunReleaseReceivePacket", "WintunAllocateSendPacket",
                   "WintunSendPacket", "WintunEndSession", "WintunCloseAdapter"):
        assert symbol in source


def test_no_automatic_route_or_dns_mutation():
    source = SOURCE.read_text(encoding="utf-8").lower()
    assert "new-netroute" not in source
    assert "set-dnsclientserveraddress" not in source
