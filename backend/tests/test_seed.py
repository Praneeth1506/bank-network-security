import csv
import io
from pathlib import Path

from sqlmodel import Session

from app.main import engine
from app.seed import seed
from app.test_cases import TEST_CASES

SPEC = Path(__file__).resolve().parents[2] / "docs" / "network_spec.md"
KEYS = ["source", "destination", "test", "expected"]


def spec_rows() -> list[dict]:
    """Rows of the section 4 table, in order, keyed like TEST_CASES."""
    section = SPEC.read_text().split("\n## 4.")[1].split("\n## ")[0]
    rows = []
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0].isdigit():
            assert int(cells[0]) == len(rows) + 1
            rows.append(dict(zip(KEYS, cells[1:])))
    return rows


def test_test_cases_match_spec():
    assert len(TEST_CASES) == 18
    assert TEST_CASES == spec_rows()
    assert {c["expected"] for c in TEST_CASES} == {"Allowed", "Blocked"}


def test_seed_is_idempotent(client):
    with Session(engine) as s:
        assert seed(s) == 18
        assert seed(s) == 0


def test_seed_route(client):
    assert client.post("/api/tests/seed").json() == {"inserted": 18, "total": 18}
    assert client.post("/api/tests/seed").json() == {"inserted": 0, "total": 18}


def test_seeded_rows_have_no_observation(client):
    client.post("/api/tests/seed")
    rows = client.get("/api/tests").json()
    assert len(rows) == 18
    assert all(r["observed"] == "" for r in rows)
    assert [{k: r[k] for k in KEYS} for r in rows] == TEST_CASES


def test_csv_quotes_destination_with_commas(client):
    client.post("/api/tests/seed")
    text = client.get("/api/tests/export.csv").text
    row14 = text.splitlines()[14]       # line 0 is the header
    assert row14 == '14,MGR1,"KIOSK1, TELLER1, SRV1",ping,Allowed,,'
    assert list(csv.reader(io.StringIO(text)))[14][2] == "KIOSK1, TELLER1, SRV1"
