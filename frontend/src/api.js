const BASE = "http://localhost:8000/api";

async function call(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.headers.get("content-type")?.includes("json") ? res.json() : res.text();
}

export const getPlan = (body = {}) => call("/plan", { method: "POST", body: JSON.stringify(body) });
export const checkFlow = (flow) => call("/acl/check", { method: "POST", body: JSON.stringify(flow) });
export const listTests = () => call("/tests");
export const addTest = (t) => call("/tests", { method: "POST", body: JSON.stringify(t) });
export const recordResult = (id, observed, screenshot) =>
  call(`/tests/${id}?observed=${encodeURIComponent(observed)}&screenshot=${encodeURIComponent(screenshot)}`, { method: "PATCH" });
