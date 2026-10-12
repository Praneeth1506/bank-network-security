import { useEffect, useState } from "react";
import { getPlan } from "../api.js";

export default function Plan() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => { getPlan().then(setRows).catch((e) => setError(e.message)); }, []);
  const cols = ["vlan", "name", "network", "prefix", "mask", "wildcard", "first", "last", "broadcast", "gateway", "usable"];
  return (
    <section>
      <h2>VLSM plan for 10.80.0.0/24</h2>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      <table border="1" cellPadding="6" style={{ borderCollapse: "collapse" }}>
        <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>{rows.map((r) => <tr key={r.vlan}>{cols.map((c) => <td key={c}>{r[c]}</td>)}</tr>)}</tbody>
      </table>
    </section>
  );
}
