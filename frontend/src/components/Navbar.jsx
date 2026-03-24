import { NavLink } from "react-router-dom";

const linkClass = ({ isActive }) =>
  `block rounded-lg px-3 py-2 text-sm font-medium ${
    isActive ? "bg-sky-600 text-white" : "text-slate-300 hover:bg-slate-800"
  }`;

const items = [
  ["/alerts", "Alerts"],
  ["/cases", "Cases"],
  ["/attack-matrix", "ATT&CK Matrix"],
  ["/metrics", "Metrics"],
  ["/rules", "Rules"],
];

export default function Navbar() {
  return (
    <aside className="flex w-56 shrink-0 flex-col border-r border-slate-800 bg-slate-900/80 p-4">
      <div className="mb-6 text-lg font-semibold text-sky-400">SOC Console</div>
      <nav className="flex flex-col gap-1">
        {items.map(([to, label]) => (
          <NavLink key={to} to={to} className={linkClass} end={to === "/alerts"}>
            {label}
          </NavLink>
        ))}
      </nav>
      <p className="mt-auto pt-6 text-xs text-slate-500">Local simulation · MITRE ATT&CK</p>
    </aside>
  );
}
