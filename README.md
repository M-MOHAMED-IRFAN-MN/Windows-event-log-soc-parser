🔐 Windows Event Log SOC Parser
A lightweight Python-based EVTX parser for Security Operations Center (SOC) analysts to detect and investigate Windows authentication anomalies.
📋 Overview
This tool extracts Windows Security Event Logon events (Event ID 4624 - Successful Logon & 4625 - Failed Logon) from .evtx files and converts them into structured CSV format for SOC analysis, threat hunting, and incident triage.
Built for SOC analysts who need to quickly parse Windows authentication logs to identify brute-force attacks, suspicious login patterns, and lateral movement indicators.
✨ Features
🎯 Targeted Event Extraction — Focuses on critical Event IDs 4624 & 4625 (Logon Success/Failure)
📊 CSV Export — Structured output for Excel, Splunk, ELK, or any SIEM ingestion
🚨 Built-in Alerting — Auto-detects brute-force patterns (configurable threshold: >5 failed logins)
🔍 Key SOC Fields — Extracts: Username, Domain, Logon Type, Source IP, Workstation Name, Timestamp
⚡ Lightweight — Zero external dependencies beyond python-evtx
🛡️ Error Resilient — Skips malformed XML records without crashing
🛠️ Requirements
Table
Dependency	Version
Python	3.7+
python-evtx	Latest
bash
pip install python-evtx
🚀 Installation
bash
# Clone the repository
git clone https://github.com/M-MOHAMED-IRFAN-MN/Windows-event-log-soc-parser.git
cd Windows-event-log-soc-parser

# Install dependency
pip install python-evtx
📖 Usage
Basic Command
bash
python evtx_parser.py <Security.evtx> <output.csv>
Example
bash
python evtx_parser.py C:\Windows\System32\winevt\Logs\Security.evtx login_analysis.csv
Sample Output
plain
[+] 1,247 login events saved  -> login_analysis.csv
         SUCCESS : 1,102 | FAILED : 145
[!] ALERT : 145 failed logins - possible brute-force activity!
📊 Output CSV Schema
Table
Field	Description	SOC Relevance
EventID	Windows Event ID (4624/4625)	Event classification
Type	SUCCESS or FAILED	Quick triage filter
Timestamp	ISO 8601 system time	Timeline correlation
Username	Target account name	Compromised account detection
Domain	Target domain	Domain-wide attack scope
LogonType	Authentication method (2,3,4,7,10...)	Remote vs. local access
SourceIP	Originating IP address	Geo-location & threat intel
Workstation	Source workstation name	Lateral movement tracking
Logon Type Quick Reference
Table
Type	Meaning	SOC Use Case
2	Interactive (Console)	Physical access
3	Network (SMB/RDP)	Lateral movement
4	Batch (Scheduled Task)	Persistence
7	Unlock	Session hijacking
10	Remote Interactive (RDP)	Remote access attacks
🎯 SOC Use Cases
1. Brute-Force Detection
The parser automatically alerts when failed logins exceed 5 attempts:
plain
[!] ALERT : 145 failed logins - possible brute-force activity!
2. RDP Attack Investigation
Filter by LogonType = 10 and Type = FAILED to identify RDP brute-force campaigns.
3. Lateral Movement Detection
Correlate SourceIP and Workstation fields across multiple hosts to map attacker movement.
4. Compromised Account Triage
Sort by Username with high FAILED counts followed by SUCCESS to find successfully breached accounts.
5. SIEM Ingestion
Import the CSV into Splunk, ELK, or Sentinel for dashboarding and correlation:
bash
# Splunk HEC example
curl -k https://splunk:8088/services/collector/event \
  -H "Authorization: Splunk <token>" \
  -d '{"event": {"file": "login_analysis.csv", "source": "evtx_parser"}}'
🔧 Customization
Adjust Brute-Force Threshold
Edit line 47 in evtx_parser.py:
Python
if failed > 5:  # Change to your SOC threshold
Add More Event IDs
Extend the tuple to include other Security events:
Python
if eid is None or int(eid.text) not in (4624, 4625, 4648, 4672):
📁 File Structure
plain
Windows-event-log-soc-parser/
├── evtx_parser.py          # Main parser script
├── README.md               # This documentation
└── examples/
    └── sample_output.csv   # Example parsed output
🛡️ Security Considerations
Run with least privilege — Only access .evtx files you own or are authorized to analyze
Handle CSV outputs securely — Contains sensitive authentication data
Timestamp accuracy — Ensure system clock sync for accurate timeline analysis
IP validation — SourceIP may show 127.0.0.1 or ::1 for local logons
📝 To-Do / Roadmap
[ ] Add Event ID 4648 (Explicit Credential Logon) support
[ ] JSON output format for modern SIEMs
[ ] GeoIP enrichment for SourceIP
[ ] Multi-file batch processing
[ ] Config file for customizable thresholds
[ ] Integration with MITRE ATT&CK mapping
🤝 Contributing
Contributions welcome! Open an issue or PR for:
New Event ID support
Output format enhancements
Performance optimizations
Bug fixes
📜 License
MIT License — Free for personal and commercial SOC use.
👤 Author
Mohamed Irfan MN
🔒 Cybersecurity | SOC | SIEM | Log Analysis | Threat Detection | Incident Triage
📍 Chennai, India
🌐 Portfolio
💼 LinkedIn
🙏 Acknowledgments
python-evtx by Willi Ballenthin — The core EVTX parsing library
Windows Security Log Events reference by Microsoft Docs
"In SOC, every logon tells a story. This parser helps you read it." 🛡️
If you want, I can also add:
A requirements.txt file content
Sample CSV output example
MITRE ATT&CK mapping for each logon type
PowerShell one-liner to export Security.evtx for analysis
Let me know what you'd like to enhance!
