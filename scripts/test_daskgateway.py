from eodc.dask import EODCDaskGateway
from dask.distributed import Client
from unittest.mock import patch
from datetime import datetime
import os

LOG_DIR = "results/logs"
LOG_FILE = os.path.join(LOG_DIR, "test_dask_gateway.log") 

class CustomEODCDaskGateway(EODCDaskGateway):
    def __init__(self, username, password):
        self._password = password
        super().__init__(username=username)

    def _authenticate(self):
        return self._password

def log_result(status: str, message: str = ""):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp}, {status}, {message}\n")

def get_cluster_options(gateway):
    try:
        _ = gateway.cluster_options()
    except Exception as e:
        log_result("FAILURE", f"cluster_options: {type(e).__name__}")
        raise

def create_and_connect_cluster(gateway):
    try:
        cluster = gateway.new_cluster()
        client = Client(cluster)
        cluster.scale(2)
        return cluster, client
    except Exception as e:
        log_result("FAILURE", f"cluster/client: {type(e).__name__}")
        raise

def test_simple_computation(client):
    try:
        def add(x, y): return x + y
        future = client.submit(add, 5, 10)
        result = future.result(timeout=30)
        assert result == 15
    except Exception as e:
        log_result("FAILURE", f"compute: {type(e).__name__}")
        raise

def main():
    username = os.getenv("EODC_USERNAME")
    password = os.getenv("EODC_PASSWORD")
    if not username or not password:
        log_result("FAILURE", "missing EODC_USERNAME/EODC_PASSWORD")
        return

    cluster = None
    client = None
    try:
        with patch("getpass.getpass", return_value=password):
            gateway = CustomEODCDaskGateway(username=username, password=password)

        try:
            get_cluster_options(gateway)
        except Exception:
            
            pass

        cluster, client = create_and_connect_cluster(gateway)
        test_simple_computation(client)

        log_result("SUCCESS", "compute 5+10=15")

    except Exception:
        if not os.path.exists(LOG_FILE):
            log_result("FAILURE", "unhandled error")
    finally:
        try:
            if client:
                client.close()
            if cluster:
                cluster.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
