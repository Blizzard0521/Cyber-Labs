# 📁 Phase 1 — Linux, Networking & Physical Locks

**Start Date:** 4 May 2026
**End Date:** 26 July 2026
**Duration:** 12 weeks
**Books:** Linux Basics for Hackers (B-100) + Learn Wireshark (B-220)
**Status:** 🔄 In Progress

---

## 🎯 Phase Objectives

- Become fluent with the Linux command line and bash scripting
- Understand network protocols and packet analysis using Wireshark
- Build a reusable bash scripting toolkit (10 scripts)
- Capture and annotate real network traffic (3 pcap files)
- Complete TryHackMe Pre-Security and Jr Penetration Tester paths
- Master Single Pin Picking (SPP) on a practice lock

---

## 📚 Reading Progress

### Linux Basics for Hackers (B-100)

| Chapter | Topic | Priority | Status | Date Done |
|---------|-------|----------|--------|-----------|
| Ch1 | Getting Started | Must Read | ⏳ | |
| Ch2 | Text Manipulation | Must Read | ⏳ | |
| Ch3 | Analyzing and Managing Networks | Must Read | ⏳ | |
| Ch4 | Adding and Removing Software | Skim | ⏳ | |
| Ch5 | Controlling File Permissions | Must Read | ⏳ | |
| Ch6 | Process Management | Must Read | ⏳ | |
| Ch7 | Managing User Environment Variables | Selective | ⏳ | |
| Ch8 | Bash Scripting | Must Read | ⏳ | |
| Ch9 | Compressing and Archiving | Skim | ⏳ | |
| Ch10 | Filesystem and Storage | Selective | ⏳ | |
| Ch11 | The Logging System | Must Read | ⏳ | |
| Ch12 | Using and Abusing Services | Must Read | ⏳ | |
| Ch13 | Becoming Secure and Anonymous | Selective | ⏳ | |
| Ch14 | Wireless Networks | SKIP | ❌ | N/A |
| Ch15 | Managing the Linux Kernel | Skim | ⏳ | |
| Ch16 | Automating Tasks with Job Scheduling | Must Read | ⏳ | |
| Ch17 | Python Scripting Basics for Hackers | Must Read | ⏳ | |

### Learn Wireshark (B-220) — Selective Read

| Chapter | Topic | Priority | Scheduled Week | Status | Date Done |
|---------|-------|----------|---------------|--------|-----------|
| Ch1 | Introduction to Wireshark | Read | Week 1 Saturday | ⏳ | |
| Ch2 | Capturing Packets | Read | Week 2 Saturday | ⏳ | |
| Ch3 | Filters | Read | Week 3 Saturday | ⏳ | |
| Ch4 | Protocol Overview | Skim | Week 4 Saturday | ⏳ | |
| Ch5 | TCP/IP Analysis | Read | Week 5 Saturday | ⏳ | |
| Ch6 | HTTP and DNS | Read | Week 6 Saturday | ⏳ | |
| Ch7 | Following Streams | Read | Week 8 Saturday | ⏳ | |
| Ch8 | Statistics and Graphs | Skim | Week 9 Saturday | ⏳ | |
| Ch9 | Wireless Analysis | SKIP | — | ❌ | N/A |
| Ch10+ | Advanced Features | SKIP | — | ❌ | N/A |

---

## 🛠️ Bash Scripts Deliverables

> All scripts saved in this folder with individual READMEs and example output.

| # | Script | Description | Status | Date |
|---|--------|-------------|--------|------|
| 1 | user-management.sh | Create, delete, modify Linux users | ⏳ | |
| 2 | cron-setup.sh | Automate scheduled tasks with cron | ⏳ | |
| 3 | log-rotation.sh | Manage and rotate system logs | ⏳ | |
| 4 | file-permissions.sh | Audit and fix file permissions | ⏳ | |
| 5 | port-scanner.py | Basic TCP/UDP port scanner in Python | ⏳ | |
| 6 | network-info.sh | Display full network configuration | ⏳ | |
| 7 | process-monitor.sh | Monitor running processes and kill by name | ⏳ | |
| 8 | backup.sh | Automated file and directory backup | ⏳ | |
| 9 | service-checker.sh | Check status of key system services | ⏳ | |
| 10 | sys-info.sh | Generate a full system information report | ⏳ | |

---

## 📦 Packet Captures

> All pcap files saved in `/02-pcaps/` with written annotations.

| File | Protocol | Description | Status | Date |
|------|----------|-------------|--------|------|
| http.pcap | HTTP | Captured from Juice Shop web traffic | ⏳ | |
| dns.pcap | DNS | DNS queries from lab network | ⏳ | |
| tls.pcap | TLS | Encrypted HTTPS traffic sample | ⏳ | |

---

## 🏆 CTF Progress

> All writeups saved in `/ctf-writeups/thm/`

### TryHackMe — Pre-Security Path

| Room | Topic | Status | Date | Writeup |
|------|-------|--------|------|---------|
| How the Web Works | HTTP, DNS, URLs | ⏳ | | |
| Linux Fundamentals Part 1 | Basic commands, navigation | ⏳ | | |
| Linux Fundamentals Part 2 | Permissions, scripting | ⏳ | | |
| Linux Fundamentals Part 3 | Automation, services | ⏳ | | |
| Network Fundamentals | TCP/IP, OSI model, packets | ⏳ | | |
| How the Internet Works | Protocols overview | ⏳ | | |

### TryHackMe — Jr Penetration Tester Path

| Room | Topic | Status | Date | Writeup |
|------|-------|--------|------|---------|
| Intro to Pentesting | Methodology and mindset | ⏳ | | |
| Network Security | nmap, services, enumeration | ⏳ | | |
| Web Application Security | OWASP Top 10 basics | ⏳ | | |
| Privilege Escalation | Linux privesc techniques | ⏳ | | |
| Metasploit | Framework basics and modules | ⏳ | | |

---

## 🔒 Spy Track — Physical Locks

| Week | Milestone | Status | Date |
|------|-----------|--------|------|
| 1–2 | Study lock anatomy: springs, driver pins, shear line, plug | ⏳ | |
| 3–4 | First successful Single Pin Pick on clear practice lock | ⏳ | |
| 5–6 | Consistent SPP — open practice lock in under 3 minutes | ⏳ | |
| 7–8 | Progress to raking technique on a cheap padlock | ⏳ | |
| 9–10 | Open basic padlock in under 60 seconds | ⏳ | |
| 11–12 | Attempt a second lock type | ⏳ | |

---

## 📋 Weekly Log

> **Monday** = Must-read B-100 chapter. Full 2-hour read, handwritten notes, 5-bullet summary committed to notes/
> **Saturday** = Skim/selective B-100 chapter + Wireshark chapter. 30–45 mins each, no pressure.
> **All 16 B-100 chapters + 8 Wireshark chapters must be completed by end of Week 12.**
> **Ch14 (Wireless Networks) — SKIP. Not relevant to red team path.**

| Week | Dates | Monday — B-100 | Saturday — B-100 | Saturday or Friday — Wireshark | Thursday Script | Wednesday CTF | Status |
|------|-------|---------------|-----------------|---------------------|-----------------|---------------|--------|
| 1 | 4–10 May | Ch1 — Getting Started | — | Ch1 — Introduction | user-management.sh | THM: How Web Works | ⏳ |
| 2 | 11–17 May | Ch2 — Text Manipulation | — | Ch2 — Capturing Packets | cron-setup.sh | THM: Linux Fund. 1 | ⏳ |
| 3 | 18–24 May | Ch3 — Networking | — | Ch3 — Filters | log-rotation.sh | THM: Linux Fund. 2 | ⏳ |
| 4 | 25–31 May | Ch5 — File Permissions | Ch4 — Adding Software (skim) | Ch4 — Protocol Overview (skim) | file-permissions.sh | THM: Linux Fund. 3 | ⏳ |
| 5 | 1–7 Jun | Ch6 — Process Management | Ch7 — Environment Variables (selective) | Ch5 — TCP/IP Analysis | port-scanner.py | THM: Network Fund. | ⏳ |
| 6 | 8–14 Jun | Ch8 — Bash Scripting | Ch9 — Compressing & Archiving (skim) | Ch6 — HTTP and DNS | network-info.sh | THM: How Internet Works | ⏳ |
| 7 | 15–21 Jun | Ch11 — Logging System | Ch10 — Filesystem & Storage (selective) | — | process-monitor.sh | THM: Intro to Pentesting | ⏳ |
| 8 | 22–28 Jun | Ch12 — Using & Abusing Services | Ch13 — Secure & Anonymous (selective) | Ch7 — Following Streams | backup.sh | THM: Network Security | ⏳ |
| 9 | 29 Jun–5 Jul | Ch16 — Job Scheduling | Ch15 — Linux Kernel (skim) | Ch8 — Statistics (skim) | service-checker.sh | THM: Web App Security | ⏳ |
| 10 | 6–12 Jul | Ch17 — Python Scripting | — | — | sys-info.sh | THM: Privilege Escalation | ⏳ |
| 11 | 13–19 Jul | Wireshark review + capture all 3 pcaps | Catch up any missed B-100 chapters | Catch up any missed Wireshark chapters | Wireshark pcaps | THM: Metasploit | ⏳ |
| 12 | 20–26 Jul | Full review + weak areas | Catch up anything missed | Catch up anything missed | Polish all scripts | Extra CTF room | ⏳ |
---

## 📝 Weekly Notes

*Update every Sunday during your review session. Record what you have learned, what confused you, any mistakes and all*

**Week 1 — 4 May:**

**Week 2 — 11 May:**

**Week 3 — 18 May:**

**Week 4 — 25 May:**

**Week 5 — 1 Jun:**

**Week 6 — 8 Jun:**

**Week 7 — 15 Jun:**

**Week 8 — 22 Jun:**

**Week 9 — 29 Jun:**

**Week 10 — 6 Jul:**

**Week 11 — 13 Jul:**

**Week 12 — 20 Jul:**

---

## ✅ Phase 1 Completion Checklist

- [ ] All 17 chapters of B-100 read with 5-bullet summaries in notes/
- [ ] Wireshark key chapters completed
- [ ] 10 bash scripts committed with individual READMEs
- [ ] 3 annotated pcap files saved in 02-pcaps/
- [ ] TryHackMe Pre-Security path fully completed
- [ ] TryHackMe Jr Penetration Tester path fully completed
- [ ] 10+ CTF writeups committed in ctf-writeups/thm/
- [ ] Practice lock opened consistently in under 60 seconds
- [ ] Phase 1 status updated to ✅ in main Cyber-Labs README
- [ ] All work committed and pushed to GitHub

---

*Phase 1 of 9 — [Cyber-Labs](../README.md)*
