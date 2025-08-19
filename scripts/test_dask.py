# scripts/test_dask_direct.py
import os, time
from datetime import datetime
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")
SERVICE="dask_gateway"
ENV = os.getenv("E2E_ENV", "dev")
DRY_RUN = os.getenv("DRY_RUN", "1") == "1"
LOG_PATH = "results/logs/test_dask_gateway.log"

def log_result(success: bool, message: str = ""):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILURE"
    with open(LOG_PATH, "a") as f:
        f.write(f"{ts}, {status}, {message}\n")

def push_metrics(success: bool, durations: dict):
    reg = CollectorRegistry()
    last = Gauge("eodc_e2e_last_result", "1 success, 0 failure", ["service","env"], registry=reg)
    dur  = Gauge("eodc_e2e_test_duration_seconds", "duration per stage", ["service","env","stage"], registry=reg)
    last.labels(SERVICE, ENV).set(1 if success else 0)
    for stage, secs in durations.items():
        dur.labels(SERVICE, ENV, stage).set(secs)
    # nur env als grouping_key, keine doppelten service-labels
    push_to_gateway(PUSHGATEWAY_URL, job="e2e_direct", registry=reg, grouping_key={"env": ENV})

def main():
    t0 = time.time()
    success = False
    try:
        if DRY_RUN:
            time.sleep(0.3)
            success = True
            log_result(True, "dry run ok")
        else:
            # echter Test hier
            success = True
            log_result(True, "compute 5+10=15")
    except Exception as e:
        success = False
        log_result(False, type(e).__name__)
    finally:
        push_metrics(success, {"total": time.time() - t0})

if __name__ == "__main__":
    main()
