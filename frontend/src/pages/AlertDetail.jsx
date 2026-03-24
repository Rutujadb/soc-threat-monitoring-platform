import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getAlert, getCases, patchAlert, linkAlertToCase } from "../api/client.js";
import SeverityBadge from "../components/SeverityBadge.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import TechniqueTag from "../components/TechniqueTag.jsx";

export default function AlertDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("new");
  const [assignee, setAssignee] = useState("");
  const [note, setNote] = useState("");
  const [cases, setCases] = useState([]);
  const [caseId, setCaseId] = useState("");

  async function refresh() {
    const { data: d } = await getAlert(id);
    setData(d);
    setStatus(d.status);
    setAssignee(d.assigned_to || "");
  }

  useEffect(() => {
    refresh().catch(console.error);
    getCases()
      .then((r) => setCases(r.data))
      .catch(console.error);
  }, [id]);

  async function submitUpdate() {
    await patchAlert(id, { status, assigned_to: assignee, note_content: note || undefined });
    setNote("");
    await refresh();
  }

  async function addToCase() {
    if (!caseId) return;
    await linkAlertToCase(caseId, id);
    alert("Linked to case");
  }

  if (!data) return <div className="p-6 text-slate-400">Loading…</div>;

  return (
    <div className="grid gap-4 p-6 lg:grid-cols-3">
      <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/40 p-4 lg:col-span-1">
        <Link to="/alerts" className="text-sm text-sky-400 hover:underline">
          ← Back to queue
        </Link>
        <h1 className="text-xl font-semibold text-white">{data.rule_name}</h1>
        <div className="flex flex-wrap gap-2">
          <SeverityBadge value={data.severity} />
          <StatusBadge value={data.status} />
        </div>
        <div className="text-sm text-slate-300">
          <div>
            <span className="text-slate-500">Host:</span> {data.affected_host || "—"}
          </div>
          <div>
            <span className="text-slate-500">Source IP:</span> {data.source_ip || "—"}
          </div>
          <div>
            <span className="text-slate-500">Assigned:</span> {data.assigned_to || "—"}
          </div>
        </div>
        <div>
          <div className="text-xs uppercase text-slate-500">MITRE</div>
          <div className="mt-1 flex flex-wrap">
            {(data.mitre_techniques || []).map((t) => (
              <TechniqueTag key={t} id={t} />
            ))}
          </div>
        </div>
        <div className="space-y-2 border-t border-slate-800 pt-4">
          <label className="text-xs text-slate-500">Status</label>
          <select
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="new">New</option>
            <option value="investigating">Investigating</option>
            <option value="escalated">Escalated</option>
            <option value="resolved">Resolved</option>
            <option value="false_positive">False Positive</option>
          </select>
          <label className="text-xs text-slate-500">Assign to</label>
          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
            value={assignee}
            onChange={(e) => setAssignee(e.target.value)}
          />
          <button
            type="button"
            onClick={submitUpdate}
            className="w-full rounded-lg bg-sky-600 px-3 py-2 text-sm font-medium text-white hover:bg-sky-500"
          >
            Update alert
          </button>
        </div>
        <div className="space-y-2 border-t border-slate-800 pt-4">
          <div className="text-xs text-slate-500">Add to case</div>
          <select
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-sm"
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
          >
            <option value="">Select case…</option>
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={addToCase}
            className="w-full rounded-lg border border-slate-600 px-3 py-2 text-sm text-slate-100 hover:bg-slate-800"
          >
            Link alert
          </button>
          {data.playbook_path ? (
            <Link
              to={`/playbooks/${data.rule_id}`}
              className="block text-center text-sm text-sky-400 hover:underline"
            >
              Open playbook
            </Link>
          ) : null}
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 lg:col-span-1">
        <div className="text-xs uppercase text-slate-500">Raw event</div>
        <pre className="mt-2 max-h-[480px] overflow-auto rounded-lg bg-black/40 p-3 text-xs text-emerald-200">
          {JSON.stringify(data.raw_event, null, 2)}
        </pre>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 lg:col-span-1">
        <div className="text-xs uppercase text-slate-500">Investigation notes</div>
        <div className="mt-2 space-y-3">
          {(data.notes || []).map((n) => (
            <div key={n.id} className="rounded-lg border border-slate-800 bg-slate-950/40 p-2 text-sm">
              <div className="text-xs text-slate-500">
                {new Date(n.timestamp).toLocaleString()} · {n.author}
              </div>
              <div className="mt-1 text-slate-200">{n.content}</div>
            </div>
          ))}
        </div>
        <textarea
          className="mt-3 w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-sm"
          rows={4}
          placeholder="Add note…"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <button
          type="button"
          onClick={submitUpdate}
          className="mt-2 rounded-lg bg-slate-800 px-3 py-2 text-sm text-white hover:bg-slate-700"
        >
          Add note
        </button>
      </div>
    </div>
  );
}
