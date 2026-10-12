import pytest

from app.main import DEFAULT_VLANS
from app.vlsm import vlsm

FIELDS = ["vlan", "network", "prefix", "mask", "wildcard",
          "first", "last", "broadcast", "gateway", "usable"]

# docs/network_spec.md section 1, in table order
EXPECTED = [
    (10, "10.80.0.0", 27, "255.255.255.224", "0.0.0.31",
     "10.80.0.1", "10.80.0.30", "10.80.0.31", "10.80.0.1", 30),
    (20, "10.80.0.32", 27, "255.255.255.224", "0.0.0.31",
     "10.80.0.33", "10.80.0.62", "10.80.0.63", "10.80.0.33", 30),
    (30, "10.80.0.64", 29, "255.255.255.248", "0.0.0.7",
     "10.80.0.65", "10.80.0.70", "10.80.0.71", "10.80.0.65", 6),
    (40, "10.80.0.72", 29, "255.255.255.248", "0.0.0.7",
     "10.80.0.73", "10.80.0.78", "10.80.0.79", "10.80.0.73", 6),
    (99, "10.80.0.80", 29, "255.255.255.248", "0.0.0.7",
     "10.80.0.81", "10.80.0.86", "10.80.0.87", "10.80.0.81", 6),
]


def test_default_plan_matches_spec():
    rows = vlsm("10.80.0.0/24", DEFAULT_VLANS, 1.0)
    assert [tuple(r[f] for f in FIELDS) for r in rows] == EXPECTED


def test_undersized_block_raises():
    with pytest.raises(ValueError):
        vlsm("10.80.0.0/26", DEFAULT_VLANS, 1.0)


def test_plan_endpoint_rejects_undersized_block(client):
    r = client.post("/api/plan", json={"block": "10.80.0.0/26"})
    assert r.status_code == 400


@pytest.mark.parametrize("vlan", [
    {"id": 10, "name": "KIOSK"},
    {"name": "KIOSK", "hosts": 10},
    {"id": 10, "hosts": 10},
    {"id": 10, "name": "KIOSK", "hosts": -1},
    {"id": 10, "name": "KIOSK", "hosts": "many"},
])
def test_plan_endpoint_rejects_bad_vlan(client, vlan):
    assert client.post("/api/plan", json={"vlans": [vlan]}).status_code == 422


def test_plan_endpoint_custom_vlans(client):
    r = client.post("/api/plan", json={"vlans": [{"id": 10, "name": "KIOSK", "hosts": 10}]})
    assert r.status_code == 200
    assert [row["network"] for row in r.json()] == ["10.80.0.0"]
