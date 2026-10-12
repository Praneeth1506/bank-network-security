
import { useState } from "react";
import "./App.css";

const navigation = [
  { id: "dashboard", label: "Dashboard", icon: "◫" },
  { id: "policy", label: "ACL Policy", icon: "⬡" },
  { id: "tests", label: "Security Tests", icon: "✓" },
  { id: "configs", label: "Device Configs", icon: "⌘" },
];

function Dashboard() {
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">NETWORK OPERATIONS / OVERVIEW</p>
          <h1>Security Dashboard</h1>
          <p className="muted">Monitor access control and network security.</p>
        </div>
        <div className="system-status">
          <span className="status-dot" /> Dashboard online
        </div>
      </div>

      <section className="metrics">
        <article className="metric-card">
          <p>Security policies</p>
          <h2>—</h2>
          <span>Awaiting network rules</span>
        </article>
        <article className="metric-card">
          <p>Tests executed</p>
          <h2>0</h2>
          <span>Test results not connected</span>
        </article>
        <article className="metric-card">
          <p>Devices configured</p>
          <h2>—</h2>
          <span>Awaiting device API</span>
        </article>
        <article className="metric-card">
          <p>Policy engine</p>
          <h2 className="accent-text">READY</h2>
          <span>Basic evaluator implemented</span>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">PROJECT STATUS</p>
            <h2>Security components</h2>
          </div>
          <span className="tag">DEVELOPMENT</span>
        </div>

        {[
          ["ACL policy engine", "Implemented", "complete"],
          ["Automated ACL tests", "3 tests passing", "complete"],
          ["Cisco device configurations", "Awaiting backend API", "pending"],
          ["Packet Tracer verification", "Pending network setup", "pending"],
        ].map(([name, status, type]) => (
          <div className="status-row" key={name}>
            <div className={`status-icon ${type}`}>
              {type === "complete" ? "✓" : "·"}
            </div>
            <span>{name}</span>
            <span className={`status-label ${type}`}>{status}</span>
          </div>
        ))}
      </section>

      <section className="notice">
        <span className="notice-icon">i</span>
        <div>
          <strong>Backend integration pending</strong>
          <p>
            This dashboard currently displays development status. Live network
            metrics and ACL results will appear after the backend is connected.
          </p>
        </div>
      </section>
    </>
  );
}

function PlaceholderPage({ page }) {
  const details = {
    policy: {
      title: "ACL Policy",
      description:
        "Review KIOSK_IN and TELLER_IN rules and their expected packet decisions.",
      note: "Actual network rules will be added after the addressing plan is confirmed.",
    },
    tests: {
      title: "Security Tests",
      description:
        "Review permit and deny scenarios for your bank network.",
      note: "The three passing Python unit tests verify the basic policy engine only.",
    },
    configs: {
      title: "Device Configurations",
      description:
        "Inspect generated configurations for R1, SW1, and SW2.",
      note: "Configuration data will appear when Person A's API is available.",
    },
  };

  const item = details[page];

  return (
    <section className="panel placeholder">
      <p className="eyebrow">SECURITY / {page.toUpperCase()}</p>
      <h1>{item.title}</h1>
      <p className="muted">{item.description}</p>
      <div className="notice">
        <span className="notice-icon">i</span>
        <div>
          <strong>Integration pending</strong>
          <p>{item.note}</p>
        </div>
      </div>
    </section>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const activeItem = navigation.find((item) => item.id === activePage);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">N</div>
          <div>
            <strong>NETGUARD</strong>
            <span>BANK SECURITY</span>
          </div>
        </div>

        <p className="nav-heading">WORKSPACE</p>
        <nav>
          {navigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                activePage === item.id ? "active" : ""
              }`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
              {activePage === item.id && <span className="active-marker" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-indicator">
            <span className="status-dot" />
            <div>
              <strong>Local workspace</strong>
              <span>Development mode</span>
            </div>
          </div>
          <p className="sidebar-footer">NETWORK SECURITY PROJECT</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <span>Workspace <span className="crumb">/</span> {activeItem.label}</span>
          <span className="environment-badge">LOCAL ENVIRONMENT</span>
        </header>

        <div className="page-content">
          {activePage === "dashboard" ? (
            <Dashboard />
          ) : (
            <PlaceholderPage page={activePage} />
          )}
        </div>
      </main>
    </div>
  );
}
