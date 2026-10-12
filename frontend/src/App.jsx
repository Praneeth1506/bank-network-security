import { useEffect, useState } from "react";
import "./App.css";
import Plan from "./pages/Plan.jsx";
import PolicyChecker from "./pages/PolicyChecker.jsx";
import Tests from "./pages/Tests.jsx";

const navigation = [
  { id: "dashboard", label: "Dashboard", icon: "◉" },
  { id: "plan", label: "Network Plan", icon: "⌘" },
  { id: "policy", label: "ACL Policy", icon: "⇄" },
  { id: "tests", label: "Security Tests", icon: "✓" },
  { id: "configs", label: "Device Configs", icon: "▤" },
];

function Dashboard({ setActivePage }) {
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">NETWORK OPERATIONS / OVERVIEW</p>
          <h1>Security Dashboard</h1>
          <p className="muted">
            Manage network addressing, access control, security tests, and
            device configurations.
          </p>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          Backend integration
        </div>
      </div>

      <section className="metrics">
        {[
          {
            title: "Network Plan",
            value: "VLSM",
            detail: "View the bank network addressing plan",
            page: "plan",
          },
          {
            title: "Access Control",
            value: "ACL",
            detail: "Check whether network traffic is permitted",
            page: "policy",
          },
          {
            title: "Security Tests",
            value: "TEST",
            detail: "Record and review test outcomes",
            page: "tests",
          },
          {
            title: "Device Configs",
            value: "3",
            detail: "R1, SW1, and SW2",
            page: "configs",
          },
        ].map((item) => (
          <button
            className="metric-card dashboard-link"
            key={item.page}
            onClick={() => setActivePage(item.page)}
          >
            <p>{item.title}</p>
            <h2 className="accent-text">{item.value}</h2>
            <span>{item.detail}</span>
          </button>
        ))}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">WORKSPACE</p>
            <h2>Network Security Components</h2>
          </div>
          <span className="tag">LOCAL ENVIRONMENT</span>
        </div>

        {[
          ["Network addressing plan", "View VLANs, gateways, and subnets", "plan"],
          ["ACL policy checker", "Test permit and deny decisions", "policy"],
          ["Security test tracker", "Record observed test results", "tests"],
          ["Device configurations", "Inspect router and switch configurations", "configs"],
        ].map(([name, description, page]) => (
          <button
            className="status-row dashboard-row"
            key={page}
            onClick={() => setActivePage(page)}
          >
            <span className="status-icon complete">✓</span>
            <span className="dashboard-row-text">
              <strong>{name}</strong>
              <small>{description}</small>
            </span>
            <span className="status-label complete">OPEN →</span>
          </button>
        ))}
      </section>
    </>
  );
}

function DeviceConfigs() {
  const [devices, setDevices] = useState([]);
  const [selected, setSelected] = useState("R1");
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadDevices() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/config");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      const data = await response.json();
      const names = Object.keys(data.devices ?? {});
      setDevices(names);

      const device = names.includes(selected) ? selected : names[0];
      if (device) {
        setSelected(device);
        await loadConfig(device);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadConfig(device) {
    setError("");
    setConfig(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/config/${encodeURIComponent(device)}`
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      setConfig(await response.json());
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    loadDevices();
  }, []);

  return (
    <section className="panel">
      <p className="eyebrow">NETWORK / CONFIGURATION</p>
      <h1>Device Configurations</h1>
      <p className="muted">
        Inspect the configurations generated for the bank network devices.
      </p>

      {error && <p className="error-message">{error}</p>}
      {loading && <p className="muted">Loading devices...</p>}

      <div className="config-controls">
        {devices.map((device) => (
          <button
            key={device}
            className={`action-button ${selected === device ? "selected" : ""}`}
            onClick={() => {
              setSelected(device);
              loadConfig(device);
            }}
          >
            {device}
          </button>
        ))}

        {selected && (
          <a
            className="action-button"
            href={`http://localhost:8000/api/config/${encodeURIComponent(selected)}.txt`}
            target="_blank"
            rel="noreferrer"
          >
            Download {selected} .txt
          </a>
        )}
      </div>

      {config && (
        <pre className="config-output">
          {JSON.stringify(config, null, 2)}
        </pre>
      )}
    </section>
  );
}

function PlaceholderPage({ page }) {
  const details = {
    unknown: {
      title: "Page Not Found",
      description: "Select a page from the navigation menu.",
    },
  };

  const item = details[page] ?? details.unknown;

  return (
    <section className="panel placeholder">
      <p className="eyebrow">SECURITY / WORKSPACE</p>
      <h1>{item.title}</h1>
      <p className="muted">{item.description}</p>
    </section>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const activeItem = navigation.find((item) => item.id === activePage);

  function renderPage() {
    switch (activePage) {
      case "dashboard":
        return <Dashboard setActivePage={setActivePage} />;
      case "plan":
        return <Plan />;
      case "policy":
        return <PolicyChecker />;
      case "tests":
        return <Tests />;
      case "configs":
        return <DeviceConfigs />;
      default:
        return <PlaceholderPage page={activePage} />;
    }
  }

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
              className={`nav-item ${activePage === item.id ? "active" : ""}`}
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
          <span>
            Workspace <span className="crumb">/</span>{" "}
            {activeItem?.label ?? "Page"}
          </span>
          <span className="environment-badge">LOCAL ENVIRONMENT</span>
        </header>

        <div className="page-content">{renderPage()}</div>
      </main>
    </div>
  );
}