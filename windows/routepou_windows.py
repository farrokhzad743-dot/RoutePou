"""RoutePou Windows companion: authenticated HTTP and SOCKS5 TCP bridges."""
import socket, ssl, hashlib, hmac, threading, tkinter as tk
from pairing import parse_pairing_payload
from tkinter import messagebox
import winreg

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
LOCAL_HOST, LOCAL_HTTP_PORT, LOCAL_SOCKS_PORT = "127.0.0.1", 17878, 17879
PHONE_PORT_DEFAULT = "8788"
http_server = None
socks_server = None
stop_event = threading.Event()
previous = {}
active_sockets = set()
socket_lock = threading.Lock()




def read_reg(name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
            return winreg.QueryValueEx(k, name)
    except OSError:
        return None


def write_reg(name, value, typ):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
        winreg.SetValueEx(k, name, 0, typ, value)


def refresh_windows():
    try:
        import ctypes
        ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
        ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
    except Exception:
        pass


def track(sock):
    with socket_lock:
        active_sockets.add(sock)


def untrack(sock):
    with socket_lock:
        active_sockets.discard(sock)


def relay(a, b):
    def cp(src, dst):
        try:
            while not stop_event.is_set():
                data = src.recv(65536)
                if not data:
                    break
                dst.sendall(data)
        except OSError:
            pass
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass
    t1 = threading.Thread(target=cp, args=(a, b), daemon=True)
    t2 = threading.Thread(target=cp, args=(b, a), daemon=True)
    t1.start(); t2.start(); t1.join(); t2.join()


def recv_exact(sock, count):
    data = bytearray()
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise ConnectionError("Unexpected end of SOCKS5 handshake")
        data.extend(chunk)
    return bytes(data)


def tls_phone_socket(phone, port, fingerprint):
    raw = socket.create_connection((phone, int(port)), timeout=12)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Trust is established by the explicit SHA-256 pin below.
    wrapped = context.wrap_socket(raw, server_hostname="routepou.local")
    actual = hashlib.sha256(wrapped.getpeercert(binary_form=True)).hexdigest().upper()
    expected = "".join(ch for ch in fingerprint.upper() if ch in "0123456789ABCDEF")
    if len(expected) != 64 or not hmac.compare_digest(actual, expected):
        wrapped.close()
        raise ssl.SSLError("TLS certificate fingerprint mismatch. Verify the fingerprint shown by the Android app.")
    return wrapped


def handle_http_client(client, phone, port, token, fingerprint):
    upstream = None
    track(client)
    try:
        client.settimeout(30)
        data = bytearray()
        while b"\r\n\r\n" not in data and len(data) < 32768:
            part = client.recv(4096)
            if not part:
                return
            data.extend(part)
        if b"\r\n\r\n" not in data:
            return
        head, rest = bytes(data).split(b"\r\n\r\n", 1)
        lines = [line for line in head.split(b"\r\n") if not line.lower().startswith(b"x-routepou-key:")]
        lines.append(("X-RoutePou-Key: " + token).encode("ascii"))
        upstream = tls_phone_socket(phone, port, fingerprint)
        track(upstream)
        upstream.sendall(b"\r\n".join(lines) + b"\r\n\r\n" + rest)
        client.settimeout(None); upstream.settimeout(None)
        relay(client, upstream)
    except OSError:
        pass
    finally:
        for s in (client, upstream):
            if s:
                untrack(s)
                try: s.close()
                except OSError: pass


def handle_socks_client(client, phone, port, token, fingerprint):
    """Local unauthenticated SOCKS5 endpoint; authenticates to phone using RFC1929."""
    upstream = None
    track(client)
    try:
        client.settimeout(30)
        ver, nmethods = recv_exact(client, 2)
        if ver != 5 or nmethods < 1:
            return
        recv_exact(client, nmethods)
        # Local apps connect to loopback only; the bridge performs phone-side auth.
        client.sendall(b"\x05\x00")
        upstream = tls_phone_socket(phone, port, fingerprint)
        track(upstream); upstream.settimeout(30)
        upstream.sendall(b"\x05\x01\x02")
        if recv_exact(upstream, 2) != b"\x05\x02":
            client.sendall(b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")
            return
        user = b"routepou"; pwd = token.encode("ascii")
        upstream.sendall(b"\x01" + bytes([len(user)]) + user + bytes([len(pwd)]) + pwd)
        if recv_exact(upstream, 2) != b"\x01\x00":
            client.sendall(b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")
            return
        request_head = recv_exact(client, 4)
        atyp = request_head[3]
        if atyp == 1:
            address = recv_exact(client, 4)
        elif atyp == 3:
            size = recv_exact(client, 1)
            address = size + recv_exact(client, size[0])
        elif atyp == 4:
            address = recv_exact(client, 16)
        else:
            client.sendall(b"\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00")
            return
        request = request_head + address + recv_exact(client, 2)
        upstream.sendall(request)
        reply = recv_exact(upstream, 4)
        atyp_reply = reply[3]
        if atyp_reply == 1:
            reply += recv_exact(upstream, 6)
        elif atyp_reply == 4:
            reply += recv_exact(upstream, 18)
        elif atyp_reply == 3:
            n = recv_exact(upstream, 1); reply += n + recv_exact(upstream, n[0] + 2)
        client.sendall(reply)
        if reply[1] == 0:
            client.settimeout(None); upstream.settimeout(None)
            relay(client, upstream)
    except (OSError, ConnectionError, IndexError):
        pass
    finally:
        for s in (client, upstream):
            if s:
                untrack(s)
                try: s.close()
                except OSError: pass


def server_loop(host, local_port, handler, phone, phone_port, token, fingerprint):
    global http_server, socks_server
    server = socket.socket(); server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, local_port)); server.listen(64); server.settimeout(1)
    if local_port == LOCAL_HTTP_PORT: http_server = server
    else: socks_server = server
    while not stop_event.is_set():
        try: client, _ = server.accept()
        except socket.timeout: continue
        except OSError: break
        threading.Thread(target=handler, args=(client, phone, phone_port, token, fingerprint), daemon=True).start()
    try: server.close()
    except OSError: pass
    if local_port == LOCAL_HTTP_PORT: http_server = None
    else: socks_server = None


def start_bridges(phone, port, token, fingerprint):
    stop_event.clear()
    threading.Thread(target=server_loop, args=(LOCAL_HOST, LOCAL_HTTP_PORT, handle_http_client, phone, port, token, fingerprint), daemon=True).start()
    threading.Thread(target=server_loop, args=(LOCAL_HOST, LOCAL_SOCKS_PORT, handle_socks_client, phone, port, token, fingerprint), daemon=True).start()


def connect():
    if http_server or socks_server:
        return
    phone = ip.get().strip(); token = key_var.get().strip(); port = port_var.get().strip(); fingerprint = fingerprint_var.get().strip()
    try:
        socket.inet_aton(phone)
        if not token or len(token) < 16 or not port.isdigit() or not 1 <= int(port) <= 65535 or len("".join(c for c in fingerprint if c in "0123456789abcdefABCDEF")) != 64:
            raise ValueError("Check the pairing key and port.")
        test = tls_phone_socket(phone, port, fingerprint); test.close()
        start_bridges(phone, port, token, fingerprint)
        for name in ("ProxyEnable", "ProxyServer", "ProxyOverride"):
            previous[name] = read_reg(name)
        write_reg("ProxyEnable", 1, winreg.REG_DWORD)
        write_reg("ProxyServer", f"http={LOCAL_HOST}:{LOCAL_HTTP_PORT};https={LOCAL_HOST}:{LOCAL_HTTP_PORT}", winreg.REG_SZ)
        write_reg("ProxyOverride", "localhost;127.*;<local>", winreg.REG_SZ)
        refresh_windows()
        status.config(text=f"Connected · HTTP {LOCAL_HTTP_PORT} · SOCKS5 {LOCAL_SOCKS_PORT}", fg="#35c77a")
    except Exception as e:
        stop_event.set()
        messagebox.showerror("RoutePou", str(e))


def disconnect():
    global http_server, socks_server
    stop_event.set()
    for srv in (http_server, socks_server):
        if srv:
            try: srv.close()
            except OSError: pass
    with socket_lock:
        sockets = list(active_sockets)
    for sock in sockets:
        try: sock.shutdown(socket.SHUT_RDWR)
        except OSError: pass
        try: sock.close()
        except OSError: pass
    for name, old in previous.items():
        try:
            if old is None:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as k:
                    winreg.DeleteValue(k, name)
            else:
                write_reg(name, old[0], old[1])
        except OSError:
            pass
    previous.clear(); refresh_windows()
    status.config(text="Disconnected · previous settings restored", fg="#e25b68")


root = tk.Tk(); root.title("RoutePou · Pou Network Tools"); root.geometry("540x680"); root.resizable(False, False); root.configure(bg="#101114")
tkfont = ("Segoe UI", 10)
tk.Label(root, text="RoutePou", font=("Segoe UI", 30, "bold"), fg="white", bg="#101114").pack(pady=(22, 2))
tk.Label(root, text="Phone VPN sharing · Windows companion", font=tkfont, fg="#b9bbc4", bg="#101114").pack(pady=(0, 18))
form = tk.Frame(root, bg="#101114"); form.pack(padx=42, fill="x")
def field(label, var, show=None):
    tk.Label(form, text=label, fg="white", bg="#101114").pack(anchor="w", pady=(8, 3))
    tk.Entry(form, textvariable=var, show=show, font=("Segoe UI", 11), width=48).pack(fill="x")
ip = tk.StringVar(value="192.168.43.1"); port_var = tk.StringVar(value=PHONE_PORT_DEFAULT); key_var = tk.StringVar()
field("Phone hotspot IPv4", ip); field("Android service port", port_var); field("Pairing key", key_var, show="•")
fingerprint_var = tk.StringVar()
field("Android TLS SHA-256 fingerprint (64 hex characters)", fingerprint_var)
qr_var = tk.StringVar()
field("Or paste decoded RoutePou QR text here", qr_var)
def import_pairing_qr():
    try:
        host, qr_port, qr_key, qr_fp = parse_pairing_payload(qr_var.get())
        ip.set(host); port_var.set(qr_port); key_var.set(qr_key); fingerprint_var.set(qr_fp)
        status.config(text="Pairing details imported · ready to connect", fg="#35c77a")
    except Exception as exc:
        messagebox.showerror("RoutePou pairing", str(exc))
tk.Button(root, text="Import pairing QR text", command=import_pairing_qr, bg="#30343d", fg="white", pady=6).pack()
buttons = tk.Frame(root, bg="#101114"); buttons.pack(pady=14)
tk.Button(buttons, text="Connect", command=connect, bg="#d51f35", fg="white", width=17, pady=9).pack(side="left", padx=8)
tk.Button(buttons, text="Disconnect", command=disconnect, width=17, pady=9).pack(side="left", padx=8)
status = tk.Label(root, text="Disconnected", fg="#e25b68", bg="#101114", font=("Segoe UI", 10, "bold")); status.pack(pady=(0, 12))
info = "TLS encrypted link to phone: port 8788\nHTTP proxy: 127.0.0.1:17878 (system proxy)\nSOCKS5 TCP: 127.0.0.1:17879 (configure per-app)\nTLS 1.2/1.3 with SHA-256 certificate pinning. QR pairing import is supported. UDP and full-device tunneling are not included yet.\nUse only on your own trusted hotspot."
tk.Label(root, text=info, fg="#9b9da6", bg="#101114", font=("Segoe UI", 9), justify="center").pack(pady=12)
root.protocol("WM_DELETE_WINDOW", lambda: (disconnect(), root.destroy()))
root.mainloop()
