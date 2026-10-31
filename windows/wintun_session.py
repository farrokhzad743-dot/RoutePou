"""Safe Wintun adapter/session primitives (Windows only).

This module exposes packet I/O but deliberately does not alter routes or DNS.
A higher-level authenticated transport must consume/produce IP packets before
full-tunnel mode can be enabled.
"""
from __future__ import annotations
import ctypes
import os
import uuid
from ctypes import wintypes

RING_CAPACITY = 0x400000  # 4 MiB, Wintun requires a power of two in its limits.

class WintunError(RuntimeError):
    pass

class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

    @classmethod
    def from_uuid(cls, value: uuid.UUID) -> "GUID":
        raw = value.bytes_le
        obj = cls()
        ctypes.memmove(ctypes.byref(obj), raw, 16)
        return obj


def _last_error(operation: str) -> WintunError:
    code = ctypes.get_last_error()
    return WintunError(f"{operation} failed (Windows error {code}).")


class WintunSession:
    """Owns one Wintun adapter and ring session; caller owns routing policy."""
    def __init__(self, name: str = "RoutePou", tunnel_type: str = "RoutePou",
                 capacity: int = RING_CAPACITY, adapter_guid: str | None = None):
        if os.name != "nt":
            raise WintunError("Wintun is available only on Windows.")
        if capacity < 0x20000 or capacity > 0x4000000 or capacity & (capacity - 1):
            raise ValueError("capacity must be a power of two from 128 KiB to 64 MiB")
        dll_path = os.path.join(os.path.dirname(__file__), "wintun.dll")
        if not os.path.isfile(dll_path):
            raise WintunError("wintun.dll is missing beside this module.")
        self.dll = ctypes.WinDLL(dll_path, use_last_error=True)
        self.adapter = None
        self.session = None
        self._bind()
        guid = GUID.from_uuid(uuid.UUID(adapter_guid)) if adapter_guid else None
        guid_ptr = ctypes.byref(guid) if guid else None
        self.adapter = self.dll.WintunCreateAdapter(name, tunnel_type, guid_ptr)
        if not self.adapter:
            raise _last_error("WintunCreateAdapter")
        self.session = self.dll.WintunStartSession(self.adapter, capacity)
        if not self.session:
            self.dll.WintunCloseAdapter(self.adapter)
            self.adapter = None
            raise _last_error("WintunStartSession")

    def _bind(self):
        d = self.dll
        d.WintunCreateAdapter.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(GUID)]
        d.WintunCreateAdapter.restype = ctypes.c_void_p
        d.WintunStartSession.argtypes = [ctypes.c_void_p, wintypes.DWORD]
        d.WintunStartSession.restype = ctypes.c_void_p
        d.WintunEndSession.argtypes = [ctypes.c_void_p]
        d.WintunEndSession.restype = None
        d.WintunCloseAdapter.argtypes = [ctypes.c_void_p]
        d.WintunCloseAdapter.restype = None
        d.WintunReceivePacket.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
        d.WintunReceivePacket.restype = ctypes.POINTER(ctypes.c_ubyte)
        d.WintunReleaseReceivePacket.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte)]
        d.WintunReleaseReceivePacket.restype = None
        d.WintunAllocateSendPacket.argtypes = [ctypes.c_void_p, wintypes.DWORD]
        d.WintunAllocateSendPacket.restype = ctypes.POINTER(ctypes.c_ubyte)
        d.WintunSendPacket.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte)]
        d.WintunSendPacket.restype = None

    def receive(self) -> bytes | None:
        """Return one IP packet, or None when the receive ring is empty."""
        if not self.session:
            raise WintunError("Session is closed.")
        size = wintypes.DWORD()
        packet = self.dll.WintunReceivePacket(self.session, ctypes.byref(size))
        if not packet:
            code = ctypes.get_last_error()
            if code == 259:  # ERROR_NO_MORE_ITEMS
                return None
            raise WintunError(f"WintunReceivePacket failed (Windows error {code}).")
        try:
            return ctypes.string_at(packet, size.value)
        finally:
            self.dll.WintunReleaseReceivePacket(self.session, packet)

    def send(self, packet: bytes) -> None:
        """Inject one complete IPv4/IPv6 packet into the virtual adapter."""
        if not self.session:
            raise WintunError("Session is closed.")
        if not packet or len(packet) > 0xFFFF:
            raise ValueError("packet must contain 1..65535 bytes")
        target = self.dll.WintunAllocateSendPacket(self.session, len(packet))
        if not target:
            raise _last_error("WintunAllocateSendPacket")
        ctypes.memmove(target, packet, len(packet))
        self.dll.WintunSendPacket(self.session, target)

    def close(self) -> None:
        if self.session:
            self.dll.WintunEndSession(self.session)
            self.session = None
        if self.adapter:
            self.dll.WintunCloseAdapter(self.adapter)
            self.adapter = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
