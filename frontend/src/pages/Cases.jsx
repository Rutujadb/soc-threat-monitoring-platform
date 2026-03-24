import { useEffect, useMemo, useState } from "react";
import { createCase, getCases, getCaseDetail } from "../api/client.js";
import SeverityBadge from "../components/SeverityBadge.jsx";

const COLS = [
  ["open", "Open"],
  ["investigating", "Investigating"],
  ["escalated", "Escalated"],
  ["resolved", "Resolved"],
];

export default function Cases() {
  const [cases, setCases] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [detail, setDetail] = useState(null);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ title: "", severity: "medium", description: "" });

  async function load() {
    const { data } = await getCases();
    setCases(data);
  }

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const grouped = useMemo(() => {
    const g = { open: [], investigating: [], escalated: [], resolved: [] };
    for (const c of cases) {
      const k = g[c.status] ? c.status : "open";
      (g[k] || g.open).push(c);
    }
    return g;
  }, [cases]);

  async function openDetail(id) {
    if (expanded === id) {
      setExpanded(null);
      setDetail(null);
      return;
    }
    setExpanded(id);
    const { data } = await getCaseDetail(id);
    setDetail(data);
  }

  async function submitNew(e) {
    e.preventDefault();
    await createCase(form);
    setModal(false);
    setForm({ title: "", severity: "medium", description: "" });
    await load();
  }

  return (
    <div className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white">Cases</h1>
        <button
          type="button"
          onClick={() => setModal(true)}
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
        >
          New case
        </button>
      </div>

      {modal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <form
            onSubmit={submitNew}
            className="w-full max-w-lg space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-6 shadow-xl"
          >
            <div className="text-lg font-semibold text-white">New case</div>
            <input
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              placeholder="Title"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              value={form.severity}
              onChange={(e) => setForm({ ...form, severity: e.target.value })}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <textarea
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              rows={3}
              placeholder="Description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
            <div className="flex justify-end gap-2">
              <button type="button" className="rounded-lg px-3 py-2 text-sm text-slate-300" onClick={() => setModal(false)}>
                Cancel
              </button>
              <button type="submit" className="rounded-lg bg-sky-600 px-4 py-2 text-sm text-white">
                Create
              </button>
            </div>
          </form>
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-4">
        {COLS.map(([key, label]) => (
          <div key={key} className="rounded-xl border border-slate-800 bg-slate-900/30 p-3">
            <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">{label}</div>
            <div className="space-y-2">
              {(grouped[key] || []).map((c) => (
                <div key={c.id}>
                  <button
                    type="button"
                    onClick={() => openDetail(c.id)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-950/40 p-3 text-left hover:border-slate-600"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="font-medium text-slate-100">{c.title}</div>
                      <SeverityBadge value={c.severity} />
                    </div>
                    <div className="mt-1 text-xs text-slate-500">{c.alert_count} alerts</div>
                    <div className="text-xs text-slate-500">{new Date(c.created_at).toLocaleString()}</div>
                  </button>
                  {expanded === c.id && detail ? (
                    <div className="mt-2 rounded-lg border border-slate-800 bg-black/30 p-2 text-xs text-slate-300">
                      <div className="mb-1 text-slate-500">Linked alerts</div>
                      {(detail.alerts || []).length === 0 ? (
                        <div>No linked alerts</div>
                      ) : (
                        <ul className="space-y-1">
                          {detail.alerts.map((a) => (
                            <li key={a.id}>
                              <span className="text-slate-400">{a.rule_name}</span> ·{" "}
                              <SeverityBadge value={a.severity} />
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
