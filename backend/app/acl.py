from ipaddress import ip_address, ip_network

ANY = "0.0.0.0/0"
SERVER = "10.80.0.74/32"
KIOSK, TELLER, MANAGER = "10.80.0.0/27", "10.80.0.32/27", "10.80.0.64/29"

# Mirrors R1's ACLs: (action, proto, src, dst, dst_port, needs_established)
ACLS = {
    "KIOSK_IN": {"interface": "G0/0.10", "vlan_net": KIOSK, "rules": [
        ("permit", "udp", ANY, ANY, 67, False),
        ("permit", "tcp", KIOSK, SERVER, 80, False),
        ("permit", "tcp", KIOSK, SERVER, 443, False),
        ("permit", "tcp", KIOSK, MANAGER, None, True),
        ("permit", "icmp-reply", KIOSK, MANAGER, None, False),
        ("deny", "ip", ANY, ANY, None, False),
    ]},
    "TELLER_IN": {"interface": "G0/0.20", "vlan_net": TELLER, "rules": [
        ("permit", "tcp", TELLER, SERVER, 80, False),
        ("permit", "tcp", TELLER, SERVER, 443, False),
        ("permit", "tcp", TELLER, SERVER, 21, False),
        ("permit", "tcp", TELLER, SERVER, 20, False),
        ("permit", "tcp", TELLER, MANAGER, None, True),
        ("permit", "icmp-reply", TELLER, MANAGER, None, False),
        ("deny", "ip", TELLER, KIOSK, None, False),
        ("deny", "ip", TELLER, MANAGER, None, False),
        ("deny", "ip", ANY, ANY, None, False),
    ]},
}


def check(src, dst, proto, port=None, established=False):
    """First match wins, like IOS. proto: tcp | udp | icmp | icmp-reply.
    A DHCP Discover (src 0.0.0.0) is treated as arriving on the kiosk VLAN."""
    s, d = ip_address(src), ip_address(dst)
    for name, acl in ACLS.items():
        ingress = s in ip_network(acl["vlan_net"]) or (str(s) == "0.0.0.0" and name == "KIOSK_IN")
        if not ingress:
            continue
        for n, (action, p, rs, rd, rport, est) in enumerate(acl["rules"], start=1):
            if ((p == "ip" or p == proto) and s in ip_network(rs) and d in ip_network(rd)
                    and (rport is None or rport == port) and (not est or established)):
                return {"verdict": action, "acl": name, "interface": acl["interface"], "line": n}
    return {"verdict": "permit", "acl": None, "interface": None, "line": None,
            "note": "No ACL on the source VLAN (manager or server)"}
