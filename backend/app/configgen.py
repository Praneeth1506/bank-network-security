"""Render IOS configs for the BankNet devices from network.py + templates/."""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from . import network as net

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True,
    undefined=StrictUndefined,
)
_env.globals.update(
    common=net.COMMON, mgmt_acl=net.MGMT_ACL, port_security=net.PORT_SECURITY,
    vlans=net.VLANS, routed_vlans=net.ROUTED_VLANS, mgmt_vlan=net.MGMT_VLAN,
    trunk_native_vlan=net.TRUNK_NATIVE_VLAN, trunk_allowed_vlans=net.TRUNK_ALLOWED_VLANS,
    etherchannel=net.ETHERCHANNEL, dhcp_pools=net.DHCP_POOLS, acls=net.ACLS,
)


def list_devices() -> list[str]:
    return list(net.DEVICES)


def render(device: str) -> str:
    """Return the full config for a device (name is case-insensitive); KeyError if unknown."""
    d = net.DEVICES[device.upper()]
    return _env.get_template(d.template).render(d=d)
