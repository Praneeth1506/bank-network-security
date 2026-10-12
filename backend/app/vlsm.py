import ipaddress
import math


def block_size(hosts: int, growth: float) -> int:
    need = math.ceil(hosts * (1 + growth)) + 1 + 2   # hosts + gateway + network/broadcast
    return 1 << (need - 1).bit_length()              # round up to a power of two


def vlsm(block: str, vlans: list[dict], growth: float = 1.0) -> list[dict]:
    """Allocate largest block first; equal sizes keep input order."""
    parent = ipaddress.ip_network(block)
    cursor = int(parent.network_address)
    rows = []
    for v in sorted(vlans, key=lambda v: block_size(v["hosts"], growth), reverse=True):
        size = block_size(v["hosts"], growth)
        net = ipaddress.ip_network((cursor, 32 - (size.bit_length() - 1)))
        if not net.subnet_of(parent):
            raise ValueError(f"{block} is too small for VLAN {v['id']}")
        hosts = list(net.hosts())
        rows.append({
            "vlan": v["id"], "name": v["name"], "hosts_now": v["hosts"],
            "network": str(net.network_address), "prefix": net.prefixlen,
            "mask": str(net.netmask), "wildcard": str(net.hostmask),
            "first": str(hosts[0]), "last": str(hosts[-1]),
            "broadcast": str(net.broadcast_address),
            "gateway": str(hosts[0]), "usable": net.num_addresses - 2,
        })
        cursor += size
    return rows
