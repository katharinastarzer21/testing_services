import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")
SERVICE = os.getenv("SERVICE", "dask_gateway")
ENV = os.getenv("ENV", "dev")

def main():
    reg = CollectorRegistry()
    g_pass = Gauge("eodc_e2e_test_pass", "1 if pass else 0", ["service","env"], registry=reg)
    g_dur  = Gauge("eodc_e2e_test_duration_seconds", "duration seconds per stage", ["service","env","stage"], registry=reg)

    g_pass.labels(SERVICE, ENV).set(1)
    g_dur.labels(SERVICE, ENV, "total").set(2.34)

    push_to_gateway(PUSHGATEWAY_URL, job="e2e_tests", registry=reg, grouping_key={"service": SERVICE, "env": ENV})
    print(f"pushed to {PUSHGATEWAY_URL} for service={SERVICE}, env={ENV}")

if __name__ == "__main__":
    main()
