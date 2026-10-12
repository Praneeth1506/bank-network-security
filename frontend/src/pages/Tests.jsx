import { useEffect, useState } from "react";
import { addTest, listTests, recordResult } from "../api.js";

const EMPTY = { source: "", destination: "", test: "", expected: "Allowed" };

export default function Tests() {
  const [tests, setTests] = useState([]);
  const [draft, setDraft] = useState(EMPTY);
  const load = () => listTests().then(setTests);
  useEffect(() => { load(); }, []);

  async function save() { await addTest(draft); setDraft(EMPTY); load(); }
  async function mark(t, observed) {
    const shot = prompt("Screenshot file name (optional)", t.screenshot || "") ?? "";
    await recordResult(t.id, observed, shot); load();
  }

  return (
    <section>
      <h2>Allowed / blocked test tracker</h2>
      <p>
        {["source", "destination", "test"].map((k) => (
          <input key={k} placeholder={k} value={draft[k]} onChange={(e) => setDraft({ ...draft, [k]: e.target.value })} style={{ marginRight: 8 }} />
        ))}
        <select value={draft.expected} onChange={(e) => setDraft({ ...draft, expected: e.target.value })}>
          <option>Allowed</option><option>Blocked</option>
        </select>{" "}
        <button onClick={save}>Add test</button>{" "}
        <a href="http://localhost:8000/api/tests/export.csv">Export CSV</a>
      </p>
      <table border="1" cellPadding="6" style={{ borderCollapse: "collapse" }}>
        <thead><tr><th>#</th><th>From</th><th>To</th><th>Test</th><th>Expected</th><th>Observed</th><th>Screenshot</th><th>Record</th></tr></thead>
        <tbody>{tests.map((t) => (
          <tr key={t.id} style={{ background: t.observed && t.observed !== t.expected ? "#fde2e2" : undefined }}>
            <td>{t.id}</td><td>{t.source}</td><td>{t.destination}</td><td>{t.test}</td><td>{t.expected}</td>
            <td>{t.observed}</td><td>{t.screenshot}</td>
            <td><button onClick={() => mark(t, "Allowed")}>Allowed</button> <button onClick={() => mark(t, "Blocked")}>Blocked</button></td>
          </tr>
        ))}</tbody>
      </table>
    </section>
  );
}
