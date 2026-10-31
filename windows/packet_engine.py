"""RoutePou v0.8 packet validation and framing primitives.

This module intentionally does not alter Windows routes or DNS settings. It is
safe groundwork for a future authenticated packet transport, not a full VPN.
"""
from __future__ import annotations
from dataclasses import dataclass
import ipaddress
import socket
import struct
from typing import BinaryIO

DEFAULT_MTU = 1280
MAX_MTU = 1500
MAX_PACKET = 65535
FRAME_HEADER = struct.Struct("!I")

class PacketError(ValueError):
    pass

@dataclass(frozen=True)
class PacketInfo:
    version: int
    source: str
    destination: str
    protocol: int
    length: int
    is_dns: bool


def inspect_packet(packet: bytes, mtu: int = DEFAULT_MTU) -> PacketInfo:
    if not isinstance(packet, (bytes, bytearray)) or len(packet) < 1:
        raise PacketError("empty or invalid packet")
    if not 576 <= mtu <= MAX_MTU:
        raise PacketError("MTU must be between 576 and 1500")
    if len(packet) > mtu:
        raise PacketError(f"packet exceeds configured MTU ({len(packet)} > {mtu})")
    version = packet[0] >> 4
    if version == 4:
        if len(packet) < 20: raise PacketError("truncated IPv4 header")
        ihl = (packet[0] & 0x0f) * 4
        if ihl < 20 or len(packet) < ihl: raise PacketError("invalid IPv4 header length")
        total = struct.unpack_from("!H", packet, 2)[0]
        if total != len(packet) or total < ihl: raise PacketError("IPv4 total length mismatch")
        proto = packet[9]
        src = str(ipaddress.IPv4Address(packet[12:16])); dst = str(ipaddress.IPv4Address(packet[16:20]))
        dns = proto == 17 and total >= ihl + 8 and (struct.unpack_from("!H", packet, ihl + 2)[0] == 53)
        return PacketInfo(4, src, dst, proto, total, dns)
    if version == 6:
        if len(packet) < 40: raise PacketError("truncated IPv6 header")
        payload = struct.unpack_from("!H", packet, 4)[0]
        if payload + 40 != len(packet): raise PacketError("IPv6 payload length mismatch")
        proto = packet[6]
        src = str(ipaddress.IPv6Address(packet[8:24])); dst = str(ipaddress.IPv6Address(packet[24:40]))
        # DNS detection for direct UDP next-header only; extension headers need a parser.
        dns = proto == 17 and payload >= 8 and struct.unpack_from("!H", packet, 42)[0] == 53
        return PacketInfo(6, src, dst, proto, len(packet), dns)
    raise PacketError("only IPv4 and IPv6 packets are supported")


def write_frame(stream: BinaryIO, packet: bytes, mtu: int = DEFAULT_MTU) -> None:
    inspect_packet(packet, mtu)
    stream.write(FRAME_HEADER.pack(len(packet)))
    stream.write(packet)
    if hasattr(stream, "flush"): stream.flush()


def read_exact(stream: BinaryIO, count: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < count:
        part = stream.read(count - len(chunks))
        if not part: raise EOFError("transport closed during packet frame")
        chunks.extend(part)
    return bytes(chunks)


def read_frame(stream: BinaryIO, mtu: int = DEFAULT_MTU) -> bytes:
    (length,) = FRAME_HEADER.unpack(read_exact(stream, FRAME_HEADER.size))
    if not 1 <= length <= mtu: raise PacketError("invalid frame length")
    packet = read_exact(stream, length)
    inspect_packet(packet, mtu)
    return packet


def resolve_dns_upstream(host: str, port: int = 53) -> tuple[str, int]:
    """Resolve a configured DNS upstream; no system DNS settings are changed."""
    if not 1 <= port <= 65535: raise ValueError("invalid DNS port")
    return socket.gethostbyname(host), port
