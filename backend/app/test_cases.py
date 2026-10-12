"""Seed rows for the test tracker: docs/network_spec.md section 4, in order."""

TEST_CASES = [
    {"source": "KIOSK1", "destination": "R1", "test": "ipconfig (DHCP lease)", "expected": "Allowed"},
    {"source": "KIOSK1", "destination": "SRV1", "test": "Browser http://10.80.0.74", "expected": "Allowed"},
    {"source": "KIOSK1", "destination": "SRV1", "test": "Browser https://10.80.0.74", "expected": "Allowed"},
    {"source": "KIOSK1", "destination": "SRV1", "test": "ping 10.80.0.74", "expected": "Blocked"},
    {"source": "KIOSK1", "destination": "SRV1", "test": "ftp 10.80.0.74", "expected": "Blocked"},
    {"source": "KIOSK1", "destination": "TELLER1", "test": "ping 10.80.0.34", "expected": "Blocked"},
    {"source": "KIOSK1", "destination": "MGR1", "test": "ping 10.80.0.66", "expected": "Blocked"},
    {"source": "TELLER1", "destination": "SRV1", "test": "Browser http and https", "expected": "Allowed"},
    {"source": "TELLER1", "destination": "SRV1", "test": "ftp 10.80.0.74, login teller, put/get", "expected": "Allowed"},
    {"source": "TELLER1", "destination": "SRV1", "test": "ping 10.80.0.74", "expected": "Blocked"},
    {"source": "TELLER1", "destination": "KIOSK1", "test": "ping", "expected": "Blocked"},
    {"source": "TELLER1", "destination": "MGR1", "test": "ping 10.80.0.66", "expected": "Blocked"},
    {"source": "TELLER1", "destination": "R1", "test": "ssh -l admin 10.80.0.33", "expected": "Blocked"},
    {"source": "MGR1", "destination": "KIOSK1, TELLER1, SRV1", "test": "ping", "expected": "Allowed"},
    {"source": "MGR1", "destination": "SRV1", "test": "Browser and FTP (manager account)", "expected": "Allowed"},
    {"source": "MGR1", "destination": "R1, SW1, SW2", "test": "ssh -l admin 10.80.0.65 / .82 / .83", "expected": "Allowed"},
    {"source": "MGR1", "destination": "R1", "test": "telnet 10.80.0.65", "expected": "Blocked"},
    {"source": "ROGUE laptop", "destination": "SW2 Fa0/3", "test": "ping 10.80.0.33 (port security)", "expected": "Blocked"},
]
