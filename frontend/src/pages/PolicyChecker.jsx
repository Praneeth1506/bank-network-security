import { useState } from "react";
import { checkFlow } from "../api.js";

const PRESETS = {
  "Kiosk -> web": { src: "10.80.0.6", dst: "10.80.0.74", proto: "tcp", port: 80 },
  "Kiosk -> ping teller": { src: "10.80.0.6", dst: "10.80.0.34", proto: "icmp", port: null },
  "Teller -> FTP": { src: "10.80.0.34", dst: "10.80.0.74", proto: "tcp", port: 21 },
  "Teller -> SSH R1": { src: "10.80.0.34", dst: "10.80.0.33", proto: "tcp", port: 22 },
};

export default function PolicyChecker() {
  const [flow, setFlow] = useState({ src: "10.80.0.6", dst: "10.80.0.74", proto: "tcp", port: 80, established: false });
  const [result, setResult] = useState(null);
  const set = (k) => (e) => setFlow({ ...flow, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  async function run() {
    const port = flow.port === "" || flow.port === null ? null : Number(flow.port);
    setResult(await checkFlow({ ...flow, port }));
  }

  return (
    <section>
      <h2>Predict whether R1's ACLs allow a flow</h2>
      <p>{Object.keys(PRESETS).map((k) => (
        <button key={k} onClick={() => setFlow({ ...flow, ...PRESETS[k] })} style={{ marginRight: 8 }}>{k}</button>
      ))}</p>
      <label>Source IP <input value={flow.src} onChange={set("src")} /></label>{" "}
      <label>Destination IP <input value={flow.dst} onChange={set("dst")} /></label>{" "}
      <label>Protocol <select value={flow.proto} onChange={set("proto")}>
        <option>tcp</option><option>udp</option><option>icmp</option><option>icmp-reply</option>
      </select></label>{" "}
      <label>Port <input value={flow.port ?? ""} onChange={set("port")} size={5} /></label>{" "}
      <label><input type="checkbox" checked={flow.established} onChange={set("established")} /> reply (established)</label>{" "}
      <button onClick={run}>Check</button>
      {result && (
        <p style={{ fontWeight: 600, color: result.verdict === "permit" ? "green" : "crimson" }}>
          {result.verdict.toUpperCase()} {result.acl ? `by ${result.acl} line ${result.line} on ${result.interface}` : `(${result.note})`}
        </p>
      )}
    </section>
  );
}
