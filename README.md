# EODC E2E Observability (Local)

Lokaler Stack zum Testen von **Prometheus + Pushgateway + Grafana** für E2E-Testmetriken.

## Inhalt
- **Docker Compose** für Prometheus, Pushgateway, Grafana (inkl. Prometheus-Datasource).
- **scripts/push_probe.py**: Mini-Pusher (simuliert Pass/Fail & Dauer).
- **tests/test_dask_gateway_e2e.py**: Beispieltest mit **DRY_RUN**, der Metriken in den Pushgateway schreibt.
- **Grafana-Dashboard** wird automatisch provisioniert (einfache Kacheln für Pass/Fail & Dauer).

## Voraussetzungen
- Docker & Docker Compose
- Python 3 (nur falls du `push_probe.py`/Tests lokal ausführen willst)

## Start
```bash
docker compose up -d
# Prometheus: http://localhost:9090
# Pushgateway: http://localhost:9091
# Grafana:    http://localhost:3000  (Login: admin / admin)
```

## Erste Metrik pushen (ohne Python)
```bash
echo 'eodc_e2e_test_pass{service="dask_gateway",env="dev"} 1' \
 | curl --data-binary @- http://localhost:9091/metrics/job/e2e_tests/run/local
```

## Python-Probe (optional)
```bash
python3 -m pip install -r requirements.txt
export PUSHGATEWAY_URL=http://localhost:9091
python3 scripts/push_probe.py
```

## Beispieltest (DRY_RUN lokal)
```bash
export DRY_RUN=1
export PUSHGATEWAY_URL=http://localhost:9091
python3 tests/test_dask_gateway_e2e.py
```
Danach siehst du in Grafana/Prometheus:
- `eodc_e2e_test_pass{service="dask_gateway",env="dev"}`
- `eodc_e2e_test_duration_seconds{service="dask_gateway",env="dev",stage="total"}`

## Stoppen
```bash
docker compose down -v
```

## Nächste Schritte (Firma)
- `PUSHGATEWAY_URL` auf internen Endpoint stellen (z. B. `https://pushgateway.company.internal:9091`).
- Self-hosted Runner in GitHub Actions nutzen und den Push-Step in den Workflow einbauen.
- Dashboard/Alerts anpassen/erweitern.
