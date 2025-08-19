up:
	docker compose up -d

down:
	docker compose down -v

push-probe:
	PUSHGATEWAY_URL=http://localhost:9091 python3 scripts/push_probe.py

test-dry:
	DRY_RUN=1 PUSHGATEWAY_URL=http://localhost:9091 python3 tests/test_dask_gateway_e2e.py
