# Network Scanner — Study & Revision Notes

**Project:** `network-scanner.py` (Phase 1, `05-python-security-toolkit/`)
**Built:** 5 Nov 2026 · extends `port-scanner.py`
**How to use this doc:** Part 1 is the theory (including every concept you asked about mid-build). Part 2 walks the build the way you lived it. Part 3 is the annotated final code. Part 4 is the quick-recap lessons list.

---

## PART 1 — The Theory (revision layer)

### 1.1 Host discovery vs port scanning — two questions, one level apart

The port scanner answered: *"which **doors** (ports) are open on **one building** (host)?"*
The network scanner answers one level up: *"which **buildings** (hosts) on this street even exist?"*

```
Host discovery  → which machines on the network are alive?   (THIS tool)
Port scanning   → on a live machine, which ports are open?    (port scanner)
Banner grabbing → what service is behind an open port?        (reused here)
Exploitation    → attack a specific service
```

This is the **recon pipeline**, and it runs in this order on a real engagement: you land on a network (via a compromised box), read its config to learn the range, **discover** live hosts, **scan** the interesting ones, **identify** their services, then attack. Discovery always precedes attack — you can't pick a lock before you've found the house.

### 1.2 The `(host, port)` axis insight (the key realisation)

Every network address is a **pair**: `(host, port)` — the IP picks the *building*, the port picks a *door on that building*. Crucially: **every device has its own full set of 65,535 ports.** Your router's port 80 and your phone's port 80 are completely different doors on different buildings. Port 80 isn't one thing on the network — it's a door that *every* device has.

Both of your scanners knock on `(host, port)` doors. The only difference is **which part you hold fixed and which you loop:**

| | Port scanner | Network scanner |
|---|---|---|
| **Question** | which doors open on one building? | which buildings exist on the street? |
| **Loops** | the **port** (1–100) | the **host** (1–254) |
| **Fixed** | host (`scanme.nmap.org`) | port (80, etc.) + network prefix |
| **Shape** | one building, many doors | many buildings, one door each |

So the two tools are the same knocking along different axes of the same 2D space. (And you scan *other* machines, never your own — scanning yourself/localhost is only for testing.)

### 1.3 How you detect a live host (ICMP vs TCP connect)

**"Is this host alive?"** — two ways to ask:

- **ICMP ping (the "proper" way):** send an echo request (what the `ping` command does). But crafting ICMP in Python needs **raw sockets + admin/root privileges**, and it's painful on Windows. Rough first build.
- **TCP connect (what we used):** try to connect to a common port. If the host responds **in any way** — open OR refused — it's alive (a machine exists there to answer). Only **silence** suggests it's down/filtered. Privilege-free, reuses your port scanner's socket logic. The right learning choice.

**The trick:** you use the port as a *doorbell*. You don't care if the door opens — you care whether *anyone's home to answer the knock*. Any response (even a rejection) proves a device exists at that address.

### 1.4 Listening vs closed vs filtered (the nuance you dug into)

Two separate layers — don't conflate them:

- **Listening / not listening** = whether a *program* has claimed that port (internal cause).
- **Open / closed / filtered** = what *response you get* when you knock (observable result).

| You observe | Program listening? | Host responded? | Meaning |
|---|---|---|---|
| **Open** | ✅ yes | ✅ yes | listening + accepted you |
| **Closed** | ❌ no | ✅ yes | nothing listening, but host *refused* you ("no, nothing here") |
| **Filtered** | ❌ (hidden) | ❌ no | firewall silently **dropped** your knock — silence |

Key corrections you worked through:
- **"Closed" does NOT mean listening.** Only *open* means a program is listening. Closed = nothing listening, but the host was alive enough to say "no."
- **A port is only "open" because a program is actively listening on it** — software opened it to wait for connections. Your router runs a web server → listens on 80 → answers. Your phone runs no web server → nothing on 80.

**Why it matters for discovery:** you care about *"did it respond?"*, not *"is it listening?"* — because **open OR closed both mean the host is ALIVE** (it answered). Only **filtered (silence)** makes a host invisible to you.

### 1.5 The ARP-vs-TCP limitation (why firewalled devices vanish)

You reasoned this out yourself: if a device had nothing on port 80 but was otherwise responsive, you'd get a **closed** (refusal) and detect it. If it stays *completely silent*, your knock was **dropped** — a firewall.

Modern devices (phones, laptops) **silently drop** unsolicited inbound packets by default, rather than refusing them — silence leaks less info to an attacker than a refusal. The side effect: **TCP-connect discovery is blind to well-firewalled devices.** Even multi-port scanning won't fix this — a device that drops knocks on *all* ports stays invisible no matter how many you try.

**What actually finds them** (where this goes next, both need privileges):
- **ARP scanning** — on a local network, devices *must* answer ARP ("who has IP X?") to communicate at all, even with a firewall up. ARP sits *below* the firewall's filtering, so it catches devices that drop TCP. This is what `nmap -sn` does on a LAN and why it finds far more than a TCP sweep.
- **ICMP ping** — sometimes gets through when TCP is filtered.

> **This is the tool's documented limitation** (like the port scanner's nmap-service ceiling): *finds responsive hosts, misses firewalled devices that drop packets; ARP scanning would catch those.* A quiet result means a well-secured network, not a broken tool.

### 1.6 Reading `ipconfig` (real pentest skill)

The first thing you do on a new network: find the adapter *with a gateway* and note its IP + subnet mask.

- **Real adapter** → has a normal private IP (`192.168.1.3`) AND a **Default Gateway** (the router). The gateway is the tell — only a genuinely connected network has one.
- **Dead adapter** → `169.254.x.x` address = **APIPA**, what Windows assigns when an adapter can't reach a DHCP server (failed to join a network). No gateway. Ignore it (usually virtual adapters — VMs, VPNs, unplugged ports).

### 1.7 Subnet mask = which part is network vs host

```
IP:    192.168.1.3
Mask:  255.255.255.0   ("/24")
       └─ 255 = network ─┘ └ 0 = host
```

- `255` octets → **network** part, fixed across all devices on the LAN (`192.168.1`).
- `0` octet → **host** part, varies per device (`.1`–`.254`).

That's *why* your loop varies only the **last octet** — the mask says that's where devices live. `/24` = last octet varies (254 hosts), common home-network size. `/16` (`255.255.0.0`) = two octets vary (~65k hosts).

### 1.8 `errors="ignore"` in `.decode()` (you asked this)

`.decode()` turns **bytes → text**, but not every byte is valid text. When it hits a byte it can't interpret:
- `.decode()` alone → **crashes** with `UnicodeDecodeError`.
- `.decode(errors="ignore")` → **skips** the bad bytes and keeps going. You lose junk, you get a clean string, no crash.

Critical here because you grab banners from **random devices**, some of which send **binary** (not text). Same family as `encoding="latin-1"` on rockyou — "handle messy bytes without crashing." (`errors="replace"` swaps bad bytes for `�` instead of dropping — `"ignore"` is cleaner for banners.)

### 1.9 Why SMB (port 445) gives no readable banner

Port 445 (Windows file sharing) speaks a **binary protocol**, not readable text. So:
- The null-probe `recv` gets raw binary (or nothing clean).
- The HTTP poke is meaningless to SMB — it doesn't speak HTTP, returns nothing useful.
- `.decode(errors="ignore")` strips the unparseable binary → empty string.

So an **empty banner on 445 is correct**, not a bug — it honestly says "host alive, no human-readable banner." And it's exactly why `errors="ignore"` mattered: raw SMB bytes would otherwise *crash* the decode.

### 1.10 Two new Python tools

- **Nested loop:** a loop inside a loop. Outer = hosts, inner = ports. `254 hosts × 6 ports` = up to 1,524 knocks. The inner `break` stops knocking a host once *any* port confirms it alive.
- **List comprehension:** `[f"{base}{i}" for i in range(1, 255)]` builds a list in one line — the compact form of a for-loop that appends. Here it builds all 254 IP strings to hand to the thread pool.

---

## PART 2 — The Build Journey

### Step 1 — Generate the IP range

```python
for i in range(1, 255):
    ip = f"192.168.1.{i}"
    print(ip)
```

Fixed network prefix + changing last octet (`1`–`254`). f-string handles the number→string glue. (`255` is excluded by `range`; start at `1`, not `0` — `.0` is the network address, not a host.)

> **Lesson:** an IP range is just a fixed prefix with a counting host part — the subnet mask (1.7) is what tells you the last octet is the part that varies.

### Step 2 — Read `ipconfig`, find the real adapter

Three adapters shown; only **Wi-Fi** was real (IP `192.168.1.3`, mask `255.255.255.0`, **gateway `192.168.1.254`**). The two Ethernet adapters had `169.254.x.x` (APIPA) and no gateway → dead, ignored. Confirmed the `192.168.1.` range was correct for the real network.

> **Lesson:** the adapter *with a gateway* is the live one; `169.254.` = failed-to-connect, ignore. (See 1.6.)

### Step 3 — First live-host sweep (single port)

```python
for i in range(1, 255):
    ip = f"192.168.1.{i}"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip, 80))
        print(f"Host {ip} is up")
    except ConnectionRefusedError:
        print(f"Host {ip} is up but port 80 is closed")   # refused = STILL alive
    except (socket.timeout, OSError):
        pass
    s.close()
```

Result: only `192.168.1.254` (the router).

> **Lesson:** both success and refusal mean alive (host responded). Only timeout = skip. BUT single-port discovery **under-reports** — it only finds devices that answer on *that one port* (router has a web server on 80; most other devices don't).

**Conceptual detour you worked through** (Steps where the real learning happened):
- "We're not assigned those IPs" → you're not *claiming* them, you're *contacting* them — knocking on your neighbours' doors. Your IP is the sender; theirs are destinations. The network delivers your packet to whatever device holds that address, like mail.
- "Whose doors did the port scanner knock on?" → `scanme.nmap.org`'s (a remote practice target), not yours.
- The `(host, port)` axis insight (1.2) and listening-vs-closed-vs-filtered (1.4) — both clarified here.

### Step 4 — Multi-port sweep (nested loop)

Knock several common ports per host; if *any* responds, the host is alive — print once and `break`.

```python
ports = [80, 443, 22, 445, 139, 8080]
for i in range(1, 255):
    ip = f"192.168.1.{i}"
    for port in ports:                       # inner loop
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # fresh per knock
        s.settimeout(1)
        try:
            s.connect((ip, port))
            print(f"Host {ip} is up")
            s.close(); break                 # alive → stop knocking this host
        except ConnectionRefusedError:
            print(f"Host {ip} is up")
            s.close(); break                 # refused = alive → stop
        except (socket.timeout, OSError):
            s.close()                        # silent → try NEXT port (don't break)
```

> **Lesson:** `break` on the first response (open OR refused) — host is confirmed, no point knocking its other ports. But **don't break on timeout** — a different port might still answer. Only all-ports-silent = invisible host.

### Step 5 — The 25-minute problem → threading

You did the math: 254 hosts × 6 ports × 1s timeout ≈ **25 minutes** worst case (filtered hosts burn the full timeout on every port). Same bottleneck as the port scanner — sequential waits stacking, CPU idle.

**Fix (reused from port scanner):** wrap per-host logic in `scan_host(ip)`, map it across a thread pool so the waits overlap.

```python
ips = [f"{base}{i}" for i in range(1, 255)]   # list comprehension builds all IPs
with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(scan_host, ips)
```

Result: seconds instead of 25 minutes, and **two** hosts now — `.254` (router) **and `.3` (your laptop)**. The laptop appeared because multi-port caught it on **445 (SMB)**, which it was silent-on-80 for. The upgrade proved itself.

> **Lesson:** threading collapses overlapping I/O waits (I/O-bound work again). Feed the pool IP *strings* via a list comprehension, not raw numbers.

### Step 6 — Banner grabbing on live hosts (reuse port scanner)

Grab a banner from the port that confirmed the host alive — but **only on an OPEN port** (a *refused* port has nothing listening, so no banner to grab). Reused the null-probe + HTTP-probe pattern.

**Results:**
- **Router (.254, port 80):** `HTTP/1.1 406 ... Set-Cookie: JSESSIONID=... X-Frame-Options: SAMEORIGIN` → fingerprinted as a **Java web-admin device** (JSESSIONID = Java servlet) with some hardening. Real device fingerprinting from a banner.
- **Laptop (.3, port 445):** empty banner — **correct**, because SMB is binary (see 1.9). `errors="ignore"` prevented a decode crash on the raw bytes.

> **Lesson:** banners fingerprint devices (the router leaked its stack). An empty banner on a binary port (SMB) is honest, not broken — and `errors="ignore"` is what kept it from crashing.

---

## PART 3 — Final Code (annotated)

```python
import socket
from concurrent.futures import ThreadPoolExecutor

base = "192.168.1."
ports = [80, 443, 22, 445, 139, 8080]        # common doors to knock on

def scan_host(ip):
    for port in ports:                        # inner loop: try each port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # fresh socket per knock
        s.settimeout(1)
        try:
            s.connect((ip, port))             # open → host alive, grab a banner
            banner = b""
            try:
                banner = s.recv(1024)         # null probe: does it greet us?
            except (socket.timeout, OSError):
                pass
            if banner == b"":                 # silent → poke with HTTP
                try:
                    s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = s.recv(1024)
                except (socket.timeout, OSError):
                    pass
            clean = banner.decode(errors="ignore").strip().replace("\r\n", " ")
            print(f"Host {ip} is up (port {port}) - {clean}")
            s.close()
            break                             # alive confirmed → stop knocking this host
        except ConnectionRefusedError:        # refused = alive, but nothing to banner
            print(f"Host {ip} is up")
            s.close()
            break
        except (socket.timeout, OSError):     # silent → try the NEXT port (no break)
            s.close()

# Build all 254 IP strings, then scan them in parallel
ips = [f"{base}{i}" for i in range(1, 255)]
with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(scan_host, ips)
```

**Sample output:**
```
Host 192.168.1.3 is up (port 445) -
Host 192.168.1.254 is up (port 80) - HTTP/1.1 406 Not Acceptable ... Set-Cookie: JSESSIONID=... X-Frame-Options: SAMEORIGIN ...
```

**Known rough edges / limitations (not bugs):**
- **TCP discovery misses firewalled devices** that drop all knocks (phones, well-secured laptops). ARP scanning (needs privileges) would catch them. (1.5)
- **Banner reuses one socket** for both probes (simpler than the port scanner's fresh-`s2`). Fine for a bonus banner on a discovery tool; may come back empty/messy on some hosts (worn-socket fragility).
- **Hardcoded network prefix** (`192.168.1.`) — a real tool would take the range as a CLI argument (argparse, like the cracker).
- **Port labels** — printing `445 (SMB)`, `22 (SSH)` etc. would make empty-banner results self-explaining.

---

## PART 4 — Key Transferable Lessons (quick recap)

1. **Recon runs in order:** discover hosts → scan ports → grab banners → attack. You can't attack a door before finding the building.
2. **Every address is `(host, port)`** — IP picks the building, port picks a door. Every device has its own 65,535 ports. Port scanner loops the *port*; network scanner loops the *host*. Same knocking, different axis.
3. **Detect a host by knocking a port — any response (open OR closed) = alive.** The port is a doorbell; you care if someone's home, not if the door opens.
4. **Open / closed / filtered:** open = program listening + responded; closed = nothing listening but host responded; filtered = silence (dropped). Only *filtered* hides a host.
5. **A port is open only because a program is actively listening on it.** No program → closed or filtered.
6. **TCP discovery is blind to firewalled devices that drop packets.** ARP scanning (needs privileges) sits below the firewall and catches them. Document the limit.
7. **Read `ipconfig` first:** the adapter *with a gateway* is live; `169.254.` (APIPA) = failed connection, ignore.
8. **Subnet mask tells you network vs host bits.** `/24` → last octet varies (254 hosts) → that's what your loop counts.
9. **Nested loop:** outer hosts, inner ports. `break` on first response (host confirmed); **don't** break on timeout (another port may answer).
10. **`errors="ignore"`** = decode what you can, drop unparseable bytes, never crash. Essential for banners from devices that speak binary.
11. **An empty banner on a binary port (SMB/445) is correct, not broken.** Not every service sends readable text.
12. **Banners fingerprint devices** — the router leaked "Java web-admin" via its JSESSIONID cookie. That's recon.
13. **Threading collapses overlapping I/O waits** — 25 min → seconds. Feed the pool IP strings via a list comprehension. (Same I/O-bound lesson as the port scanner.)

---

*Built 5 Nov 2026 by extending the port scanner. The point was never the file — it was understanding every line, and every limit, of it.*