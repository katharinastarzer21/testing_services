# scripts/logs_to_metrics.py
import os, glob
from datetime import datetime, timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Konfig über ENV
PUSHGATEWAY_URL = os.environ.get("PUSHGATEWAY_URL", "http://localhost:9091")
ENV            = os.environ.get("E2E_ENV", "dev")
LOG_DIR        = os.environ.get("LOG_DIR", "results/logs")
WINDOW_MINUTES = int(os.environ.get("WINDOW_MINUTES", "60"))

OK_TOKENS   = {"SUCCESS", "OK", "PASS"}
FAIL_TOKENS = {"FAILURE", "ERROR", "FAIL"}

def parse_line(line: str):
    # erwartet: "YYYY-MM-DD HH:MM[:SS], STATUS, message"
    parts = [p.strip() for p in line.strip().split(",", 2)]
    if len(parts) < 2:
        return None
    ts_s, status = parts[0], parts[1]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            ts = datetime.strptime(ts_s, fmt)
            break
        except ValueError:
            ts = None
    if ts is None:
        return None
    return ts, status.upper()

def service_from_filename(path: str) -> str:
    base = os.path.basename(path)  # z.B. test_dask_gateway.log
    name = base.replace("test_", "").replace(".log", "")
    return name.lower()

def push_series(series):
    reg = CollectorRegistry()
    g_last = Gauge("eodc_e2e_last_result", "Last E2E result (1/0)", ["service","env"], registry=reg)
    g_sc   = Gauge("eodc_e2e_success_count_1h", "Success lines in last 1h", ["service","env"], registry=reg)
    g_fc   = Gauge("eodc_e2e_failure_count_1h", "Failure lines in last 1h", ["service","env"], registry=reg)
    g_av   = Gauge("eodc_e2e_availability_ratio_1h", "success/(success+failure) in last 1h", ["service","env"], registry=reg)
    g_ts   = Gauge("eodc_e2e_last_success_timestamp", "Unix ts of last success", ["service","env"], registry=reg)

    for s in series:
        lbl = (s["service"], s["env"])
        g_last.labels(*lbl).set(s["last"])
        g_sc.labels(*lbl).set(s["succ"])
        g_fc.labels(*lbl).set(s["fail"])
        g_av.labels(*lbl).set(s["avail"])
        g_ts.labels(*lbl).set(s["last_succ_ts"])

    # geringe Kardinalität: ein Job, gruppiert nur nach env
    push_to_gateway(PUSHGATEWAY_URL, job="e2e_from_logs", registry=reg, grouping_key={"env": ENV})

def main():
    cutoff = datetime.now() - timedelta(minutes=WINDOW_MINUTES)
    series = []
    for path in glob.glob(os.path.join(LOG_DIR, "test_*.log")):
        service = service_from_filename(path)
        succ = fail = 0
        last = 0
        last_succ_ts = 0.0
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            continue

        for line in lines:
            parsed = parse_line(line)
            if not parsed:
                continue
            ts, status = parsed
            if status in OK_TOKENS:
                if ts >= cutoff: succ += 1
                last_succ_ts = max(last_succ_ts, ts.timestamp())
            elif status in FAIL_TOKENS:
                if ts >= cutoff: fail += 1

        # letzter Status
        for line in reversed(lines):
            parsed = parse_line(line)
            if parsed:
                _, status = parsed
                last = 1 if status in OK_TOKENS else 0
                break

        total = succ + fail
        avail = (succ/total) if total > 0 else (1.0 if last == 1 else 0.0)
        series.append({"service": service, "env": ENV, "last": last,
                       "succ": succ, "fail": fail, "avail": avail,
                       "last_succ_ts": last_succ_ts})

    if series:
        push_series(series)
        print("pushed metrics for:", ", ".join(sorted(s["service"] for s in series)))
    else:
        print(f"no logs found in {LOG_DIR}")

if __name__ == "__main__":
    main()
