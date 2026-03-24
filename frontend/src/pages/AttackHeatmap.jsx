import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getHeatmap } from "../api/client.js";

const TACTIC_ORDER = [
  "Reconnaissance",
  "Resource Development",
  "Initial Access",
  "Execution",
  "Persistence",
  "Privilege Escalation",
  "Defense Evasion",
  "Credential Access",
  "Discovery",
  "Lateral Movement",
  "Collection",
  "Command and Control",
  "Exfiltration",
  "Impact",
];

const TECH_META = [
  { id: "T1046", name: "Network Service Discovery", tactic: "Discovery" },
  { id: "T1053.005", name: "Scheduled Task", tactic: "Persistence" },
  { id: "T1059.001", name: "PowerShell", tactic: "Execution" },
  { id: "T1071.004", name: "DNS", tactic: "Command and Control" },
  { id: "T1078", name: "Valid Accounts", tactic: "Initial Access" },
  { id: "T1003.001", name: "LSASS Memory", tactic: "Credential Access" },
  { id: "T1021.002", name: "SMB/Windows Admin Shares", tactic: "Lateral Movement" },
  { id: "T1110", name: "Brute Force", tactic: "Credential Access" },
  { id: "T1110.001", name: "Password Guessing", tactic: "Credential Access" },
  { id: "T1110.003", name: "Password Spraying", tactic: "Credential Access" },
  { id: "T1136.001", name: "Local Account", tactic: "Persistence" },
  { id: "T1543.003", name: "Windows Service", tactic: "Persistence" },
  { id: "T1548.003", name: "Sudo / Cached Creds", tactic: "Privilege Escalation" },
  { id: "T1550.002", name: "Pass the Hash", tactic: "Lateral Movement" },
  { id: "T1558.003", name: "Kerberoasting", tactic: "Credential Access" },
];

function heatColor(n) {
  if (!n) return "bg-slate-900 text-slate-500 border-slate-800";
  if (n <= 2) return "bg-yellow-900/50 text-yellow-100 border-yellow-800";
  if (n <= 5) return "bg-orange-900/50 text-orange-100 border-orange-700";
  return "bg-red-900/60 text-red-50 border-red-700";
}

export default function AttackHeatmap() {
  const navigate = useNavigate();
  const [counts, setCounts] = useState({});

  useEffect(() => {
    getHeatmap()
      .then((r) => setCounts(r.data))
      .catch(console.error);
  }, []);

  const cols = useMemo(() => {
    const byTactic = {};
    for (const t of TACTIC_ORDER) byTactic[t] = [];
    for (const row of TECH_META) {
      (byTactic[row.tactic] || byTactic["Discovery"]).push(row);
    }
    return TACTIC_ORDER.map((t) => ({ tactic: t, techniques: byTactic[t] || [] }));
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-4 text-xl font-semibold text-white">ATT&CK heatmap</h1>
      <p className="mb-4 text-sm text-slate-400">Click a technique cell to filter the alert queue.</p>
      <div className="overflow-auto rounded-xl border border-slate-800">
        <div className="flex min-w-[1100px] divide-x divide-slate-800">
          {cols.map((col) => (
            <div key={col.tactic} className="flex-1 bg-slate-950/40">
              <div className="sticky top-0 bg-slate-900/90 p-2 text-center text-xs font-semibold uppercase tracking-wide text-slate-300">
                {col.tactic}
              </div>
              <div className="space-y-2 p-2">
                {col.techniques.map((cell) => {
                  const n = counts[cell.id] || 0;
                  return (
                    <button
                      type="button"
                      key={cell.id}
                      onClick={() => navigate(`/alerts?technique=${encodeURIComponent(cell.id)}`)}
                      className={`w-full rounded-lg border p-2 text-left text-xs transition hover:ring-2 hover:ring-sky-500 ${heatColor(n)}`}
                    >
                      <div className="font-mono text-[11px]">{cell.id}</div>
                      <div className="mt-1 leading-snug">{cell.name}</div>
                      <div className="mt-1 font-semibold">Count: {n}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
