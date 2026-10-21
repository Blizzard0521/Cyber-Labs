import socket
from concurrent.futures import ThreadPoolExecutor

host = "scanme.nmap.org"

def scan_port(port):
    #Create Sockets
    # ---Probe 1: null probe (listen first) ---         
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((host, port))
        banner = b""
        try:
            banner = s.recv(1024)
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
        s.close()

        # --- Probe 2: HTTP probe (onlyu if null probe found nothing) ---
        if banner == b"":
            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s2.settimeout(1)
            try:
                s2.connect((host, port))
                s2.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = s2.recv(1024)
            except (socket.timeout, ConnectionRefusedError, OSError):
                pass
            s2.close()

        clean = banner.decode(errors="ignore").strip().replace("\r\n", " ")
        print(f"Port {port} open - {clean}")

    except(socket.timeout):
        pass


#Instead of a for loop, hand all ports to a pool of workers:

with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(scan_port, range(1,101))
    # Meaning: run scan_port for every number in the range, across up to 100 worker threads at once
    # max_workers = how many threads run simultaneously. Faster but heavier



