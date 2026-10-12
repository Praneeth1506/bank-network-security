# BankNet Lab Assistant (optional companion for CN Lab Problem 8)

Not part of the graded Packet Tracer deliverable. Helps plan VLSM, predict ACL decisions and record test results.

## Backend (Python 3.11+)
    cd backend
    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000
    # API docs: http://localhost:8000/docs

## Frontend (Node 18+)
    cd frontend
    npm install
    npm run dev        # http://localhost:5173
