import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import Plan from "./pages/Plan.jsx";
import PolicyChecker from "./pages/PolicyChecker.jsx";
import Tests from "./pages/Tests.jsx";

function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: 16, padding: 16, borderBottom: "1px solid #ccc" }}>
        <NavLink to="/">VLSM plan</NavLink>
        <NavLink to="/policy">Policy checker</NavLink>
        <NavLink to="/tests">Test tracker</NavLink>
      </nav>
      <main style={{ padding: 16, fontFamily: "system-ui, sans-serif" }}>
        <Routes>
          <Route path="/" element={<Plan />} />
          <Route path="/policy" element={<PolicyChecker />} />
          <Route path="/tests" element={<Tests />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
