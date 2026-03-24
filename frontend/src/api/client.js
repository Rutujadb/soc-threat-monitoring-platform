import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

export function getAlerts(params) {
  return client.get("/alerts", { params });
}

export function getAlert(id) {
  return client.get(`/alerts/${id}`);
}

export function patchAlert(id, body) {
  return client.patch(`/alerts/${id}`, body);
}

export function getCases() {
  return client.get("/cases");
}

export function createCase(body) {
  return client.post("/cases", body);
}

export function patchCase(id, body) {
  return client.patch(`/cases/${id}`, body);
}

export function linkAlertToCase(caseId, alertId) {
  return client.post(`/cases/${caseId}/alerts`, { alert_id: alertId });
}

export function getCaseDetail(caseId) {
  return client.get(`/cases/${caseId}/detail`);
}

export function getMetrics() {
  return client.get("/metrics");
}

export function getHeatmap() {
  return client.get("/attack-heatmap");
}

export function getRules() {
  return client.get("/rules");
}

export function getPlaybook(ruleId) {
  return client.get(`/playbooks/${ruleId}`, { responseType: "text" });
}
