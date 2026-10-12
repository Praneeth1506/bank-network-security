"""Single source of truth for the BankNet topology (docs/network_spec.md).

configgen.py renders R1, SW1 and SW2 from this module only; the templates in
templates/ hold IOS syntax but no addresses, names or passwords.
"""
from dataclasses import dataclass
from ipaddress import IPv4Network, ip_network


# ---- VLANs and addressing (spec section 1) ---------------------------------

@dataclass(frozen=True)
class Vlan:
    id: int
    name: str
    subnet: str | None = None       # None for VLANs without an IP (PARKING)

    @property
    def net(self) -> IPv4Network:
        return ip_network(self.subnet)

    @property
    def network(self) -> str:
        return str(self.net.network_address)

    @property
    def mask(self) -> str:
        return str(self.net.netmask)

    @property
    def wildcard(self) -> str:
        return str(self.net.hostmask)

    @property
    def gateway(self) -> str:       # first usable host, configured on R1
        return str(next(self.net.hosts()))


VLANS = (
    Vlan(10, "KIOSK", "10.80.0.0/27"),
    Vlan(20, "TELLER", "10.80.0.32/27"),
    Vlan(30, "MANAGER", "10.80.0.64/29"),
    Vlan(40, "SERVER", "10.80.0.72/29"),
    Vlan(99, "MGMT", "10.80.0.80/29"),
    Vlan(999, "PARKING"),
)
VLAN = {v.id: v for v in VLANS}
ROUTED_VLANS = tuple(v for v in VLANS if v.subnet)

MGMT_VLAN = VLAN[99]
PARKING_VLAN = VLAN[999]

# ---- Trunks (spec section 2) -----------------------------------------------

TRUNK_NATIVE_VLAN = PARKING_VLAN.id
TRUNK_ALLOWED_VLANS = tuple(v.id for v in ROUTED_VLANS)    # 10,20,30,40,99


@dataclass(frozen=True)
class EtherChannel:
    ports: str
    group: int
    mode: str


ETHERCHANNEL = EtherChannel("FastEthernet0/23 - 24", group=1, mode="active")

# ---- Shared credentials and management access ------------------------------

COMMON = {
    "enable_secret": "Bank@Enable26",
    "admin_user": "admin",
    "admin_privilege": 15,
    "admin_secret": "Bank@Admin26",
    "console_password": "Bank@Con26",
    "domain_name": "bank.local",
    "banner": "Authorized access only",
    "rsa_modulus": 1024,
    "exec_timeout": "5 0",
}

# access-list 10: only the MANAGER subnet may reach the VTY lines.
MGMT_ACL = {"number": 10, "vlan": VLAN[30]}

PORT_SECURITY = {"maximum": 1, "violation": "shutdown"}

# ---- Switches ---------------------------------------------------------------


@dataclass(frozen=True)
class AccessPorts:
    ports: str                      # "FastEthernet0/1 - 10" or "FastEthernet0/11"
    description: str
    vlan: int
    portfast: bool = False
    bpduguard: bool = False
    port_security: bool = False
    shutdown: bool = False

    @property
    def interface(self) -> str:
        kind = "interface range" if " - " in self.ports else "interface"
        return f"{kind} {self.ports}"


def unused(ports: str) -> AccessPorts:
    return AccessPorts(ports, "UNUSED", PARKING_VLAN.id, shutdown=True)


@dataclass(frozen=True)
class Uplink:
    port: str
    description: str


@dataclass(frozen=True)
class Switch:
    hostname: str
    svi_ip: str                     # address on interface Vlan99
    etherchannel_peer: str
    router_uplink: Uplink | None
    # Each inner tuple is printed as one "!"-terminated section.
    access_sections: tuple[tuple[AccessPorts, ...], ...]
    unused_ports: tuple[AccessPorts, ...]
    template: str = "switch.j2"


SW1 = Switch(
    hostname="SW1",
    svi_ip="10.80.0.82",
    etherchannel_peer="SW2",
    router_uplink=Uplink("GigabitEthernet0/1", "Trunk to R1 G0/0"),
    access_sections=(
        (AccessPorts("FastEthernet0/1 - 10", "KIOSK", 10, portfast=True, bpduguard=True),
         AccessPorts("FastEthernet0/11", "SRV1", 40, portfast=True)),
    ),
    unused_ports=(unused("FastEthernet0/12 - 22"), unused("GigabitEthernet0/2")),
)

SW2 = Switch(
    hostname="SW2",
    svi_ip="10.80.0.83",
    etherchannel_peer="SW1",
    router_uplink=None,
    access_sections=(
        (AccessPorts("FastEthernet0/1 - 8", "TELLER", 20, portfast=True, port_security=True),),
        (AccessPorts("FastEthernet0/9 - 10", "MANAGER", 30, portfast=True),),
    ),
    unused_ports=(unused("FastEthernet0/11 - 22"), unused("GigabitEthernet0/1 - 2")),
)

# ---- Router -----------------------------------------------------------------


@dataclass(frozen=True)
class DhcpPool:
    name: str
    vlan: Vlan
    excluded: tuple[str, str]       # first and last excluded address


@dataclass(frozen=True)
class ExtendedAcl:
    name: str
    vlan: Vlan                      # applied inbound on R1's subinterface for this VLAN
    lines: tuple[str, ...]


DHCP_POOLS = (DhcpPool("KIOSK", VLAN[10], ("10.80.0.1", "10.80.0.5")),)

# These lines must match the rules in acl.py (owned by Person B). They are kept
# as plain IOS text here on purpose; do not import acl.py.
ACLS = (
    ExtendedAcl("KIOSK_IN", VLAN[10], (
        "permit udp any eq 68 any eq 67",
        "permit tcp 10.80.0.0 0.0.0.31 host 10.80.0.74 eq 80",
        "permit tcp 10.80.0.0 0.0.0.31 host 10.80.0.74 eq 443",
        "permit tcp 10.80.0.0 0.0.0.31 10.80.0.64 0.0.0.7 established",
        "permit icmp 10.80.0.0 0.0.0.31 10.80.0.64 0.0.0.7 echo-reply",
        "deny ip any any",
    )),
    ExtendedAcl("TELLER_IN", VLAN[20], (
        "permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 80",
        "permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 443",
        "permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 21",
        "permit tcp 10.80.0.32 0.0.0.31 host 10.80.0.74 eq 20",
        "permit tcp 10.80.0.32 0.0.0.31 10.80.0.64 0.0.0.7 established",
        "permit icmp 10.80.0.32 0.0.0.31 10.80.0.64 0.0.0.7 echo-reply",
        "deny ip 10.80.0.32 0.0.0.31 10.80.0.0 0.0.0.31",
        "deny ip 10.80.0.32 0.0.0.31 10.80.0.64 0.0.0.7",
        "deny ip any any",
    )),
)


@dataclass(frozen=True)
class Router:
    hostname: str
    trunk_port: str                 # subinterfaces are <trunk_port>.<vlan id>
    trunk_description: str
    unused_ports: tuple[str, ...]
    ssh_timeout: int
    ssh_retries: int
    template: str = "r1.j2"


R1 = Router(
    hostname="R1",
    trunk_port="GigabitEthernet0/0",
    trunk_description="Trunk to SW1 G0/1",
    unused_ports=("GigabitEthernet0/1", "GigabitEthernet0/2"),
    ssh_timeout=60,
    ssh_retries=3,
)

DEVICES = {d.hostname: d for d in (R1, SW1, SW2)}
