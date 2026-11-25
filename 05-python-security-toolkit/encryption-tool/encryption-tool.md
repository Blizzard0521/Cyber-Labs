# Encryption Tool — Study & Revision Notes

**Project:** `encryption-tool.py` (Phase 1, `05-python-security-toolkit/`) — the 4th and final Python tool
**Built:** 25 Nov 2026 · AES (Fernet) + RSA, encrypt/decrypt, persistent keys
**How to use this doc:** Part 1 is the theory (crypto families + the encoding concepts you dug into). Part 2 walks the build the way you lived it. Part 3 is the annotated final code. Part 4 is the quick-recap lessons list.

---

## PART 1 — The Theory (revision layer)

### 1.1 Hashing vs encryption (anchor against the cracker)

| | Hashing (cracker) | Encryption (this tool) |
|---|---|---|
| **Direction** | One-way — can't reverse | **Two-way** — encrypt AND decrypt |
| **Purpose** | Verify ("is this the same?") | Confidentiality ("hide, then reveal") |
| **Key?** | No key | **Needs a key** |
| **Output** | Fixed-length fingerprint | Scrambled version of the *actual data*, recoverable |

Hashing destroys the original (you guess your way back). Encryption *hides* the original and gives it back with the right key.

### 1.2 Symmetric (AES) vs asymmetric (RSA) — the two families

**AES = symmetric.** One key does both lock and unlock.
- Analogy: a door key — same key locks and unlocks.
- Fast, no size limit, great for bulk data.
- Problem: **key distribution** — how do you share the secret key without an eavesdropper stealing it?

**RSA = asymmetric.** Two mathematically linked keys:
- **Public key** — share with everyone; it can **encrypt** but *not* decrypt.
- **Private key** — keep secret; the *only* thing that can **decrypt** what the public key locked.
- Analogy: a mailbox — anyone drops mail in the slot (public encrypts), only you open the box (private decrypts).
- **Solves key distribution:** publish your public key openly, no secret ever travels. Foundation of HTTPS, SSH, signatures.
- Cost: **slow**, and can only encrypt **small** data.

**Share public, guard private.** For *you* to receive secret messages: hand out your public key (people encrypt to you), never reveal your private key (only it decrypts).

**Why both exist — the hybrid:** real systems use RSA to safely exchange a small AES key, then AES for the bulk data. Best of both. (You don't build the hybrid, but the RSA size limit is *why* it exists — see 1.6.)

### 1.3 Keys must persist (the #1 practical rule)

Both AES and RSA are useless if the key changes between runs:
- AES: same key encrypts and decrypts. Regenerate it → you can never decrypt yesterday's data.
- RSA: encrypt with public, decrypt with private. Lose the private key → the data is gone forever.

So: **generate the key ONCE, save it, reload the same key every run.** A key you don't save is a key you've lost, and lost key = lost data (that irreversibility is *why* encryption is secure — no key, no recovery, even for you).

Pattern: `if the key file exists → load it; else → generate + save it.`

### 1.4 Fernet (AES) vs raw RSA (hazmat)

- **Fernet** (`cryptography.fernet`) is the **high-level, safe** wrapper for symmetric encryption. It *is* AES (AES-128-CBC + authentication), with all the fiddly security details handled, and it **base64-encodes its output automatically** (the `gAAAAA...` tokens).
- **RSA** lives under **`hazmat`** ("hazardous materials") — the library's name for **low-level primitives you must use carefully**. You specify padding yourself, handle raw bytes yourself, base64 yourself. More control, more responsibility.

### 1.5 PEM serialization (why you can't just `.write()` an RSA key)

A Fernet key is **bytes** → write it straight to a file.
An RSA key is a **Python object** (`<RSAPrivateKey object at 0x...>`) → you can't write an object to a file. You must **serialize** it first: convert the object into storable bytes. The standard format is **PEM** — the `-----BEGIN PRIVATE KEY-----` text blocks.

- `private_key.private_bytes(encoding=PEM, format=..., encryption_algorithm=NoEncryption())` → object → PEM bytes to save.
- `serialization.load_pem_private_key(data, password=None)` → PEM bytes → object to use.
- Save **only the private key** — the public key is derived anytime with `private_key.public_key()`.
- PEM is **text-based**, so it displays fine in an editor (unlike the binary Fernet `key.key`, which looked empty).

### 1.6 OAEP padding + the RSA size limit

**Padding:** raw RSA is deterministic and insecure (same message → same ciphertext, which leaks info). **OAEP** padding adds randomness/structure before encrypting, so the same message encrypts differently each time. Rules:
- Always use OAEP for RSA encryption.
- **The same padding config must be used for encrypt and decrypt** (match it exactly, like the key).
- `MGF1` + `SHA256` are the standard secure parameter choices — use as-is.

**The size limit:** RSA can only encrypt data **smaller than the key size**. For a 2048-bit key with SHA-256 OAEP:
```
max bytes = key_bytes − 2×hash_bytes − 2 = 256 − 64 − 2 = 190 bytes
```
Over ~190 bytes → `ValueError`. **Don't hardcode 190** (it changes with key size/hash) — just try to encrypt and **catch the `ValueError`**; let the library report its own limit (same lesson as catching socket exceptions vs hardcoding OS error codes). This hard limit is *why* RSA can't do bulk data, and why the hybrid approach exists.

### 1.7 base64 — making raw bytes copy-safe (and why RSA needs it, Fernet didn't)

**base64 represents *any* raw bytes using only safe printable characters** (A–Z, a–z, 0–9, +, /, =). Its job: make binary survive as text you can copy, paste, email, put in a URL.

**Why RSA needs it:** RSA ciphertext is raw binary (`b'\xa4\xfe)\xa3...'`) — those bytes are *untypeable/uncopyable*. The encrypt→copy→decrypt flow breaks: the user can't move `\xa4\xfe` through a terminal without corrupting it. base64 turns it into `pP4po4ds...` — fully copyable — then `b64decode` reverses it before decrypting.
- `base64.b64encode(ciphertext)` → raw bytes → base64 **bytes** (`b'pP4...'`, printable content)
- `.decode()` → base64 bytes → clean **string** (strips the `b'`)
- `base64.b64decode(text.encode())` → reverses it back to raw bytes

**Why Fernet didn't need you to add it:** Fernet base64-encodes internally — those `gAAAAA...` tokens were base64 all along. Raw RSA doesn't, so you add it yourself.

### 1.8 Encoding layers: encode/decode, utf-8, base64 (what you untangled)

- `.encode(enc)` = **text → bytes**. `.decode(enc)` = **bytes → text**. They're reverse directions.
- **An encoding (utf-8, latin-1) is a *rulebook*** mapping bytes↔characters — not a "language." The *same bytes* under a *different* rulebook give *different* characters, which is why `.decode()` needs you to name one (utf-8 is the default). (Same idea as rockyou needing `latin-1` and `errors="ignore"`.)
- **utf-8 ≠ base64 — different jobs:**

| | **utf-8** | **base64** |
|---|---|---|
| Job | text ↔ bytes (represent characters) | bytes ↔ safe-printable text (make binary copyable) |
| Input | human text (`"héllo"`) | any raw bytes (`\xa4\xfe`) |

They chain: `b64encode(ciphertext).decode()` uses **both** — base64 to make the bytes printable, then utf-8 (`.decode()`) to turn those printable bytes into a Python string.

### 1.9 Key storage is a real, hard problem (documented limitation)

The key is the *entire* secret — anyone who reads the key file can decrypt everything. The proper solution is dedicated infrastructure (**KMS** — Key Management Service, or **HSM** — Hardware Security Module: AWS KMS, Vault, etc.), which you **use, not build.** A homemade "secure vault" is a trap (false confidence). So this tool stores keys in local files and **documents that as a known limitation** — appropriate for a learning deliverable, same pattern as the scanner's nmap ceiling.

---

## PART 2 — The Build Journey (your mistakes → fixes)

### Step 1 — Generate an AES (Fernet) key

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()     # b'QpN3_czP...=' — 32 random bytes, base64
```

> **Lesson:** the key IS the secret (whoever has it decrypts everything). It's bytes (`b''` again). And the question it raised: *if you regenerate it every run, you can't decrypt last run's data* → keys must persist.

### Step 2 — "The key file looks empty"

Opened `key.key` (written in `"wb"` binary mode) — looked blank in VS Code.

> **Lesson:** it wasn't empty — a **text editor can't render raw bytes**. `print(key)` proves the key is there. Don't judge a binary file by what a text editor shows. (Same as the SMB banner and rockyou needing latin-1.)

### Step 3 — The regenerate-every-run bug (the big one)

```python
with open("key.key", "wb") as key_file:   # runs EVERY run → overwrites the key
    key = Fernet.generate_key()
```

Round-tripped fine *in testing* — but only because encrypt and decrypt happened **in the same run** with the same throwaway key. A token saved from an *earlier* run would fail with `InvalidToken`, because the key that could decrypt it got overwritten.

> **Lesson (two of them):** (1) **generate only if the key doesn't exist** — `if not os.path.exists(path):` — so the key persists. (2) **"It worked when I ran it" ≠ correct** — your same-run test never exercised the broken cross-run path. A bug invisible to a too-narrow test is still a bug. (Echo of the bare-`except` lesson.)

### Step 4 — Path fights (relative vs absolute, backslash escapes)

Tried hardcoding `"05-python-security-toolkit\encryption-tool\key.key"` — broke two ways: wrote and read from *different* paths, and `\e`/`\k` are invalid string escapes.

**Fix — anchor to the script's own location:**
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(script_dir, "key.key")
```

> **Lesson:** relative paths resolve from where Python was *launched*, not where the script *lives* (same `FileNotFoundError` lesson as the cracker). `__file__` + `os.path.dirname`/`join` puts the key next to the script regardless of launch directory, and `os.path.join` handles separators so there are no backslash-escape bugs.

### Step 5 — Stale key file poisoned the guard

Got `Fernet key must be 32 url-safe base64-encoded bytes.` — a leftover empty/corrupt `key.key` from the path experiments existed, so `os.path.exists` returned True, the code skipped generation, and loaded garbage.

> **Lesson:** **leftover state from earlier broken runs** is a classic "but it should work now" bug. When a fix doesn't take, suspect stale files. Fix: delete the bad file (or check `len(key) > 0` before trusting it).

### Step 6 — The `need_new_key` flag + a scoping bug

```python
need_new_key = True
if os.path.exists(aes_key_path):
    with open(aes_key_path, "rb") as kf:
        key = kf.read()
    if len(key) > 0:            # ← MUST be indented INSIDE the if
        need_new_key = False
if need_new_key:
    key = Fernet.generate_key()
    with open(aes_key_path, "wb") as kf:
        kf.write(key)
```

The bug: if `len(key) > 0` is *not* indented inside the `if os.path.exists` block, then on a no-file run `key` is never assigned → `len(key)` → **`NameError`**.

> **Lesson:** `len(key)` doesn't check the *file* — it checks the *variable*, which only exists if the `key = kf.read()` line actually ran. A check on a variable must live where that variable is *guaranteed* assigned. (This is also why AES needed the flag and RSA didn't — AES guards 3 states: missing / empty / valid; RSA's simple `if/else` only guards 2: exists / doesn't.)

### Step 7 — AES as a real tool: menu, modes, user input

Built a `while` loop with a `try_again()` helper, **mode first (encrypt/decrypt) → algorithm (AES/RSA)**, taking the message from the user.

> **Lesson:** separate encrypt and decrypt paths — encrypt takes a *message* → outputs a *token*; decrypt takes a *token* → outputs a *message*. The real proof: encrypt in one run, copy the token, **decrypt it in a separate run** → survives, because the key persisted. (The old auto-round-trip could never test this.) On the token in decrypt mode: `.encode()` it back to bytes, because `f.decrypt` needs bytes but the pasted token is a string.

### Step 8 — RSA keypair + encrypt/decrypt + the size limit

Generated a keypair (`rsa.generate_private_key`, derive `public_key()`), encrypted with **public**, decrypted with **private**, using the OAEP block. Then forced a >190-byte message:

```python
message = b"Secret..." + b"a" * 200       # over 190 bytes
# → caught: "Message too long for RSA encryption: Encryption failed"
```

> **Lesson:** RSA has a hard **size limit** (~190 bytes for 2048-bit + SHA256) — witnessed firsthand. This is *why* RSA can't do bulk data and why the hybrid (RSA-wraps-AES) exists. Catch the `ValueError` rather than hardcoding 190.

### Step 9 — Two code-structure bugs

- **Un-balanced parentheses** while restructuring the nested `encrypt(...)` call → `SyntaxError` (code won't even start — different from a runtime error).
- **`try` scope too narrow:** the decrypt + prints must live *inside* the `try` with the encrypt. If encrypt fails and only *it* is in the try, execution continues to `print(ciphertext)` → `NameError` (ciphertext never assigned).

> **Lesson:** a `try` should wrap the risky line *and everything that depends on its success*. And syntax errors (unbalanced brackets) are caught *before* execution; runtime errors happen *during* — different classes.

### Step 10 — RSA persistence (PEM) + the self-contained `else`

First version's `else` (generate branch) referenced `private_key` to serialize it — but never *generated* it in that branch; it only worked due to leftover test code above.

> **Lesson:** the `else` ("no key file") must **generate the keypair first**, then serialize + save. Same leftover-state trap as Step 5. PEM displays as readable text (`-----BEGIN RSA PRIVATE KEY-----`), unlike the binary Fernet key.

### Step 11 — base64 for RSA output (the menu integration snag)

RSA ciphertext is raw bytes (`\xa4\xfe...`) — a user can't copy-paste it. So for the menu's encrypt→copy→decrypt flow:
```python
encoded = base64.b64encode(ciphertext).decode()   # printable string to copy
...
ciphertext = base64.b64decode(user_message.encode())  # back to raw bytes to decrypt
```

> **Lesson:** base64 makes binary copy-safe (1.7). Fernet did this invisibly; raw RSA needs you to. Final robustness touch: a second `try/except ValueError` in decrypt mode catches a user pasting an AES token (or junk) into RSA decrypt.

---

## PART 3 — Final Code (annotated)

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import cryptography.hazmat.primitives.hashes as hashes
from cryptography.hazmat.primitives import serialization
import base64
import os

script_dir = os.path.dirname(os.path.abspath(__file__))   # anchor paths to the script's folder
aes_key_path = os.path.join(script_dir, "key.key")
rsa_private_key_path = os.path.join(script_dir, "private_key.pem")

def try_again():
    while True:
        ans = input("Do you want to encrypt/decrypt another message? (y/n): ").strip().lower()
        if ans == "y":
            return True
        elif ans == "n":
            print("Exiting the encryption tool. Thank you for using it!")
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def encrypt_decrypt_message():
    while True:
        mode = input("Choose a mode \n1. Encrypt \n2. Decrypt \n").strip()
        method = input("Choose the encryption method \n1. AES \n2. RSA \n").strip()
        user_message = input("Enter a message to " + ("encrypt" if mode == "1" else "decrypt") + ": ")

        if method == "1":   # ---------- AES (Fernet, symmetric) ----------
            need_new_key = True
            if os.path.exists(aes_key_path):
                with open(aes_key_path, "rb") as key_file:
                    key = key_file.read()
                if len(key) > 0:            # nested: only runs if a file was read (no NameError)
                    need_new_key = False
            if need_new_key:
                key = Fernet.generate_key()
                with open(aes_key_path, "wb") as key_file:
                    key_file.write(key)

            f = Fernet(key)
            if mode == "1":
                token = f.encrypt(user_message.encode())
                print(f"Encrypted message: {token.decode()}")
            elif mode == "2":
                plaintext = f.decrypt(user_message.encode())
                print(f"Decrypted message: {plaintext.decode()}")
            else:
                print("Invalid mode selected. Please choose 1 or 2.")
                if not try_again(): break
            if not try_again(): break

        elif method == "2":   # ---------- RSA (asymmetric) ----------
            if os.path.exists(rsa_private_key_path):
                with open(rsa_private_key_path, "rb") as key_file:
                    private_key = serialization.load_pem_private_key(key_file.read(), password=None)
            else:
                private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
                with open(rsa_private_key_path, "wb") as key_file:
                    key_file.write(pem)

            public_key = private_key.public_key()   # derived from private, either way

            if mode == "1":   # encrypt with PUBLIC key
                try:
                    ciphertext = public_key.encrypt(
                        user_message.encode(),
                        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                     algorithm=hashes.SHA256(), label=None)
                    )
                    encoded = base64.b64encode(ciphertext).decode()   # raw bytes → copyable text
                    print("Encrypted message:", encoded)
                    if not try_again(): break
                except ValueError as e:               # RSA size limit (~190 bytes)
                    print("Message too long for RSA encryption:", e)

            elif mode == "2":   # decrypt with PRIVATE key
                try:
                    ciphertext = base64.b64decode(user_message.encode())   # text → raw bytes
                    plaintext = private_key.decrypt(
                        ciphertext,
                        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                     algorithm=hashes.SHA256(), label=None)
                    )
                    print("Decrypted:", plaintext.decode())
                    if not try_again(): break
                except ValueError as e:               # e.g. pasted an AES token into RSA
                    print("Decryption failed. Ensure the input is a valid RSA message:", e)
                    if not try_again(): break
        else:
            print("Invalid method selected. Please choose 1 for AES or 2 for RSA.")
            if not try_again(): break

encrypt_decrypt_message()
```

**Known limitations (documented, not bugs):**
- **Keys stored in plaintext local files** (`key.key`, `private_key.pem`). Production uses a KMS/HSM; the PEM is saved with `NoEncryption()` (no password). Appropriate for a learning tool; documented. (1.9)
- **AES uses one global key** — everyone sharing this tool shares one key. Real use would scope keys per user/message.
- **RSA single-key-pair, small messages only** — no hybrid RSA+AES, so no bulk data. (1.6)
- **`user_message` is prompted even for the RSA path** before the method is known — a minor UX ordering quirk.

---

## PART 4 — Key Transferable Lessons (quick recap)

1. **Encryption is two-way (unlike hashing).** It hides data and gives it back with the key; it doesn't destroy the original.
2. **Symmetric (AES) = one key both ways; asymmetric (RSA) = public encrypts, private decrypts.** Share public, guard private. RSA solves key distribution (no secret travels).
3. **Keys must persist:** generate once, save, reload the same key. A regenerated key = unrecoverable old data. "It worked" in a same-run test can hide a broken cross-run key path.
4. **Fernet is the safe high-level AES wrapper; `hazmat` RSA is low-level** — you handle padding, raw bytes, and base64 yourself.
5. **RSA keys are objects → must be serialized (PEM) to save;** Fernet keys are bytes. Save only the private key (public is derived).
6. **OAEP padding** is mandatory for RSA and must match on encrypt/decrypt. **RSA has a hard size limit** (~190 bytes for 2048-bit) — catch the `ValueError`, don't hardcode the number. That limit is why the RSA+AES hybrid exists.
7. **base64 makes raw bytes copy-safe.** RSA ciphertext is untypeable binary → base64 it for the user, decode it back before decrypting. Fernet did this for you.
8. **encode/decode = text↔bytes; an encoding (utf-8) is a *rulebook*, not a language; base64 ≠ utf-8** (different jobs, often chained).
9. **A check on a variable must live where that variable is guaranteed assigned.** `len(key)` reads the *variable*, not the file — un-nested, it `NameError`s when no file was read.
10. **Anchor file paths to `__file__`**, not the launch directory. Use `os.path.join` (no manual backslashes).
11. **Leftover/stale files poison "file exists" guards.** When a fix won't take, suspect old state. Validate contents (`len > 0`), don't just trust existence.
12. **A `try` must wrap the risky line AND everything that depends on its success** — or you catch one error and fall into a `NameError`. Syntax errors (unbalanced brackets) fail *before* run; runtime errors fail *during*.
13. **Key storage is a real hard problem solved by KMS/HSM, which you *use*, not build.** Document the file-storage limitation rather than hand-rolling a vault.

---

*Built 25 Nov 2026 — the capstone of the Phase 1 Python toolkit (port scanner · password cracker · network scanner · encryption tool). The point was never the file; it was understanding every line, and every limit, of it.*