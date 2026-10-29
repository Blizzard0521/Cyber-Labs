Claude



























Password cracker study notes · MD
# Password Cracker — Study & Revision Notes
 
**Project:** `password-cracker.py` (Phase 1, `05-python-security-toolkit/`)
**Built:** 29 Oct 2026 · from an empty file, stage by stage
**How to use this doc:** Part 1 refreshes the theory. Part 2 walks the build the way you lived it — first attempt, what broke, the fix. Part 3 is the annotated final code. Part 4 is the quick-recap lessons list (read just this when you only want a refresher).
 
---
 
## PART 1 — The Basics (revision layer)
 
### 1.1 What a hash is, and why cracking is *guessing*
 
A **hash** is the output of a **one-way function**: a password run through a fixed mathematical process that produces a fixed-length fingerprint.
 
```
"password"  ──[MD5]──▶  5f4dcc3b5aa765d61d8327deb882cf99
```
 
"One-way" is the whole point: easy to go **left → right**, mathematically infeasible to go **right → left**. You *cannot* take a hash and compute the original password back. Systems store the hash (not the password) so that a leaked database doesn't hand out everyone's passwords.
 
**So how do you crack it? You don't reverse — you replay.** Take a list of candidate passwords, hash each one the same way, and compare to the target. A match confirms the guess:
 
```
target:  5f4dcc3b5aa765d61d8327deb882cf99
 
"123456"    → hash → e10adc... → no match
"qwerty"    → hash → 65e84b... → no match
"password"  → hash → 5f4dcc... → ✅ MATCH  (guess confirmed)
```
 
> **The core truth:** you hash the **guess**, never the target. You *compare* hashes; you never decrypt. A match means "my guess, hashed, equals the stored hash → my guess is the password."
 
> **The consequence that defines the whole attack:** you can only crack a password that is **already in your wordlist**. A truly random password (`Xq7#mLp2!vR`) isn't in anyone's list, so it's never guessed — not because the math is hard, but because you never tried it. This is why `rockyou.txt` (≈14 million *real leaked* passwords) exists, and why strong random passwords resist this attack.
 
### 1.2 The avalanche effect (why case matters)
 
Hash functions are *exquisitely* sensitive: change **one character** — including its case — and the entire output is completely different, not "similar":
 
```
"password"  → MD5 → 5f4dcc3b5aa765d61d8327deb882cf99
"Password"  → MD5 → dc647eb65e6711e155375218212b3964
"PASSWORD"  → MD5 → 319f4d26e3c536b5dd871bb2c52e3178
```
 
This is the **avalanche effect**. It's why:
- `"Password"` and `"password"` are *genuinely different passwords* with unrelated hashes.
- Your wordlist must contain the password in its **exact original case** to crack it.
- You must **never** `.lower()` a candidate word — that would hash the wrong input and miss real matches.
### 1.3 Hash case vs password case (the key distinction)
 
Two different strings, two different rules:
 
| String | Case matters? | Safe to `.lower()`? | Why |
|---|---|---|---|
| **The hash** (`target`) | No — in hex, `F` = `f` (both mean 15) | ✅ Yes | Same value, just displayed differently. Cosmetic. |
| **The password** (candidate word) | **Yes** — `P` ≠ `p` | ❌ **Never** | Different case = different input = different hash (avalanche). |
 
So normalizing the **hash** to lowercase is safe insurance (a user might paste `5F4DCC...`); touching the **password's** case is destructive. The `.lower()` only ever goes on the target hash.
 
### 1.4 Hash length → algorithm
 
Each algorithm produces a fixed-length hex output. Length is the standard first clue to *which* algorithm made a hash:
 
| Algorithm | Hex length |
|---|---|
| MD5 | **32** |
| SHA1 | **40** |
| SHA256 | **64** |
 
It's a *guess* (different algorithms can share a length), but it's the normal first tell — real tools (hashid) do the same.
 
### 1.5 `hashlib` — hashing in Python
 
```python
import hashlib
hashlib.md5(b"hello").hexdigest()          # algorithm hardcoded
hashlib.new("sha256", b"hello").hexdigest()  # algorithm as a STRING variable
```
 
- `hashlib.md5(...)` / `.sha1()` / `.sha256()` — pick the algorithm directly.
- `hashlib.new(algo, ...)` — pick it by **name** (a string), so the algorithm can come from a variable, detection logic, or user input. This is the unlock for supporting multiple algorithms without hardcoding.
- Input must be **bytes** → `word.encode()` turns a string into bytes.
- `.hexdigest()` → returns the hash as a readable hex **string**.
### 1.6 File streaming (how to read a huge wordlist safely)
 
```python
with open(path, "r", encoding="latin-1") as f:
    for line in f:
        word = line.strip()
```
 
- `with open(...) as f:` — opens the file and **auto-closes** it when done (like `.close()` on a socket, handled for you).
- **`f` is a file *object* — a stream/handle, NOT a list.** The whole file is *not* loaded into memory. `for line in f:` pulls **one line at a time**, processes it, discards it. That's why a 130MB / 14-million-line file doesn't blow your RAM.
- `"r"` = read mode (default).
- `encoding="latin-1"` = **decode** the file's bytes with a forgiving scheme that maps every byte 0–255 to a character, so messy password dumps with junk bytes don't crash (UTF-8 would raise `UnicodeDecodeError` on bad bytes). Note: reading = bytes → text = *decoding*; the parameter is named `encoding` because it means "the encoding the file is in."
- `.strip()` — **the #1 wordlist-cracker bug if forgotten.** Each line comes with a trailing newline: `"password\n"`. Hashing `"password\n"` gives a *totally different* hash than `"password"` (avalanche again) and never matches. `.strip()` removes it.
### 1.7 Relative vs absolute paths (+ Windows raw strings)
 
- `open("rockyou.txt")` is a **relative path** — it looks in the *current working directory* (where Python was launched from), which is **not necessarily** the folder your script lives in. Mismatch → `FileNotFoundError`, even with the file "right there."
- **Diagnose** with `os.getcwd()` (where Python is standing) and `os.listdir()` (what it can see) — *make the program tell you where it's looking*.
- **Fix** with an absolute path. On Windows, prefix it with `r"..."` — a **raw string** — because Windows paths use backslashes and `\n`, `\t` etc. are escape characters in a normal Python string. `r"C:\Users\new"` keeps the backslashes literal.
### 1.8 `argparse` — turning a script into a tool
 
```python
import argparse
parser = argparse.ArgumentParser(description="...")
parser.add_argument("hash", help="The target hash to crack.")
args = parser.parse_args()
target_hash = args.hash
```
 
- Lets the tool take arguments **on the command line** at launch: `python password-cracker.py <hash>` — no stopping to ask, so it's **scriptable/automatable** (every Kali tool works this way).
- `add_argument("hash", ...)` with **no dashes** = a **positional** (required) argument.
- `parse_args()` reads the command line; `args.hash` holds the value.
- **For free:** `--help` auto-generates a usage message, and missing required args produce a clean error — zero validation code written by you.
### 1.9 Two things that bit you (worth knowing)
 
- **`input()` needs a real terminal.** VS Code's Code Runner shows output in a **read-only** panel that can't accept typing — `input()` there just adds blank lines. Run interactive scripts in the **integrated terminal** (`python script.py`) instead.
- **A function that `print`s but doesn't `return` gives back `None`.** So `print(my_function())` prints the real output *and then* a stray `None`. Just **call** such a function (`my_function()`), don't wrap it in `print`.
---
 
## PART 2 — The Build Journey (your mistakes → fixes)
 
### Step 1 — Hash-and-compare core (one candidate)
 
**First attempt (correct from the start):**
```python
import hashlib
target = "5f4dcc3b5aa765d61d8327deb882cf99"
attempt = "wrongguess"
if target == hashlib.md5(attempt.encode()).hexdigest():
    print("Password found: " + attempt)
else:
    print("Wrong password")
```
 
Two subtle things you got right unprompted:
- **`attempt.encode()`** — converted the string to bytes (md5 needs bytes). Chose `.encode()` over `b"..."` — the version that *scales*, because you can't put a `b` prefix on a variable coming from a file.
- Compared **string to string** (`.hexdigest()` vs `target`) — matching types.
> **Lesson:** cracking = hash the *guess*, compare to the target. Never reverse.
 
### Step 2 — Loop over a wordlist (`for...else` + `break`)
 
```python
wordlist = ["123456", "qwerty", "letmein", "password", "admin"]
for w in wordlist:
    attempt = hashlib.md5(w.encode()).hexdigest()
    if target == attempt:
        print("Password found: " + w)
        break
else:
    print("Password not found")
```
 
You reached for **`for...else`** — the idiomatic pattern most beginners don't know.
 
> **Lesson:** `else` on a `for` loop = "run this **only if the loop never hit `break`**." So: `break` stops the instant you find a match (no point hashing the rest), and the `else` prints "not found" **exactly once** after the list is exhausted — not once per miss. Cleaner than a `found = False` flag.
 
### Step 3 — Read the real wordlist from a file
 
The autocomplete suggested an `open()` line with parameters you didn't understand — **you stopped and asked instead of pasting blindly.** That pause is the entire point of this project. The parameters: filename, `"r"` (read), `encoding="latin-1"` (forgiving decode for messy dumps). See 1.6.
 
> **Lesson:** don't run code you can't explain. Understanding `latin-1` (decode, survives junk bytes) and `f` being a *stream not a list* (see below) were the real gains.
 
**Correction you needed:** you first described `f` as "a list called f" that the file is appended into, and said `latin-1` "encodes" the characters. Both wrong:
- `f` is a **streaming handle**, not a list — `for line in f:` reads one line at a time; the 130MB file is never all in memory. *This is why it scales.*
- `latin-1` **decodes** (bytes → text), not encodes. Encoding is the other direction (`.encode()`).
### Step 4 — `FileNotFoundError` (path bug)
 
```
FileNotFoundError: [Errno 2] No such file or directory: 'rockyou.txt'
```
 
The file existed (VS Code even warned it was large), but `open("rockyou.txt")` looked in the **current working directory**, not the script's folder.
 
**Fix:** absolute path with a raw string:
```python
with open(r"C:\devPROJECTS\...\rockyou.txt", "r", encoding="latin-1") as f:
```
 
> **Lesson:** a relative path searches where Python was *launched*, not where the script *lives*. Diagnose with `os.getcwd()` / `os.listdir()`; fix with an absolute `r"..."` path (raw string, so Windows backslashes aren't read as escapes). First real crack: `5f4dcc... → password`, against 14 million candidates.
 
### Step 5 — Multi-algorithm (MD5 / SHA1 / SHA256)
 
Hardcoding `hashlib.md5(...)` only handles one algorithm. You detected it from length and parameterized it:
 
```python
if   len(target_hash) == 32: algo = "md5"
elif len(target_hash) == 40: algo = "sha1"
elif len(target_hash) == 64: algo = "sha256"
else:
    print("Unknown hash type"); exit()
...
attempt = hashlib.new(algo, word.encode()).hexdigest()   # algo is now a VARIABLE
```
 
> **Lesson:** `hashlib.new(algo, ...)` makes the algorithm **data you decide at runtime** instead of hardcoded. `exit()` on an unknown length = fail early, before a pointless scan. Verified the switch with a 64-char SHA256 hash → still cracked, proving detection genuinely changes algorithm.
 
### Step 6 — The case questions (hash vs password)
 
You asked the right cautious question — *"would lowercasing break integrity?"* — before transforming input. The answer split in two:
- **Hash case** (`5F` vs `5f`): cosmetic, same hex value → **safe** to `.lower()` the target. Without it, an uppercase pasted hash would **silently** never match (a `"not found"` lie), the worst kind of bug.
- **Password case** (`Password` vs `password`): different input → different hash (avalanche) → **never** lowercase the candidate.
```python
target_hash = args.hash.strip().lower()   # normalize the HASH only
```
 
> **Lesson:** normalize input you don't control — but know *which* input is safe to normalize. Hex case is cosmetic; password case is sacred.
 
### Step 7 — Take the hash as input (`input()` → the Code Runner wall)
 
Replaced hardcoded `target` with `input(...)`. Pressing Enter just made new lines.
 
> **Lesson:** the bug wasn't the code — **Code Runner's output panel is read-only and can't accept input.** Run interactive scripts in the **integrated terminal** (`python script.py`). `input()` needs a real terminal.
 
### Step 8 — The stray `None`
 
`print(password_cracker())` printed the result **and** a trailing `None`.
 
> **Lesson:** a function with no `return` hands back `None`. `password_cracker()` *prints* its result and returns nothing, so wrapping it in `print(...)` prints that `None`. Fix: just **call** it — `password_cracker()`. (Functions that *act* vs functions that *return a value* are different patterns.)
 
### Step 9 — `argparse` (real CLI tool)
 
Replaced `input()` with command-line arguments (see 1.8). Now: `python password-cracker.py <hash>`.
 
> **Lesson:** `argparse` makes the tool scriptable and gives you `--help` + missing-argument validation for free. You placed the parser at **top level** (outside the function) — correct, since the command line is read once at startup. `--help` output was auto-generated from your two argparse lines.
 
### Step 10 — Attempt counter (+ a scope lesson)
 
```python
count = 0
for line in f:
    word = line.strip()
    count += 1
    ...
    if target_hash == attempt:
        print(f"Number of attempts: {count}")   # f-string
        break
else:
    print(f"Number of attempts: {count}")
```
 
You briefly had `count = 0` **twice** — once at top level, once inside the function — and correctly kept only the inner one.
 
> **Lesson:** a variable lives in the scope that uses it. The loop runs *inside* the function, so the function's `count` is the one that matters; the top-level one was dead code (the inner name **shadows** it). Also: f-strings (`f"...{count}..."`) embed numbers cleanly, no `str()` needed, unlike `"text" + count` which would error.
 
**The payoff — attempt counts make password strength visible:**
 
| Password | Attempt # | Why |
|---|---|---|
| `123456` | 1 | Literally line 1 of rockyou — the most common leaked password ever |
| `password` | 4 | Near the very top |
| `letmein` | 512 | Common, but deeper in the list |
| random (`Xq7#mLp2!vR`) | never found | Not in the wordlist at all |
 
> **Lesson:** crackability = how early you appear in the guess list. Depth in rockyou *is* a measure of how predictable a password is.
 
---
 
## PART 3 — Final Code (annotated)
 
```python
import hashlib
import argparse
 
# --- CLI setup (top level: the command line is read once at startup) ---
parser = argparse.ArgumentParser(description="Crack a password hash using a wordlist.")
parser.add_argument("hash", help="The target hash to crack.")   # positional = required
args = parser.parse_args()                                       # --help + validation for free
 
def password_cracker():
    target_hash = args.hash.strip().lower()   # normalize the HASH (hex case is cosmetic) — never the password
    algo = ""
    count = 0
 
    # --- Detect algorithm from hash length ---
    if   len(target_hash) == 32: algo = "md5"
    elif len(target_hash) == 40: algo = "sha1"
    elif len(target_hash) == 64: algo = "sha256"
    else:
        print("Unknown hash type")
        exit()                                 # fail early, before scanning
 
    # --- Stream the wordlist one line at a time (f is a handle, NOT a list) ---
    with open(r"C:\devPROJECTS\Cyber-Labs\05-python-security-toolkit\password-cracker\rockyou.txt",
              "r", encoding="latin-1") as f:    # latin-1 = forgiving decode for messy dumps
        for line in f:
            word = line.strip()                 # strip the trailing \n or it hashes wrong
            count += 1
            attempt = hashlib.new(algo, word.encode()).hexdigest()  # hash the GUESS
            if target_hash == attempt:          # compare hashes — never reverse
                print("Password found: " + word)
                print(f"Number of attempts: {count}")
                break                           # stop the instant we find it
        else:                                   # for...else: runs only if no break happened
            print("Password not found")
            print(f"Number of attempts: {count}")
 
print("Welcome to the Password Cracker!")
password_cracker()                              # call it — don't print() it (would show None)
```
 
**Run it:**
```
python password-cracker.py 5f4dcc3b5aa765d61d8327deb882cf99
python password-cracker.py --help
```
 
**Known rough edges to tidy later (not bugs):**
- **Hardcoded wordlist path.** Portable version: derive it from the script's own location —
  `os.path.join(os.path.dirname(os.path.abspath(__file__)), "rockyou.txt")` — so it works on any machine.
- **The "Welcome" banner prints even on `--help`/errors.** Real CLI tools keep output clean; move it or drop it.
- **`exit()`** works but is really meant for interactive use; `sys.exit()` (with `import sys`) is the proper script version.
---
 
## PART 4 — Key Transferable Lessons (quick recap)
 
1. **Cracking is guessing, not reversing.** You hash the *guess* and compare; hashes are one-way. You can only crack what's already in your wordlist.
2. **Avalanche effect:** one changed character (incl. case) → a completely different hash. Hashes reveal nothing about how similar two inputs were.
3. **Hash case is cosmetic; password case is sacred.** `.lower()` the target hash (safe); never the candidate word (destructive).
4. **Hash length hints the algorithm:** 32=MD5, 40=SHA1, 64=SHA256. `hashlib.new(algo, ...)` makes the algorithm a runtime variable.
5. **`f` is a streaming handle, not a list.** `for line in f:` reads one line at a time — that's what lets a 14-million-line file not blow memory.
6. **Always `.strip()` file lines.** A trailing `\n` changes the hash and silently breaks matching. (#1 wordlist-cracker bug.)
7. **Relative paths search where Python *launched*, not where the script *lives*.** Diagnose with `os.getcwd()`/`os.listdir()`; fix with an absolute `r"..."` raw-string path on Windows.
8. **`argparse` = a real tool.** Command-line args make it scriptable; `--help` and validation come free. Put the parser at top level.
9. **`input()` needs a real terminal.** Code Runner's output panel is read-only — run in the integrated terminal.
10. **A function with no `return` gives `None`.** Call action-functions directly; don't `print()` them.
11. **Variables live in their scope.** A name defined inside a function is separate from a top-level one; the inner shadows the outer. Delete dead duplicates.
12. **Normalize input you don't control — but know which input is safe to normalize.** (Same lesson as the scanner: clean at the boundary, but understand what you're cleaning.)
13. **Silent failures are the dangerous ones.** An uppercase hash quietly printing "not found," like a bare `except` hiding a bug — a wrong answer you trust beats a crash you can't miss. Prevent them structurally.
---
 
*Built 29 Oct 2026, one stage at a time. The point was never the file — it was understanding every line of it.*
 
Claude finished the response
