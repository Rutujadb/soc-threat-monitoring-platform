const map = {
  new: "bg-slate-700 text-slate-100",
  investigating: "bg-blue-900 text-blue-100",
  escalated: "bg-red-900 text-red-100",
  resolved: "bg-emerald-900 text-emerald-100",
  false_positive: "bg-purple-900 text-purple-100",
};

export default function StatusBadge({ value }) {
  const key = String(value || "").toLowerCase().replace(/ /g, "_");
  const c = map[key] || "bg-slate-800 text-slate-200";
  const label = String(value || "").replace(/_/g, " ");
  return <span className={`rounded-full px-2 py-0.5 text-xs capitalize ${c}`}>{label}</span>;
}
