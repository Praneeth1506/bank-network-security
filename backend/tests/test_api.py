import csv
import io

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
