# Lab Setup — Phase 0

**Date:** 4 April 2026
**Host OS:** Windows [your version] / VirtualBox [version]

## Virtual Machines

| VM | OS | IP | Purpose |
|----|----|----|---------|
| Kali Linux | Kali 2024.x | 192.168.56.105/24 brd 192.168.56.255sudo  | Attacker |
| Ubuntu Server | Ubuntu 22.04 | 192.168.56.104/24 brd 192.168.56.255 | Target |
| Metasploitable 2 | Ubuntu 8.04 | 192.168.56.106 brd 192.168.56.255 | Vulnerable target |
| Juice Shop | Docker on Kali | localhost:3000 | Web app target |

## Tools Verified

| Tool | Version | Status |
|------|---------|--------|
| nmap | 7.95 | ✅ |
| Burp Suite | 2025.7.4 | ✅ |
| Wireshark | 4.4.7 | ✅ |
| Metasploit | 6.4.84 | ✅ |
| Python 3 | 3.13.7 | ✅ |
| Docker | 28.5.2| ✅ |

## Network Verification
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  open  netbios-ssn Samba smbd 3.0.20-Debian (workgroup: WORKGROUP)
512/tcp  open  exec        netkit-rsh rexecd
513/tcp  open  login       OpenBSD or Solaris rlogind
514/tcp  open  tcpwrapped
1099/tcp open  java-rmi    GNU Classpath grmiregistry
1524/tcp open  bindshell   Metasploitable root shell
2049/tcp open  nfs         2-4 (RPC #100003)
2121/tcp open  ftp         ProFTPD 1.3.1
3306/tcp open  mysql       MySQL 5.0.51a-3ubuntu5

