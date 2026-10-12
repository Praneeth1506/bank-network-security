
from backend.acl import ACLRule, evaluate_packet


def test_matching_permit_rule():
    rules = [
        ACLRule(
            name="ALLOW_WEB",
            action="permit",
            protocol="tcp",
            source="192.0.2.0/24",
            destination="198.51.100.10/32",
            destination_port=443,
            description="Allow HTTPS",
        )
    ]

    result = evaluate_packet(
        rules,
        source_ip="192.0.2.25",
        destination_ip="198.51.100.10",
        protocol="tcp",
        destination_port=443,
    )

    assert result["action"] == "permit"
    assert result["matched_rule"] == "ALLOW_WEB"


def test_non_matching_packet_is_denied():
    rules = [
        ACLRule(
            name="ALLOW_WEB",
            action="permit",
            protocol="tcp",
            source="192.0.2.0/24",
            destination="198.51.100.10/32",
            destination_port=443,
        )
    ]

    result = evaluate_packet(
        rules,
        source_ip="192.0.2.25",
        destination_ip="198.51.100.10",
        protocol="tcp",
        destination_port=80,
    )

    assert result["action"] == "deny"
    assert result["matched_rule"] is None


def test_implicit_deny_when_no_rules_exist():
    result = evaluate_packet(
        [],
        source_ip="192.0.2.25",
        destination_ip="198.51.100.10",
        protocol="icmp",
    )

    assert result["action"] == "deny"
    assert result["reason"] == "Implicit deny: no rule matched"
