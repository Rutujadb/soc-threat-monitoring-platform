import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getAlerts } from "../api/client.js";
import SeverityBadge from "../components/SeverityBadge.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import TechniqueTag from "../components/TechniqueTag.jsx";

export default function AlertQueue() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const techFromUrl = searchParams.get("technique") || "";

  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [q, setQ] = useState("");
  const [technique, setTechnique] = useState(techFromUrl);

  useEffect(() => {
    setTechnique(techFromUrl);
  }, [techFromUrl]);

  const params = useMemo(() => {
    const p = { limit: 100 };
    if (severity) p.severity = severity;
    if (status) p.status = status;
    if (q) p.q = q;
    if (technique) p.mitre_technique = technique;
    return p;
  }, [severity, status, q, technique]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { data } = await getAlerts(params);
        if (!cancelled) {
          setRows(data.items || []);
          setTotal(data.total || 0);
        }
      } catch (e) {
        console.error(e);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params]);

  return (
    <div className="p-6">
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-xs text-slate-500">Severity</label>
          <select
            className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
          >
            <option value="">Any</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-500">Status</label>
          <select
            className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">Any</option>
            <option value="new">New</option>
            <option value="investigating">Investigating</option>
            <option value="escalated">Escalated</option>
            <option value="resolved">Resolved</option>
            <option value="false_positive">False Positive</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-500">MITRE technique</label>
          <input
            className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
            placeholder="e.g. T1110"
            value={technique}
            onChange={(e) => setTechnique(e.target.value)}
          />
        </div>
        <div className="grow">
          <label className="block text-xs text-slate-500">Search host / IP / rule</label>
          <input
            className="w-full max-w-md rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <div className="text-sm text-slate-400">
          Total: <span className="text-white">{total}</span>
        </div>
      </div>

      <div className="overflow-auto rounded-xl border border-slate-800">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-3 py-2">Time</th>
              <th className="px-3 py-2">Severity</th>
              <th className="px-3 py-2">Rule</th>
              <th className="px-3 py-2">Host</th>
              <th className="px-3 py-2">Source IP</th>
              <th className="px-3 py-2">MITRE</th>
              <th className="px-3 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr
                key={a.id}
                className="cursor-pointer border-t border-slate-800 hover:bg-slate-800/40"
                onClick={() => navigate(`/alerts/${a.id}`)}
              >
                <td className="px-3 py-2 whitespace-nowrap text-slate-300">{new Date(a.timestamp).toLocaleString()}</td>
                <td className="px-3 py-2">
                  <SeverityBadge value={a.severity} />
                </td>
                <td className="px-3 py-2 text-slate-200">{a.rule_name}</td>
                <td className="px-3 py-2 text-slate-300">{a.affected_host || "—"}</td>
                <td className="px-3 py-2 text-slate-300">{a.source_ip || "—"}</td>
                <td className="px-3 py-2">
                  {(a.mitre_techniques || []).map((t) => (
                    <TechniqueTag key={t} id={t} />
                  ))}
                </td>
                <td className="px-3 py-2">
                  <StatusBadge value={a.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
