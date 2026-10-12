import csv
import io
import os
from contextlib import asynccontextmanager
from ipaddress import IPv4Address
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, StringConstraints
from sqlmodel import Session, SQLModel, create_engine, func, select

from .acl import check
from .configgen import list_devices, render
from .models import TestResult
from .seed import seed
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


class VlanIn(BaseModel):
    id: int
    name: str
    hosts: int = Field(ge=0)


class PlanIn(BaseModel):
    block: str = "10.80.0.0/24"
    growth: float = 1.0
    vlans: list[VlanIn] = [VlanIn(**v) for v in DEFAULT_VLANS]


class FlowIn(BaseModel):
    src: IPv4Address
    dst: IPv4Address
    proto: Literal["tcp", "udp", "icmp", "icmp-reply"]
    port: int | None = Field(default=None, ge=0, le=65535)
    established: bool = False


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TestCreate(BaseModel):
    source: NonEmptyStr
    destination: NonEmptyStr
    test: NonEmptyStr
    expected: Literal["Allowed", "Blocked"]


@app.post("/api/plan")
def plan(body: PlanIn):
    try:
        return vlsm(body.block, [v.model_dump() for v in body.vlans], body.growth)
    except ValueError as e:
        raise HTTPException(400, str(e))


def _config(device: str) -> tuple[str, str]:
    try:
        return device.upper(), render(device)
    except KeyError:
        raise HTTPException(404, f"unknown device {device}")


@app.get("/api/config")
def config_devices():
    return {"devices": list_devices()}


# Declared before /api/config/{device}, which would otherwise match "R1.txt".
@app.get("/api/config/{device}.txt", response_class=PlainTextResponse)
def config_download(device: str):
    name, text = _config(device)
    return PlainTextResponse(
        text, headers={"Content-Disposition": f'attachment; filename="{name}.txt"'})


@app.get("/api/config/{device}")
def config_json(device: str):
    name, text = _config(device)
    return {"device": name, "config": text}


@app.post("/api/acl/check")
def acl_check(flow: FlowIn):
    return check(str(flow.src), str(flow.dst), flow.proto, flow.port, flow.established)


@app.get("/api/tests")
def list_tests():
    with Session(engine) as s:
        return s.exec(select(TestResult)).all()


@app.post("/api/tests")
def add_test(body: TestCreate):
    t = TestResult(**body.model_dump())
    with Session(engine) as s:
        s.add(t)
        s.commit()
        s.refresh(t)
        return t


@app.post("/api/tests/seed")
def seed_tests():
    with Session(engine) as s:
        inserted = seed(s)
        total = s.exec(select(func.count()).select_from(TestResult)).one()
        return {"inserted": inserted, "total": total}


@app.patch("/api/tests/{test_id}")
def update_test(test_id: int, observed: str, screenshot: str | None = None):
    with Session(engine) as s:
        t = s.get(TestResult, test_id)
        if not t:
            raise HTTPException(404, "test not found")
        t.observed = observed
        if screenshot is not None:      # omitted keeps the stored value; "" clears it
            t.screenshot = screenshot
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
    return PlainTextResponse(
        buf.getvalue(),
        headers={"Content-Disposition": 'attachment; filename="banknet_tests.csv"'})
