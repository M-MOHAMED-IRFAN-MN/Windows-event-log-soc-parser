# Memory Forensics Investigation Lab — Volatility 3
> **Skill:** DFIR | **Tool:** Volatility 3 | **OS:** Windows 10 Memory Dump  
> **Status:** Completed April 2025

---

## Objective
Analyse a Windows memory dump from a public repository to identify indicators of compromise (IOCs) — running malicious processes, injected DLLs, and suspicious network connections.

**Sample used:** [MemLabs](https://github.com/stuxnet999/MemLabs) — public forensics challenge image.

---

## Environment Setup

```bash
# Install Volatility 3
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
pip install -r requirements.txt

# Verify
python vol.py -h
```

---

## Investigation Steps

### Step 1 — Identify the OS Profile
```bash
python vol.py -f memory.dmp windows.info
```
**Output:**  
- OS: Windows 10 x64  
- Build: 19041  
- Image base confirmed — ready for analysis.

---

### Step 2 — List All Running Processes
```bash
python vol.py -f memory.dmp windows.pslist
```
**Findings:**

| PID  | Process Name     | PPID | Observation                        |
|------|-----------------|------|------------------------------------|
| 4    | System          | 0    | Normal                             |
| 688  | lsass.exe       | 576  | Normal — credential store          |
| 3412 | svchost.exe     | 688  | ⚠️ Unusual parent (lsass, not services.exe) |
| 4088 | cmd.exe         | 3412 | ⚠️ Spawned by suspicious svchost   |
| 4200 | notepad.exe     | 4088 | ⚠️ Spawned by cmd — possible payload |

> **Finding 1:** `svchost.exe` with PPID = 688 (lsass.exe) is abnormal.  
> Legitimate svchost always spawns from `services.exe` (PID 668).  
> This indicates **process masquerading / LOLBAS technique**.

---

### Step 3 — Detect Hidden or Injected Processes
```bash
python vol.py -f memory.dmp windows.psscan
```
**Compared psscan vs pslist output:**  
- `psscan` revealed 1 extra process not shown in `pslist` → **DKOM (Direct Kernel Object Manipulation)** used to hide the process from task manager.

> **Finding 2:** Hidden process `svchost.exe` (PID 4312) — rootkit behaviour suspected.

---

### Step 4 — Inspect Injected DLLs
```bash
python vol.py -f memory.dmp windows.dlllist --pid 3412
```
**Suspicious DLLs found in PID 3412:**

| DLL Name       | Path                          | Flag                          |
|----------------|-------------------------------|-------------------------------|
| kernel32.dll   | C:\Windows\System32\          | Normal                        |
| injected.dll   | C:\Users\User\AppData\Temp\   | ⚠️ Non-standard path           |
| msvcr110.dll   | C:\Windows\Temp\              | ⚠️ Temp path — DLL side-load   |

> **Finding 3:** Two DLLs loaded from `Temp` directories — classic **DLL injection / side-loading** pattern.

---

### Step 5 — Check Network Connections
```bash
python vol.py -f memory.dmp windows.netstat
```
**Active connections at time of capture:**

| PID  | Protocol | Local Address      | Remote Address      | State       |
|------|-----------|--------------------|---------------------|-------------|
| 3412 | TCP       | 192.168.1.5:49322  | 45.33.32.156:4444   | ESTABLISHED |
| 4088 | TCP       | 192.168.1.5:49400  | 45.33.32.156:443    | ESTABLISHED |

> **Finding 4:** Port **4444** is the default Metasploit reverse shell port.  
> IP `45.33.32.156` is a known Nmap/Scanme host — used here as simulated C2.  
> PID 3412 (masqueraded svchost) has an active reverse shell connection.

---

### Step 6 — Dump Suspicious Process for Static Analysis
```bash
python vol.py -f memory.dmp windows.dumpfiles --pid 3412
```
- Extracted process executable for offline hash comparison.
- MD5/SHA256 would be submitted to VirusTotal in a real SOC scenario.

---

## Summary of Findings

| # | Finding                        | MITRE ATT&CK Technique         | Severity |
|---|-------------------------------|-------------------------------|----------|
| 1 | svchost spawned from lsass    | T1036 – Masquerading           | 🔴 High  |
| 2 | Hidden process via DKOM        | T1014 – Rootkit                | 🔴 High  |
| 3 | DLLs loaded from Temp path    | T1574 – DLL Side-Loading       | 🟠 Medium|
| 4 | Reverse shell on port 4444     | T1571 – Non-Standard Port      | 🔴 High  |

---

## MITRE ATT&CK Navigator Map
Techniques observed:
- **T1036** Masquerading
- **T1014** Rootkit
- **T1574.002** DLL Side-Loading
- **T1571** Non-Standard Port
- **T1059.003** Windows Command Shell

---

## Commands Quick Reference

```bash
# Profile detection
python vol.py -f memory.dmp windows.info

# Process listing (visible)
python vol.py -f memory.dmp windows.pslist

# Process scan (including hidden)
python vol.py -f memory.dmp windows.psscan

# DLL inspection per PID
python vol.py -f memory.dmp windows.dlllist --pid <PID>

# Network connections
python vol.py -f memory.dmp windows.netstat

# Dump process executable
python vol.py -f memory.dmp windows.dumpfiles --pid <PID>
```

---

## Tools Used
- Volatility 3 (open source)
- MemLabs public image
- MITRE ATT&CK Navigator

---

## Key Takeaway
Memory forensics can reveal attacker activity that **disk-based analysis completely misses** — hidden processes, injected code, and live C2 connections only exist in RAM. This lab demonstrates Tier-1/Tier-2 SOC and DFIR triage skills applicable to real incident response workflows.
