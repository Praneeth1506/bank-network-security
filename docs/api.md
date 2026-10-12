# BankNet Lab Assistant API

Reference for building the frontend against the backend in `backend/app/main.py`.
Every example response below was captured from the running app with FastAPI's
TestClient against a fresh database; long responses are shortened where marked.

- Base URL: `http://localhost:8000` (all routes are under `/api`)
- Interactive docs: `http://localhost:8000/docs`
- **CORS allows only `http://localhost:5173`** (the Vite dev server). A page served
  from any other origin, including `http://127.0.0.1:5173`, gets
  `400 Disallowed CORS origin` on preflight.
- Errors raised by the app come back as JSON `{"detail": "<message>"}`.
  Validation errors (422) use FastAPI's format: `{"detail": [{"type", "loc", "msg", "input"}, ...]}`.

| Method | Path | Purpose |
|--------|------|---------|
| POST | [/api/plan](#post-apiplan) | VLSM addressing plan |
| POST | [/api/acl/check](#post-apiaclcheck) | Predict R1's ACL verdict for a flow |
| GET | [/api/tests](#get-apitests) | List test results |
| POST | [/api/tests](#post-apitests) | Add a test row |
| PATCH | [/api/tests/{id}](#patch-apitestsid) | Record what was observed |
| POST | [/api/tests/seed](#post-apitestsseed) | Load the 18 default tests |
| GET | [/api/tests/export.csv](#get-apitestsexportcsv) | Export results as CSV |
| GET | [/api/config](#get-apiconfig) | List devices with generated configs |
| GET | [/api/config/{device}](#get-apiconfigdevice) | Device config as JSON |
| GET | [/api/config/{device}.txt](#get-apiconfigdevicetxt) | Device config as a download |

---

## POST /api/plan

Allocates subnets largest-first from `block`, sizing each VLAN for
`hosts × (1 + growth)` plus a gateway.

**Body** (JSON, every field optional; send `{}` for the lab's plan)

| Field | Type | Default |
|-------|------|---------|
| `block` | string, CIDR | `"10.80.0.0/24"` |
| `growth` | number | `1.0` (100% growth) |
| `vlans` | array of `{"id": int, "name": str, "hosts": int ≥ 0}`, all three fields required | the five lab VLANs (10 KIOSK, 20 TELLER, 30 MANAGER, 40 SERVER, 99 MGMT) |

**200**: an array with one row per VLAN, largest block first. Request `{}`;
the first of 5 rows is shown:

```json
[
  {
    "vlan": 10,
    "name": "KIOSK",
    "hosts_now": 10,
    "network": "10.80.0.0",
    "prefix": 27,
    "mask": "255.255.255.224",
    "wildcard": "0.0.0.31",
    "first": "10.80.0.1",
    "last": "10.80.0.30",
    "broadcast": "10.80.0.31",
    "gateway": "10.80.0.1",
    "usable": 30
  }
]
```

**Errors**

| Code | When | Example |
|------|------|---------|
| 400 | Block too small | `{"block": "10.80.0.0/26"}` → `{"detail": "10.80.0.0/26 is too small for VLAN 30"}` |
| 400 | Block isn't a network | `{"block": "nonsense"}` → `{"detail": "'nonsense' does not appear to be an IPv4 or IPv6 network"}` |
| 422 | A VLAN is missing `id`, `name` or `hosts`, `hosts` is negative or not an integer, or `growth` is not a number | see below |

422 example, request `{"vlans": [{"id": 10, "name": "KIOSK"}]}`:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "vlans", 0, "hosts"],
      "msg": "Field required",
      "input": {"id": 10, "name": "KIOSK"}
    }
  ]
}
```

---

## POST /api/acl/check

Predicts whether R1's inbound ACLs (`KIOSK_IN`, `TELLER_IN`) would permit a
packet. Matching is first-match, as on IOS. Logic lives in `acl.py`.

**Body** (JSON)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `src` | string, dotted IPv4 address | yes | Source host. `0.0.0.0` is treated as a DHCP Discover on the kiosk VLAN |
| `dst` | string, dotted IPv4 address | yes | Destination host |
| `proto` | string | yes | Exactly `tcp`, `udp`, `icmp` or `icmp-reply` |
| `port` | int 0–65535 or null | no, default `null` | Destination port for tcp/udp |
| `established` | bool | no, default `false` | Set for TCP return traffic |

**200**, request `{"src": "10.80.0.5", "dst": "10.80.0.74", "proto": "tcp", "port": 80}`:

```json
{
  "verdict": "permit",
  "acl": "KIOSK_IN",
  "interface": "G0/0.10",
  "line": 2
}
```

`verdict` is `"permit"` or `"deny"`; `line` is the 1-based rule number in that
ACL (matches the R1 config order). A denied flow, request
`{"src": "10.80.0.34", "dst": "10.80.0.66", "proto": "icmp"}`:

```json
{
  "verdict": "deny",
  "acl": "TELLER_IN",
  "interface": "G0/0.20",
  "line": 8
}
```

When the source VLAN has no ACL (manager or server), the other fields are `null`
and a `note` is added. Request `{"src": "10.80.0.66", "dst": "10.80.0.34", "proto": "icmp"}`:

```json
{
  "verdict": "permit",
  "acl": null,
  "interface": null,
  "line": null,
  "note": "No ACL on the source VLAN (manager or server)"
}
```

**Errors**

| Code | When |
|------|------|
| 422 | `src`, `dst` or `proto` missing; `src`/`dst` not an IPv4 address (e.g. `"kiosk"`, `"10.80.0.256"`, `"::1"`); `proto` not one of the four values; `port` outside 0–65535 |

422 example, request `{"src": "kiosk", "dst": "10.80.0.74", "proto": "tcp", "port": 80}`:

```json
{
  "detail": [
    {
      "type": "ip_v4_address",
      "loc": ["body", "src"],
      "msg": "Input is not a valid IPv4 address",
      "input": "kiosk"
    }
  ]
}
```

---

## GET /api/tests

Lists every test row in insertion order. No parameters.

**200**: an array (empty `[]` on a fresh database). After seeding, the first
of 18 rows:

```json
[
  {
    "source": "KIOSK1",
    "destination": "R1",
    "expected": "Allowed",
    "screenshot": "",
    "test": "ipconfig (DHCP lease)",
    "id": 1,
    "observed": ""
  }
]
```

`expected` is `"Allowed"` or `"Blocked"` for seeded rows. `observed` and
`screenshot` are `""` until recorded with PATCH. Key order is not stable;
read fields by name.

**Errors**: none.

---

## POST /api/tests

Adds one test row.

**Body** (JSON)

| Field | Type | Required |
|-------|------|----------|
| `source` | string, non-empty | yes |
| `destination` | string, non-empty | yes |
| `test` | string, non-empty | yes |
| `expected` | `"Allowed"` or `"Blocked"` (exact case) | yes |

`source`, `destination` and `test` are stored with leading and trailing
whitespace removed, so `" KIOSK1 "` is saved as `"KIOSK1"`; a value that is empty
or only whitespace is rejected. Any other fields (including `id`, `observed`, `screenshot`) are ignored; new
rows always start with `observed` and `screenshot` set to `""`.

**200**: the stored row with its new `id`. Request
`{"source": "KIOSK1", "destination": "SRV1", "test": "ping 10.80.0.74", "expected": "Blocked"}`:

```json
{
  "test": "ping 10.80.0.74",
  "id": 1,
  "observed": "",
  "destination": "SRV1",
  "expected": "Blocked",
  "source": "KIOSK1",
  "screenshot": ""
}
```

**Errors**

| Code | When |
|------|------|
| 422 | A required field is missing; `source`, `destination` or `test` is empty or only whitespace; or `expected` is not `"Allowed"` / `"Blocked"` |

422 example, request with `"source": "   "`:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "source"],
      "msg": "String should have at least 1 character",
      "input": "   ",
      "ctx": {"min_length": 1}
    }
  ]
}
```

With `"expected": "Maybe"` the error is `"type": "literal_error"`, `"loc": ["body", "expected"]`,
`"msg": "Input should be 'Allowed' or 'Blocked'"`.

---

## PATCH /api/tests/{id}

Records the observed result. **Parameters go in the query string, not a JSON body.**

| Param | In | Type | Required |
|-------|----|------|----------|
| `id` | path | int | yes |
| `observed` | query | string | yes (e.g. `Allowed` / `Blocked`) |
| `screenshot` | query | string | no. Omit it to keep the stored value; send `screenshot=` (empty) to clear it |

**200**: the updated row. Request `PATCH /api/tests/1?observed=Blocked&screenshot=t4.png`:

```json
{
  "test": "ping 10.80.0.74",
  "id": 1,
  "observed": "Blocked",
  "destination": "SRV1",
  "expected": "Blocked",
  "source": "KIOSK1",
  "screenshot": "t4.png"
}
```

Then `PATCH /api/tests/1?observed=Allowed` (no `screenshot`) keeps it:

```json
{
  "test": "ping 10.80.0.74",
  "id": 1,
  "observed": "Allowed",
  "destination": "SRV1",
  "expected": "Blocked",
  "source": "KIOSK1",
  "screenshot": "t4.png"
}
```

**Errors**

| Code | When | Body |
|------|------|------|
| 404 | No row with that id | `{"detail": "test not found"}` |
| 422 | `observed` missing, or `id` not an integer | FastAPI validation error, e.g. `loc: ["query", "observed"]`, `msg: "Field required"` |

---

## POST /api/tests/seed

Loads the 18-row test table from `docs/network_spec.md` section 4 (backs the
"Load default tests" button). Inserts only rows whose `(source, destination, test)`
isn't already present, so it is safe to call repeatedly. No body.

**200**, first call on an empty database:

```json
{"inserted": 18, "total": 18}
```

Second call:

```json
{"inserted": 0, "total": 18}
```

`total` counts every row in the table, including ones added by hand.

**Errors**: none.

---

## GET /api/tests/export.csv

All rows as CSV with a header row. Fields containing commas are quoted.

**200**

```
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="banknet_tests.csv"
```

A plain `<a href="http://localhost:8000/api/tests/export.csv">` link downloads it
as `banknet_tests.csv`. Excerpt after seeding and patching row 1:

```
id,source,destination,test,expected,observed,screenshot
1,KIOSK1,R1,ipconfig (DHCP lease),Allowed,Allowed,t1.png
2,KIOSK1,SRV1,Browser http://10.80.0.74,Allowed,,
9,TELLER1,SRV1,"ftp 10.80.0.74, login teller, put/get",Allowed,,
14,MGR1,"KIOSK1, TELLER1, SRV1",ping,Allowed,,
16,MGR1,"R1, SW1, SW2",ssh -l admin 10.80.0.65 / .82 / .83,Allowed,,
```

**Errors**: none.

Note: `src/api.js` treats any non-JSON response as text, so `call("/tests/export.csv")`
already returns the CSV as a string.

---

## GET /api/config

Devices that have a generated IOS config. No parameters.

**200**

```json
{"devices": ["R1", "SW1", "SW2"]}
```

**Errors**: none.

---

## GET /api/config/{device}

Full generated config for one device. `device` is case-insensitive (`r1`, `R1`
and `Sw2` all work); the response always uses the canonical upper-case name.
The config matches section 3 of the spec line for line.

**200**: request `GET /api/config/r1` (config string shortened; the full text
ends with `\n`):

```json
{
  "device": "R1",
  "config": "enable\nconfigure terminal\nhostname R1\nno ip domain-lookup\n...\nend\ncopy running-config startup-config\n"
}
```

Render it in a `<pre>` so the leading spaces on sub-commands are kept.

**Errors**

| Code | When | Body |
|------|------|------|
| 404 | Unknown device | `{"detail": "unknown device R9"}` |

---

## GET /api/config/{device}.txt

Same config as a plain-text download. Case-insensitive, like the JSON route.

**200**: request `GET /api/config/R1.txt`

```
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="R1.txt"

enable
configure terminal
hostname R1
...
```

A plain `<a href="http://localhost:8000/api/config/R1.txt">` link downloads it.

**Errors**

| Code | When | Body |
|------|------|------|
| 404 | Unknown device | `{"detail": "unknown device R9"}` (JSON, even on the `.txt` route) |
