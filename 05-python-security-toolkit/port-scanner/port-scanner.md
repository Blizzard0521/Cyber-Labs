

Port scanner study notes · MD
# Port Scanner — Study & Revision Notes
 
**Project:** `port-scanner.py` (Phase 1, `05-python-security-toolkit/`)
**Built:** 15–21 Oct 2026 · from an empty file, bug by bug
**How to use this doc:** Read Part 1 (basics) to refresh the theory, then Part 2 to walk the build the way you actually lived it — each step shows your *first* attempt, what broke, and the fix. Part 3 is the final annotated code. Part 4 is the "never forget this" list. Come back to Part 4 alone when you just want a quick recap.
 
---
 
## PART 1 — The Basics (revision layer)
 
The concepts the whole tool rests on. If any of these feel fuzzy, this is the section to re-read.
 
### 1.1 What a socket is
 
A **socket** is your program's endpoint for talking over a network — the thing you read from and write to, the way a file object is for a file. You create one, point it at a destination, and data flows through it.
 
```python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 └── IPv4         └── TCP
```
 
- `AF_INET` = use IPv4 addresses.
- `SOCK_STREAM` = use **TCP** (reliable, connection-based). The alternative is `SOCK_DGRAM` = **UDP** (fire-and-forget, no connection).
**Golden rule you learned the hard way:** **one socket = one connection attempt.** A TCP socket *is* the connection, not a reusable dialer. Once it has tried to connect (success or fail), it's "spent" and the OS won't let it start a fresh connection. To make 100 attempts, you create 100 sockets. (Think: single-use envelope — you can't re-address a sealed one.)
 
### 1.2 The TCP three-way handshake
 
To open a TCP connection, three packets go back and forth:
 
```
You  ── SYN ──▶  Host      "can we talk?"
You  ◀ SYN-ACK ─ Host      "yes, let's talk"
You  ── ACK ──▶  Host      "great, connected"
```
 
When you call `s.connect(...)` in Python, the **OS runs this whole handshake for you**. You don't craft packets — you just ask "connect me" and watch whether it worked. That's why a basic scanner is almost dumb: *trying to connect* IS the scan.
 
### 1.3 Ports and the three states
 
A **port** is a numbered door on a machine (0–65535). Different services sit behind different doors: SSH=22, HTTP=80, HTTPS=443. A host + port together (`("scanme.nmap.org", 80)`) is a full address — "this door, on this machine."
 
A port can be in **three** states, not two — this is the single most important idea in the tool:
 
| State | What happens | How it feels in code |
|---|---|---|
| **Open** | Handshake completes, something is listening | `connect` succeeds (fast) |
| **Closed** | Host is up but nothing's on that port — it **actively refuses** you (sends a TCP RST) | `ConnectionRefusedError` (fast) |
| **Filtered** | A firewall **silently drops** your packet — no reply at all | `socket.timeout` (slow — waits the full timeout) |
 
**Why this matters to an attacker:** "closed" means the host is up but that service isn't running. "Filtered" means a firewall is *actively hiding* something — a very different signal. nmap distinguishes them; so does your tool.
 
### 1.4 Bytes vs strings (`b""`)
 
The network speaks **bytes**, not text. Two different Python types:
 
- `"hello"` → a **string** (`str`), human-readable text.
- `b"hello"` → **bytes**, raw wire data. The `b` prefix means "this is bytes."
Every socket method deals in bytes:
- `s.recv(1024)` **returns bytes** → that's why banners print as `b'SSH-2.0-...'`.
- `s.send(b"...")` **requires bytes** → sending a plain string raises `TypeError`.
Convert between them:
- `.decode()` → bytes → string (makes it readable, kills the `b'` prefix)
- `.encode()` → string → bytes
> **Quote trap:** `b""` and `b''` are **100% identical**. Single vs double quotes never matter in Python. The only meaningful part is the **`b` prefix** (bytes vs string), *not* the quote style. (You once "fixed" a bug by swapping them — it changed nothing; something else had changed.)
 
`b""` specifically = **empty bytes**, used as a starting value / "nothing received yet" marker.
 
### 1.5 Exceptions (and why `connect_ex` vs `connect` matters)
 
Two ways to make a connection, with different error styles:
 
- `s.connect_ex((host, port))` → **returns a number**: `0` = success, non-zero = an error *code*. Never raises.
- `s.connect((host, port))` → **raises an exception** on failure: `socket.timeout`, `ConnectionRefusedError`, etc.
**You chose `connect` + exceptions. Why it's the better instrument:**
 
Error *codes* are **OS-specific** — you proved this live:
 
| State | Linux code | Windows code |
|---|---|---|
| refused | `111` | `10061` |
| "would block" (timeout-ish) | — | `10035` |
 
Hardcoding `111` breaks on Windows; hardcoding `10061` breaks on Linux. But exception **types** (`ConnectionRefusedError`, `socket.timeout`) mean the same thing on *every* OS. So `try/except` decodes the failure *for you*, portably, with no magic numbers to guess. Fewer ways to be wrong = better tool.
 
### 1.6 Threading (I/O-bound vs CPU-bound)
 
A **thread** is an independent line of execution. Normally your program runs one thing at a time, in order (**sequential**). Threading runs many at once (**parallel**).
 
- **Sequential scan:** port 1 waits its full timeout, *then* port 2 waits, *then* port 3… 100 filtered ports × 3s ≈ 5 minutes. During each wait the CPU is **idle** — just waiting on the network.
- **Threaded scan:** fire all ports at once; their waits **overlap**. 100 ports ≈ 10 seconds.
**The key distinction (interview-level):** threading only helps **I/O-bound** work (waiting on network/disk), *not* **CPU-bound** work (heavy computation) — because of Python's GIL. Port scanning is ~99% waiting, so it's the *perfect* case for threading.
 
Bonus insight: threading made the *accurate* (long-timeout) version practical. Long timeouts used to be too slow to use; with overlapping waits, a generous timeout is now cheap. **Speed and accuracy stopped being a tradeoff.**
 
---
 
## PART 2 — The Build Journey (your mistakes → fixes)
 
Each step: what you tried, what broke, why, and the fix. This is the part worth studying — the bugs are the lessons.
 
### Step 1 — Connect to a single port
 
**First attempt (broken):**
```python
import socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # BUG 1
socket.connect_ex((host, port)).settimeout(1)                   # BUG 2 + 3
socket.close()
```
 
**Three bugs:**
1. **Shadowing** — naming the variable `socket` overwrites the `socket` *module*. After this line, `socket.AF_INET` would break. → Name it `s`.
2. **`settimeout` set *after* connecting, and chained onto a number.** A timeout is a rule for *before* you wait — set it first. And `.connect_ex()` returns an **int**; ints have no `.settimeout()`.
3. **The return value was thrown away.** That `0`/non-zero *is the answer* — you must capture it and check it.
**Fixed:**
```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)                               # set BEFORE connecting
result = s.connect_ex(("scanme.nmap.org", 81))  # capture the answer
s.close()
if result == 0:
    print("Port is open")
else:
    print("Port is closed")
```
 
> **Lesson:** capture-then-check. The thing you need is often already sitting in a return value — don't discard it.
 
### Step 2 — Three states, not two
 
The Step 1 code lumps "closed" and "filtered" into one `else`. You switched to `connect` + exception *types* to tell them apart:
 
```python
s.connect((host, port))                       # raises on failure
# ... wrapped in:
try:
    s.connect((host, port))
    print("open")
except socket.timeout:
    print("filtered (timed out)")             # firewall dropped it
except ConnectionRefusedError:
    print("closed (refused)")                 # host said "no"
```
 
**Experiments you ran to *see* all three:**
- `scanme.nmap.org:80` → **open**
- `scanme.nmap.org:81` → **filtered** (nmap's box firewalls this port — silently drops)
- `127.0.0.1:9999` → **closed** (localhost refuses; it never drops its own packets)
> **Lesson:** `connect_ex` with a 2-way check *mislabeled* filtered ports as "closed" — not because the data was wrong, but because the check was too coarse. **Your tool's accuracy is limited by how finely it inspects the signal.** `try/except` on exception *types* is the finer, portable instrument.
 
> **Also learned:** "filtered" is often indistinguishable from "slow network" from the attacker's side. You handle the ambiguity rather than resolve it.
 
### Step 3 — Loop over a range
 
```python
for port in range(1, 101):                    # 1–100 (range stops BEFORE 101)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # FRESH socket each time
    s.settimeout(1)
    try:
        s.connect((host, port))
        print(f"Port {port} is open")
    except:
        pass                                  # closed/filtered → stay silent
    s.close()
```
 
**The core realisation:** socket creation moved **inside** the loop. Because one socket = one attempt, every port needs its own fresh socket. First working output:
```
Port 22 is open
Port 80 is open
```
 
> **Lesson:** `range(1, 101)` gives 1–100 (the stop value is excluded). And the one-socket-per-attempt rule is *why* the socket is created inside the loop, not before it.
 
### Step 4 — Banner grabbing (scan → recon)
 
An open port is "a door exists." A **banner** is "and here's exactly what's behind it." Many services announce themselves on connect.
 
**Listen-only version (catches SSH):**
```python
s.connect((host, port))
banner = s.recv(1024)                         # read what the service announces
print(f"Port {port} open — {banner}")
```
 
Result on port 22:
```
b'SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13\r\n'
```
 
**Read that like an attacker:** OpenSSH **6.6.1p1** (old, ~2014) on **Ubuntu**. You now know the OS and an outdated service version — without logging in. That's the enumeration loop: *port → service → version → known exploits.*
 
**The catch:** port 80 gave **nothing** this way. HTTP stays silent until *you* speak first. So banner grabbing has two flavours:
- **Service talks first** (SSH, FTP) → just `recv`.
- **Service waits for you** (HTTP) → you must `send` a request, *then* `recv`.
To make HTTP talk:
```python
s.send(b"HEAD / HTTP/1.0\r\n\r\n")
banner = s.recv(1024)
```
 
### Step 5 — The "listen first, then poke" design + its bugs
 
**Buggy attempt (connect outside try, hardcoded port):**
```python
for port in range(1,101):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((host, 80))                     # BUG A: hardcoded 80, not `port`
    banner = b""                              # BUG B: connect is OUTSIDE any try
    try:
        banner = s.recv(1024)
    except socket.timeout:
        pass
    if banner == b"":
        try:
            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(1024)
        except socket.timeout:
            pass
    s.close()
```
 
Crash: `TimeoutError: timed out`.
 
**Why:**
- **Bug A** — used literal `80` instead of the loop variable `port`.
- **Bug B** — `connect` sat *outside* the `try`, so when a filtered port made `connect` time out, nothing caught it → whole program crashed. (Remember: most of scanme's ports are filtered, so `connect` times out constantly.)
**Fixed — nest the trys. Outer protects `connect`, inner protects the banner reads:**
```python
try:
    s.connect((host, port))                   # now protected
    banner = b""
    try:
        banner = s.recv(1024)
    except socket.timeout:
        pass
    if banner == b"":
        try:
            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(1024)
        except socket.timeout:
            pass
    print(f"Port {port} open — {banner}")      # only runs if connect succeeded
except:
    pass
```
 
> **Lesson:** `connect` and `recv` are *different* operations that each fail independently. `connect` times out when the connection won't **establish**; `recv` times out when it established but the service won't **talk**. Protect both layers.
 
Now port 80 finally coughed up:
```
Server: Apache/2.4.7 (Ubuntu)
```
Full fingerprint: **Ubuntu + OpenSSH 6.6.1p1 + Apache 2.4.7.**
 
### Step 6 — The ambiguity with no clean fix
 
Port 22 sometimes returned `b''`. **Why:** on a slow run, probe 1's `recv` times out before SSH greets → `banner` stays empty → the `if banner == b"":` block fires → you **poke SSH with HTTP** → SSH returns nothing → `b''`.
 
**The hard truth:** "slow SSH" and "silent HTTP" look *identical* to a simple scanner. No single timeout value fixes it.
 
**What the pros (nmap) do** — not a cleverer line of code, but **scale and rigour**:
- Send **many** probes (a null probe first, then HTTP, TLS, etc.) from a big database.
- Match responses against **signature fingerprints** — identify by *what it says back*, not by port number.
- **Null probe first**, so self-greeting services (SSH) are caught before any poking.
- **Fresh connection per probe.**
- **Adaptive timing + retries** so a slow service gets a second chance.
> **Lesson:** you hit the *ceiling* of what a hand-written scanner should do — and that's a success. You now understand *why nmap exists*. The pro move isn't "rebuild nmap," it's "build enough to understand it, then use nmap knowing exactly what it does."
 
### Step 7 — Separate the probes with fresh sockets
 
Baby version of nmap's approach: give each probe its **own socket** so the HTTP poke can never corrupt the null-probe banner.
 
**Buggy attempt** had two hidden bugs — *both invisible because of a bare `except`*:
```python
s2 = socket.socket(socket.AF_INET, socket.SOCK_SYSTEM)   # BUG: no such thing (SOCK_STREAM)
...
except socket.timeout():                                 # BUG: () calls it — needs the TYPE, no parens
```
 
The program printed **nothing**. You assumed "everything passed." Really, the `SOCK_SYSTEM` `AttributeError` was **swallowed by the outer bare `except:`**.
 
**Fix — specific excepts that let real bugs crash loudly:**
```python
except (socket.timeout, ConnectionRefusedError, OSError):
    pass
```
 
> **Lesson (one of the most important in the whole project):** a bare `except:` catches *everything*, including bugs you didn't anticipate — turning a loud, findable crash into silent nothing. **Catch expected failures specifically; let unexpected ones surface.** When debugging, always ask: *what is my error handling hiding from me?*
 
### Step 8 — Clean output (decode at the boundary)
 
**Buggy attempt** — decoded on the wrong socket (`s2` only) and `.strip()` didn't fix internal `\r\n`:
```python
banner = s2.recv(1024).decode().strip()       # only probe 2; port 22 stayed raw bytes
```
Port 80's headers exploded onto separate lines (`.strip()` only trims the ends, not the `\r\n` *between* headers).
 
**Fix — keep bytes through the logic; decode ONCE, right before printing:**
```python
clean = banner.decode(errors="ignore").strip().replace("\r\n", " ")
print(f"Port {port} open - {clean}")
```
- `.decode(errors="ignore")` → bytes → string, skipping any undecodable junk (instead of crashing).
- `.strip()` → trims leading/trailing whitespace.
- `.replace("\r\n", " ")` → flattens internal header breaks into one tidy line.
> **Lesson:** keep data in its raw (bytes) form through your logic; convert to human-readable text **only at the boundary where a human reads it** (the print). Convert late, at the edge. Also: when a value can be set from two code paths, clean it in **one** place they both funnel through.
 
### Step 9 — Threading
 
Replace the `for` loop with a pool of worker threads.
 
```python
from concurrent.futures import ThreadPoolExecutor
 
def scan_port(port):
    ...   # everything that used to be inside the for loop
 
with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(scan_port, range(1, 101))
```
 
- The loop body became a **function** `scan_port(port)` (handles exactly one port).
- `executor.map(scan_port, range(1,101))` runs `scan_port` for every port across up to 100 threads at once.
- Result: 100 ports in ~10s (was ~5 min), **and** SSH's banner came back clean — the long timeout is affordable now.
> **Lesson:** threaded output order is **non-deterministic** — results print whenever each thread finishes, not in port order. In practice it *correlates with task duration* (fast port 22 beats slow port 80), so it *looks* ordered with few results — but never rely on it. For sorted output, collect results and sort at the end.
 
---
 
## PART 3 — Final Code (annotated)
 
```python
import socket
from concurrent.futures import ThreadPoolExecutor
 
host = "scanme.nmap.org"
 
def scan_port(port):
    # --- Probe 1: NULL PROBE (listen first) ---
    # Fresh socket for this probe (one socket = one attempt).
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)                     # long: we're WAITING for a slow service to greet
    try:
        s.connect((host, port))         # inside try: a filtered port times out here
        banner = b""                    # empty = "nothing received yet" (bytes, to match recv)
        try:
            banner = s.recv(1024)       # does the service greet us? (SSH does)
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass                        # silent service → banner stays b""
        s.close()                       # done with probe 1's socket
 
        # --- Probe 2: HTTP PROBE (only if null probe found nothing) ---
        if banner == b"":
            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # FRESH socket, can't corrupt probe 1
            s2.settimeout(1)            # short: we SPEAK first, so the reply is fast
            try:
                s2.connect((host, port))
                s2.send(b"HEAD / HTTP/1.0\r\n\r\n")   # poke it in HTTP
                banner = s2.recv(1024)
            except (socket.timeout, ConnectionRefusedError, OSError):
                pass
            s2.close()
 
        # --- Decode at the boundary, once, right before printing ---
        clean = banner.decode(errors="ignore").strip().replace("\r\n", " ")
        print(f"Port {port} open - {clean}")
 
    except:                             # NOTE: could be tightened to specific excepts
        pass                            # connect failed (closed/filtered) → skip silently
 
 
# Hand all ports to a pool of worker threads (parallel, not sequential)
with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(scan_port, range(1, 101))
```
 
**Sample output:**
```
Port 22 open - SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13
Port 80 open - HTTP/1.1 200 OK Date: ... Server: Apache/2.4.7 (Ubuntu) ...
```
 
**One known rough edge to tighten later:** the final outer `except:` is still bare — for a polished tool, make it `except (socket.timeout, ConnectionRefusedError, OSError):` so future typos surface instead of hiding (see Step 7).
 
---
 
## PART 4 — Key Transferable Lessons (quick recap)
 
Read just this section when you want a fast refresher.
 
1. **One socket = one connection attempt.** A TCP socket *is* the connection; the OS won't let a spent one restart. Fresh socket per attempt (and per probe).
2. **There are three port states, not two:** open / closed (refused) / filtered (dropped). The difference is real intel.
3. **Exception *types* beat error *codes*.** Codes are OS-specific (`111` Linux, `10061`/`10035` Windows); types (`socket.timeout`, `ConnectionRefusedError`) are portable. Let Python decode the failure for you.
4. **The network speaks bytes.** `recv` returns bytes, `send` needs bytes. Convert to text with `.decode()` — and only at the boundary where a human reads it.
5. **`b""` == `b''`.** Quote style never matters; only the `b` prefix does. Don't credit a "fix" you can't explain — know *why* it worked.
6. **A bare `except:` hides bugs.** It swallows unexpected errors (typos, `AttributeError`) and turns loud crashes into silent nothing. Catch expected failures specifically; let the rest surface. When stuck: *what is my error handling hiding?*
7. **`connect` and `recv` fail independently.** Protect both. One is "can't establish," the other is "established but won't talk."
8. **The other side is unpredictable.** Services greet, stay silent, or hang up — there's no fixed rule. Write defensive code that survives any outcome, don't assume one.
9. **Threading helps I/O-bound work, not CPU-bound.** Scanning is ~99% waiting, so overlapping the waits collapses the total time — and makes accurate long timeouts affordable.
10. **Threaded output order isn't guaranteed.** It tracks task duration, not port number. Sort at the end if order matters.
11. **Know when a tool is "done."** Tools are never truly finished — *you* decide when it's good enough for its purpose. Hitting the ceiling of a hand-written scanner (and understanding why nmap exists) is a success, not a failure.
12. **Debugging discipline:** change one variable at a time, read what the output actually tells you (e.g. a `b` prefix proves decode never ran), and don't misattribute cause (the 3-hour gap, not the quote swap, was why it "worked later").
---
 
*Built across two sessions, Oct 2026. Every line understood before moving on — the point was never the file, it was the understanding.*
 
Claude finished the response
