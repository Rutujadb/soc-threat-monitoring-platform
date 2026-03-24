export default function MetricCard({ title, value, subtitle }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow">
      <div className="text-xs uppercase tracking-wide text-slate-500">{title}</div>
      <div className="mt-2 text-3xl font-semibold text-white">{value}</div>
      {subtitle ? <div className="mt-1 text-xs text-slate-400">{subtitle}</div> : null}
    </div>
  );
}
