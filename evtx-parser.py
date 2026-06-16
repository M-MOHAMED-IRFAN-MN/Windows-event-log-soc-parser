from Evtx.Evtx import Evtx
import csv
import sys


def parse_login_events(evtx_file, output_csv):
      NS = {"e": "http://schemas.microsoft.com/win/2004/08/events/event"}
      events = []

      with Evtx(evtx_file) as log:
            for record in log.records():
                  try:
                        xml = record.lxml()
                        eid = xml.find('.//e:EventID', NS)
                        if eid is None or int(eid.text) not in (4624, 4625):
                              continue
                        eid = int(eid.text)
                        tc = xml.find('.//e:TimeCreated', NS)
                        ts = tc.get('SystemTime', '') if tc is not None else ''
                        d = {n.get('Name'): n.text for n in xml.findall('.//e:Data', NS)}
                        events.append({
                              'EventID': eid,
                              'Type': 'SUCCESS' if eid == 4624 else 'FAILED',
                              'Timestamp': ts,
                              'Username': d.get('TargetUserName', 'N/A'),
                              'Domain': d.get('TargetDomainName', 'N/A'),
                              'LogonType': d.get('LogonType', 'N/A'),
                              'SourceIP': d.get('IPAddress', 'N/A'),
                              'Workstation': d.get('WorkstationName', 'N/A'),
                        })
                  except Exception:
                        continue

      if not events:
            print(f"[!] No matching login events found in {evtx_file}")
            return

      with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(events[0].keys()))
            writer.writeheader()
            writer.writerows(events)

      failed = sum(1 for e in events if e['Type'] == 'FAILED')
      success = sum(1 for e in events if e['Type'] == 'SUCCESS')
      print(f"[+] {len(events)} login events saved  -> {output_csv}")
      print(f"         SUCCESS : {success} | FAILED : {failed}")
      if failed > 5:
            print(f"[!] ALERT : {failed} failed logins - possible brute-force activity!")


if __name__ == '__main__':
      if len(sys.argv) != 3:
            print("usage : python evtx_parser.py <Security.evtx> <output.csv>")
            sys.exit(1)
      parse_login_events(sys.argv[1], sys.argv[2])