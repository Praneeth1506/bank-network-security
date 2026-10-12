
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.acl import ACLRule, evaluate_packet, get_policy_matrix

app = FastAPI(
    title="Bank Network Security API",
    description="ACL policy evaluation and network security dashboard API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Temporary empty policy.
# Replace this with the agreed KIOSK_IN and TELLER_IN rules
# after the network addressing plan is confirmed.
ACL_RULES: list[ACLRule] = []


@app.get("/")
def root():
    return {
        "message": "Bank Network Security API",
        "status": "online",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/policy")
def policy():
    return {
        "count": len(ACL_RULES),
        "rules": get_policy_matrix(ACL_RULES),
    }


@app.get("/api/config/{device}")
def device_config(device: str):
    # Person A will need to integrate their configuration generator here.
    return {
        "device": device.upper(),
        "available": False,
        "message": "Device configuration generator is not connected yet.",
    }
