import io, struct, unittest
from windows.packet_engine import inspect_packet, write_frame, read_frame, PacketError

def ipv4_udp(src=b'\x0a\x00\x00\x02', dst=b'\x08\x08\x08\x08', dport=53):
    udp = struct.pack('!HHHH', 12345, dport, 8, 0)
    total = 20 + len(udp)
    return struct.pack('!BBHHHBBH4s4s', 0x45, 0, total, 1, 0, 64, 17, 0, src, dst) + udp

class PacketEngineTests(unittest.TestCase):
    def test_ipv4_dns_detection(self):
        p = inspect_packet(ipv4_udp())
        self.assertEqual(p.version, 4); self.assertTrue(p.is_dns)
    def test_frame_roundtrip(self):
        packet = ipv4_udp(dport=443); stream = io.BytesIO()
        write_frame(stream, packet); stream.seek(0)
        self.assertEqual(read_frame(stream), packet)
    def test_reject_bad_length(self):
        with self.assertRaises(PacketError): inspect_packet(ipv4_udp()[:-1])
    def test_reject_mtu(self):
        with self.assertRaises(PacketError): inspect_packet(ipv4_udp(), mtu=576) if len(ipv4_udp()) > 576 else inspect_packet(ipv4_udp(), mtu=575)
    def test_reject_unknown_ip(self):
        with self.assertRaises(PacketError): inspect_packet(b'\x70' + b'0'*40)

if __name__ == '__main__': unittest.main()
