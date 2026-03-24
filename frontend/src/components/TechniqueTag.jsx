export default function TechniqueTag({ id }) {
  if (!id) return null;
  const slug = String(id).replace(/\./g, "/");
  const url = `https://attack.mitre.org/techniques/${slug}`;
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="mr-1 mb-1 inline-block rounded border border-slate-600 bg-slate-800 px-2 py-0.5 text-xs text-sky-300 hover:bg-slate-700"
    >
      {id}
    </a>
  );
}
