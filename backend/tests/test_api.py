from datetime import datetime, timezone


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ingest_and_list_alerts(client):
    payload = {
        "source_type": "windows_auth",
        "log": {
            "TimeCreated": datetime.now(timezone.utc).isoformat(),
            "EventID": 4625,
            "SubjectUserName": "u",
            "IpAddress": "10.50.50.50",
            "WorkstationName": "w",
            "LogonType": 3,
            "Status": "0xC000006D",
            "SubStatus": "0xC000006A",
        },
    }
    for _ in range(6):
        r = client.post("/api/ingest", json=payload)
        assert r.status_code == 200, r.text
    r = client.get("/api/alerts")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1


def test_rules_endpoint(client):
    r = client.get("/api/rules")
    assert r.status_code == 200
    rules = r.json()
    assert len(rules) >= 15


def test_metrics(client):
    r = client.get("/api/metrics")
    assert r.status_code == 200
    m = r.json()
    assert "by_severity" in m
    assert "fp_rate_by_rule" in m


def test_cases_flow(client):
    r = client.post("/api/cases", json={"title": "IR-1", "severity": "high"})
    assert r.status_code == 200
    cid = r.json()["id"]
    r2 = client.get("/api/cases")
    assert any(c["id"] == cid for c in r2.json())
