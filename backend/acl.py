
from dataclasses import dataclass
from ipaddress import ip_address, ip_network
from typing import Literal


Action = Literal["permit", "deny"]


@dataclass(frozen=True)
class ACLRule:
    """Represents one extended ACL rule."""

    name: str
    action: Action
    protocol: str
    source: str
    destination: str
    destination_port: int | None = None
    description: str = ""


def matches_network(ip: str, network: str) -> bool:
    """Return True if an IP address belongs to a network."""
    return ip_address(ip) in ip_network(network, strict=False)


def evaluate_packet(
    rules: list[ACLRule],
    source_ip: str,
    destination_ip: str,
    protocol: str,
    destination_port: int | None = None,
) -> dict:
    """
    Evaluate a packet against rules in order.

    The first matching rule decides the outcome.
    If no rule matches, the result is denied by default.
    """
    for rule in rules:
        if rule.protocol.lower() not in ("ip", protocol.lower()):
            continue

        if not matches_network(source_ip, rule.source):
            continue

        if not matches_network(destination_ip, rule.destination):
            continue

        if rule.destination_port is not None:
            if destination_port != rule.destination_port:
                continue

        return {
            "action": rule.action,
            "matched_rule": rule.name,
            "reason": rule.description or f"Matched rule {rule.name}",
        }

    return {
        "action": "deny",
        "matched_rule": None,
        "reason": "Implicit deny: no rule matched",
    }


def get_policy_matrix(rules: list[ACLRule]) -> list[dict]:
    """Return ACL rules in a format suitable for the frontend."""
    return [
        {
            "name": rule.name,
            "action": rule.action,
            "protocol": rule.protocol,
            "source": rule.source,
            "destination": rule.destination,
            "destination_port": rule.destination_port,
            "description": rule.description,
        }
        for rule in rules
    ]
