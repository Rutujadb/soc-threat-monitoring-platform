import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import { getMetrics } from "../api/client.js";
import MetricCard from "../components/MetricCard.jsx";

const COLORS = ["#ef4444", "#f97316", "#eab308", "#38bdf8", "#a78bfa"];

export default function MetricsDashboard() {
  const [m, setM] = useState(null);

  useEffect(() => {
    getMetrics()
      .then((r) => setM(r.data))
      .catch(console.error);
  }, []);

  if (!m) return <div className="p-6 text-slate-400">Loading…</div>;

  const sevData = Object.entries(m.by_severity || {}).map(([name, value]) => ({ name, value }));
  const statData = Object.entries(m.by_status || {}).map(([name, value]) => ({ name, value }));
  const topTech = (m.by_technique_top10 || []).map((x) => ({ name: x.technique, value: x.count }));
  const fpRows = Object.entries(m.fp_rate_by_rule || {}).map(([rule, v]) => ({
    name: rule,
    fp_rate: v.fp_rate,
    total: v.total,
  }));
  const overTime = m.alerts_over_time || [];
  const cards = m.summary_cards || {};

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-xl font-semibold text-white">Detection metrics</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total alerts (24h)" value={m.total_alerts_24h ?? m.totals_by_period?.["24h"] ?? 0} />
        <MetricCard title="Open alerts" value={cards.open_alerts ?? 0} />
        <MetricCard title="Critical (open)" value={cards.critical_alerts ?? 0} />
        <MetricCard title="Avg MTTD (min)" value={cards.avg_mttd_minutes ?? 0} subtitle="Blended across severities" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <div className="mb-2 text-sm font-medium text-slate-300">Alerts by severity (7d)</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sevData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="value" fill="#38bdf8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <div className="mb-2 text-sm font-medium text-slate-300">Alert status distribution</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={statData} dataKey="value" nameKey="name" outerRadius={80} label>
                  {statData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
        <div className="mb-2 text-sm font-medium text-slate-300">Alerts over time</div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={overTime}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Line type="monotone" dataKey="count" stroke="#22c55e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <div className="mb-2 text-sm font-medium text-slate-300">Top MITRE techniques (30d)</div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topTech} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis type="category" dataKey="name" width={80} stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="value" fill="#f97316" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
          <div className="mb-2 text-sm font-medium text-slate-300">False positive rate by rule</div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fpRows}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="fp_rate" fill="#a78bfa" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
