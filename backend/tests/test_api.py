import csv
import io

import pytest

ROW = {"source": "KIOSK1", "destination": "SRV1",
       "test": "ping 10.80.0.74", "expected": "Blocked"}


def test_create_test(client):
    r = client.post("/api/tests", json=ROW)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == 1
    assert body | ROW == body
    assert body["observed"] == "" and body["screenshot"] == ""
    assert client.get("/api/tests").json() == [body]


def test_patch_test(client):
    tid = client.post("/api/tests", json=ROW).json()["id"]
    r = client.patch(f"/api/tests/{tid}",
                     params={"observed": "Blocked", "screenshot": "t4.png"})
    assert r.status_code == 200
    assert r.json()["observed"] == "Blocked"
    assert r.json()["screenshot"] == "t4.png"
    assert client.get("/api/tests").json()[0]["observed"] == "Blocked"


def test_patch_missing_test_returns_404(client):
    r = client.patch("/api/tests/999", params={"observed": "Allowed"})
    assert r.status_code == 404


def test_export_csv(client):
    client.post("/api/tests", json=ROW)
    client.post("/api/tests", json={**ROW, "test": "ftp 10.80.0.74"})
    client.patch("/api/tests/1", params={"observed": "Blocked"})

    r = client.get("/api/tests/export.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    rows = list(csv.reader(io.StringIO(r.text)))
    assert rows == [
        ["id", "source", "destination", "test", "expected", "observed", "screenshot"],
        ["1", "KIOSK1", "SRV1", "ping 10.80.0.74", "Blocked", "Blocked", ""],
        ["2", "KIOSK1", "SRV1", "ftp 10.80.0.74", "Blocked", "", ""],
    ]


@pytest.mark.parametrize("body", [
    {"source": "KIOSK1"},
    {k: v for k, v in ROW.items() if k != "expected"},
    {**ROW, "expected": "Maybe"},
])
def test_create_test_rejects_bad_body(client, body):
    assert client.post("/api/tests", json=body).status_code == 422
    assert client.get("/api/tests").json() == []


def test_patch_without_screenshot_keeps_it(client):
    tid = client.post("/api/tests", json=ROW).json()["id"]
    client.patch(f"/api/tests/{tid}", params={"observed": "Allowed", "screenshot": "t4.png"})
    r = client.patch(f"/api/tests/{tid}", params={"observed": "Blocked"})
    assert r.json()["observed"] == "Blocked"
    assert r.json()["screenshot"] == "t4.png"


def test_patch_empty_screenshot_clears_it(client):
    tid = client.post("/api/tests", json=ROW).json()["id"]
    client.patch(f"/api/tests/{tid}", params={"observed": "Blocked", "screenshot": "t4.png"})
    r = client.patch(f"/api/tests/{tid}", params={"observed": "Blocked", "screenshot": ""})
    assert r.json()["screenshot"] == ""


def test_export_csv_download_header(client):
    r = client.get("/api/tests/export.csv")
    assert r.headers["content-disposition"] == 'attachment; filename="banknet_tests.csv"'


FLOW = {"src": "10.80.0.5", "dst": "10.80.0.74", "proto": "tcp", "port": 80}


def test_acl_check_valid_flow(client):
    r = client.post("/api/acl/check", json=FLOW)
    assert r.status_code == 200
    assert r.json() == {"verdict": "permit", "acl": "KIOSK_IN", "interface": "G0/0.10", "line": 2}


@pytest.mark.parametrize("change", [
    {"src": "kiosk"},
    {"dst": "10.80.0.256"},
    {"src": "::1"},
    {"proto": "ftp"},
    {"port": 70000},
    {"port": -1},
    {"dst": None},
])
def test_acl_check_rejects_bad_flow(client, change):
    assert client.post("/api/acl/check", json={**FLOW, **change}).status_code == 422
