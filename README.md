# BankNet Lab Assistant (optional companion for CN Lab Problem 8)

An optional web companion to the Cisco Packet Tracer lab: it plans VLSM addressing, predicts ACL decisions, generates the R1/SW1/SW2 configs and tracks test results.
It is **not** part of the graded Packet Tracer deliverable.

- Network spec (single source of truth): [docs/network_spec.md](docs/network_spec.md)
- API reference for the frontend: [docs/api.md](docs/api.md)

## Backend (Python 3.11+)

    cd backend
    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000
    # API docs: http://localhost:8000/docs

Data is stored in `backend/banknet.db` (SQLite, created on first start). Set
`BANKNET_DB_URL` to use a different database, e.g. `BANKNET_DB_URL=sqlite:///other.db`.

Load the 18 default tests from the spec (safe to run more than once):

    python -m app.seed

## Frontend (Node 18+)

    cd frontend
    npm install
    npm run dev        # http://localhost:5173

The backend only accepts browser requests from `http://localhost:5173`, so open
the app at that address (not `127.0.0.1`).

## Tests

    cd backend
    pip install -r requirements-dev.txt
    pytest

The tests use a temporary database and never touch `banknet.db`. They check the
VLSM plan and generated configs against `docs/network_spec.md`.

## Export device configs

    cd backend
    python -m app.export_configs           # writes configs/R1.txt, configs/SW1.txt, configs/SW2.txt
    python -m app.export_configs some/dir  # or to another folder

`backend/configs/` is generated output and is git-ignored.

## Who owns what

- **Person A** owns `backend/`, except `acl.py`: VLSM, the API (`main.py`), the
  config generator (`network.py`, `configgen.py`, `templates/`) and seed data.
- **Person B** owns `backend/app/acl.py` and `frontend/`.
- **Keep the ACLs in sync:** the rules in `acl.py` and the `KIOSK_IN` / `TELLER_IN`
  lines in `network.py` (`ACLS`) describe the same R1 ACLs. Change one, change the
  other, and tell the other person.
