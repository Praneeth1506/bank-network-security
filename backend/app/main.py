import csv
import io
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

from .acl import check
from .vlsm import vlsm

engine = create_engine(os.environ.get("BANKNET_DB_URL", "sqlite:///banknet.db"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="BankNet Lab Assistant", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])

DEFAULT_VLANS = [
    {"id": 10, "name": "KIOSK", "hosts": 10},
    {"id": 20, "name": "TELLER", "hosts": 8},
    {"id": 30, "name": "MANAGER", "hosts": 2},
    {"id": 40, "name": "SERVER", "hosts": 1},
    {"id": 99, "name": "MGMT", "hosts": 2},
]


class PlanIn(BaseModel):
    block: str = "10.80.0.0/24"
    growth: float = 1.0
    vlans: list[dict] = DEFAULT_VLANS


class FlowIn(BaseModel):
    src: str
    dst: str
    proto: str          # tcp | udp | icmp | icmp-reply
    port: int | None = None
    established: bool = False


class TestResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source: str
    destination: str
    test: str
    expected: str
    observed: str = ""
    screenshot: str = ""


@app.post("/api/plan")
def plan(body: PlanIn):
    try:
        return vlsm(body.block, body.vlans, body.growth)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/acl/check")
def acl_check(flow: FlowIn):
    return check(flow.src, flow.dst, flow.proto, flow.port, flow.established)


@app.get("/api/tests")
def list_tests():
    with Session(engine) as s:
        return s.exec(select(TestResult)).all()


@app.post("/api/tests")
def add_test(t: TestResult):
    with Session(engine) as s:
        s.add(t)
        s.commit()
        s.refresh(t)
        return t


@app.patch("/api/tests/{test_id}")
def update_test(test_id: int, observed: str, screenshot: str = ""):
    with Session(engine) as s:
        t = s.get(TestResult, test_id)
        if not t:
            raise HTTPException(404, "test not found")
        t.observed, t.screenshot = observed, screenshot
        s.add(t)
        s.commit()
        s.refresh(t)
        return t


@app.get("/api/tests/export.csv", response_class=PlainTextResponse)
def export_tests():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "source", "destination", "test", "expected", "observed", "screenshot"])
    for t in list_tests():
        w.writerow([t.id, t.source, t.destination, t.test, t.expected, t.observed, t.screenshot])
    return buf.getvalue()
