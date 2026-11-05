import socket
from concurrent.futures import ThreadPoolExecutor

base = "192.168.1."
ports = [80,443,22,445,139,8080]

def scan_host(ip):
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        try:
            s.connect((ip, port))
            banner = b""
            try:
                banner = s.recv(1024)
            except (socket.timeout, OSError):
                pass
            if banner == b"":
                try:
                    s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = s.recv(1024)
                except (socket.timeout, OSError):
                    pass
            clean = banner.decode(errors="ignore").strip().replace("\r\n", " ")
            print(f"Host {ip} is up (port {port}) - {clean}")
            s.close()
            break
        except ConnectionRefusedError:
            print(f"Host {ip} is up")
            s.close()
            break
        except (socket.timeout, OSError):
            s.close()


ips = [f"{base}{i}" for i in range(1,255)]

with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(scan_host, ips)