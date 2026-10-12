import re
from pathlib import Path

import pytest

from app.configgen import list_devices, render

SPEC = Path(__file__).resolve().parents[2] / "docs" / "network_spec.md"


def reference_configs() -> dict[str, str]:
    """Map device name -> fenced config block under section 3 of the spec."""
    section = SPEC.read_text().split("\n## 3.")[1].split("\n## ")[0]
    return dict(re.findall(r"^### (\S+)\n```\n(.*?)^```", section, re.S | re.M))


REFERENCE = reference_configs()


def lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines()]


def test_spec_and_generator_cover_same_devices():
    assert sorted(REFERENCE) == list_devices() == ["R1", "SW1", "SW2"]


@pytest.mark.parametrize("device", ["R1", "SW1", "SW2"])
def test_render_matches_spec(device):
    assert lines(render(device)) == lines(REFERENCE[device])


def test_render_unknown_device():
    with pytest.raises(KeyError):
        render("R9")


def test_list_route(client):
    r = client.get("/api/config")
    assert r.status_code == 200
    assert r.json() == {"devices": ["R1", "SW1", "SW2"]}


@pytest.mark.parametrize("name", ["R1", "r1", "Sw2"])
def test_json_route_is_case_insensitive(client, name):
    r = client.get(f"/api/config/{name}")
    assert r.status_code == 200
    assert r.json() == {"device": name.upper(), "config": render(name)}


@pytest.mark.parametrize("name", ["SW1", "sw1"])
def test_txt_route(client, name):
    r = client.get(f"/api/config/{name}.txt")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert r.headers["content-disposition"] == 'attachment; filename="SW1.txt"'
    assert r.text == render("SW1")


@pytest.mark.parametrize("path", ["/api/config/R9", "/api/config/R9.txt"])
def test_unknown_device_returns_404(client, path):
    assert client.get(path).status_code == 404
