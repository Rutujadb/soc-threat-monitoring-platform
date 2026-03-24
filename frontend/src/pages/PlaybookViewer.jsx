import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { getPlaybook, getRules } from "../api/client.js";

export default function PlaybookViewer() {
  const { ruleId } = useParams();
  const [md, setMd] = useState("");
  const [title, setTitle] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [{ data: text }, { data: rules }] = await Promise.all([getPlaybook(ruleId), getRules()]);
        setMd(text);
        const r = rules.find((x) => x.id === ruleId);
        setTitle(r?.name || ruleId);
      } catch (e) {
        console.error(e);
        setMd("# Playbook not found");
      }
    })();
  }, [ruleId]);

  return (
    <div className="p-6">
      <Link to="/rules" className="text-sm text-sky-400 hover:underline">
        ← Rules catalog
      </Link>
      <h1 className="mt-4 text-2xl font-semibold text-white">{title}</h1>
      <article className="mt-6 max-w-4xl space-y-3 text-slate-200 [&_a]:text-sky-400 [&_h1]:text-2xl [&_h1]:font-semibold [&_h2]:text-xl [&_ul]:list-disc [&_ul]:pl-6">
        <ReactMarkdown>{md}</ReactMarkdown>
      </article>
    </div>
  );
}
