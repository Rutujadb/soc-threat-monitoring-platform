import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import AlertQueue from "./pages/AlertQueue.jsx";
import AlertDetail from "./pages/AlertDetail.jsx";
import Cases from "./pages/Cases.jsx";
import AttackHeatmap from "./pages/AttackHeatmap.jsx";
import MetricsDashboard from "./pages/MetricsDashboard.jsx";
import Rules from "./pages/Rules.jsx";
import PlaybookViewer from "./pages/PlaybookViewer.jsx";

export default function App() {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <main className="grow overflow-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/alerts" replace />} />
          <Route path="/alerts" element={<AlertQueue />} />
          <Route path="/alerts/:id" element={<AlertDetail />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/attack-matrix" element={<AttackHeatmap />} />
          <Route path="/metrics" element={<MetricsDashboard />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/playbooks/:ruleId" element={<PlaybookViewer />} />
        </Routes>
      </main>
    </div>
  );
}
