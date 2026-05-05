# 🏆 CTF Writeups

> All Capture The Flag writeups across TryHackMe, HackTheBox, and live events.
> Updated every Wednesday after each session.

---

## 📁 Structure

| Folder | Platform | Purpose |
|--------|----------|---------|
| [`thm/`](thm/) | TryHackMe | Learning path rooms — Pre-Security and Jr Pentester |
| [`htb/`](htb/) | HackTheBox | Starting Point and retired machines |
| [`events/`](events/) | Live CTFs | Monthly competition post-mortems |

---

## 📊 Progress Tracker

### TryHackMe

| Room | Path | Date | Difficulty | Status |
|------|------|------|------------|--------|
| How the Web Works | Pre-Security | | Easy | ⏳ |
| Linux Fundamentals Part 1 | Pre-Security | | Easy | ⏳ |
| Linux Fundamentals Part 2 | Pre-Security | | Easy | ⏳ |
| Linux Fundamentals Part 3 | Pre-Security | | Easy | ⏳ |
| Network Fundamentals | Pre-Security | | Easy | ⏳ |
| How the Internet Works | Pre-Security | | Easy | ⏳ |
| Intro to Pentesting | Jr Pentester | | Easy | ⏳ |
| Network Security | Jr Pentester | | Easy | ⏳ |
| Web App Security | Jr Pentester | | Easy | ⏳ |
| Privilege Escalation | Jr Pentester | | Easy | ⏳ |
| Metasploit | Jr Pentester | | Easy | ⏳ |

**Completed:** 0 / 11

---

### HackTheBox — Starting Point

| Machine | Tier | OS | Date | Status |
|---------|------|----|------|--------|
| Meow | Tier 0 | Linux | | ⏳ |
| Fawn | Tier 0 | Linux | | ⏳ |
| Dancing | Tier 0 | Windows | | ⏳ |
| Redeemer | Tier 0 | Linux | | ⏳ |
| Appointment | Tier 1 | Linux | | ⏳ |
| Sequel | Tier 1 | Linux | | ⏳ |
| Crocodile | Tier 1 | Linux | | ⏳ |
| Responder | Tier 1 | Windows | | ⏳ |
| Archetype | Tier 2 | Windows | | ⏳ |
| Oopsie | Tier 2 | Linux | | ⏳ |
| Vaccine | Tier 2 | Linux | | ⏳ |
| Unified | Tier 2 | Linux | | ⏳ |

**Completed:** 0 / 12

---

### HackTheBox — Retired Machines

| Machine | OS | Difficulty | Date | Key Technique | Writeup |
|---------|----|------------|------|---------------|---------|
| — | — | — | — | — | — |

**Completed:** 0

---

### Live CTF Events

| Event | Date | Category | Solves | Post-Mortem |
|-------|------|----------|--------|-------------|
| — | — | — | — | — |

**Events participated:** 0

---

## 📈 Overall Stats

| Metric | Count |
|--------|-------|
| TryHackMe rooms completed | 0 |
| HTB Starting Point machines | 0 |
| HTB Retired machines | 0 |
| Live CTF events | 0 |
| Total writeups published | 0 |

---

## 📝 Writeup Template

Copy this template every time you start a new writeup. Save it in the
correct subfolder with a clear filename e.g. `thm-linux-fundamentals-1.md`
or `htb-blue.md`

```markdown
# [Platform]: [Machine/Room Name] — Writeup

**Date:** 
**Platform:** TryHackMe / HackTheBox / CTF Event
**Difficulty:** Easy / Medium / Hard
**OS:** Linux / Windows (HTB only)
**Category:** 
**Tags:** 
**Status:** ✅ Completed

---

## 📌 Summary

One paragraph. What was the machine or room about, what was the
attack path, what did you learn. Write this last even though it
appears first.

---

## 🔍 Enumeration

What you found when you first looked at the target.
What tools you used and why.
What stood out as interesting.

​```bash
# Example — always explain what each command does
nmap -sV -sC -T4 TARGET_IP -oN scan.txt
# -sV detects service versions
# -sC runs default scripts for extra info
# -T4 speeds up the scan for local lab use
# -oN saves output to a readable text file
​```

---

## 🚪 Initial Access / Exploitation

How you got your first foothold on the target.
What vulnerability you found and why it worked.
Exact commands with explanations of each step.

​```bash
# Example
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.10.10.40
set LHOST tun0   # tun0 is your VPN interface for HTB
run
​```

---

## ⬆️ Privilege Escalation

How you went from low-privilege user to root or administrator.
What you checked, what you found, how you used it.
Skip this section if you got root/SYSTEM access directly.

​```bash
# Example — checking for SUID binaries on Linux
find / -perm -u=s -type f 2>/dev/null
​```

---

## 🏁 Flags

​```
user.txt: [flag value]
root.txt: [flag value]
​```

---

## 💡 Lessons Learned

- What did this challenge teach you
- What would you do differently next time
- What new technique, tool, or concept did you discover
- Any rabbit holes you went down and why they didn't work

---

## 🛠️ Commands Reference

Quick reference of every important command used in this writeup.

| Command | Purpose |
|---------|---------|
| `nmap -sV -sC -T4 IP` | Full service and script scan |
| `nmap --script smb-vuln-ms17-010 IP` | Check specific SMB vulnerability |
| `find / -perm -u=s -type f 2>/dev/null` | Find SUID binaries for privesc |
```

---

## 🔗 Platform Profiles

- TryHackMe: [Add your profile link]
- HackTheBox: [Add your profile link]

---

*Part of the [Cyber-Labs](../README.md) 24-month Red Team Roadmap*
