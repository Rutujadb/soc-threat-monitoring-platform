const map = {
  critical: "bg-red-900 text-red-100 border border-red-700",
  high: "bg-orange-900 text-orange-100 border border-orange-700",
  medium: "bg-amber-900 text-amber-100 border border-amber-700",
  low: "bg-sky-900 text-sky-100 border border-sky-700",
};

export default function SeverityBadge({ value }) {
  const c = map[String(value || "").toLowerCase()] || "bg-slate-800 text-slate-200 border border-slate-600";
  return <span className={`rounded-full px-2 py-0.5 text-xs uppercase tracking-wide ${c}`}>{value}</span>;
}
