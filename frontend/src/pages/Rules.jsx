import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getRules } from "../api/client.js";
import SeverityBadge from "../components/SeverityBadge.jsx";
import TechniqueTag from "../components/TechniqueTag.jsx";

export default function Rules() {
  const [rules, setRules] = useState([]);

  useEffect(() => {
    getRules()
      .then((r) => setRules(r.data))
      .catch(console.error);
  }, []);

  return (
    <div className="p-6">
      <h1 className="mb-4 text-xl font-semibold text-white">Detection rules</h1>
      <div className="overflow-auto rounded-xl border border-slate-800">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-3 py-2">ID</th>
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2">Severity</th>
              <th className="px-3 py-2">MITRE</th>
              <th className="px-3 py-2">Triggers</th>
              <th className="px-3 py-2">Playbook</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((r) => (
              <tr key={r.id} className="border-t border-slate-800">
                <td className="px-3 py-2 font-mono text-xs text-slate-400">{r.id}</td>
                <td className="px-3 py-2 text-slate-100">{r.name}</td>
                <td className="px-3 py-2">
                  <SeverityBadge value={r.severity} />
                </td>
                <td className="px-3 py-2">
                  {(r.mitre_techniques || []).map((t) => (
                    <TechniqueTag key={t} id={t} />
                  ))}
                </td>
                <td className="px-3 py-2 text-slate-300">{r.trigger_count ?? 0}</td>
                <td className="px-3 py-2">
                  <Link className="text-sky-400 hover:underline" to={`/playbooks/${r.id}`}>
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
