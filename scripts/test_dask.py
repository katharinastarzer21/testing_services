from eodc.dask import EODCDaskGateway
from dask.distributed import Client
from unittest.mock import patch
import os
from datetime import datetime

class CustomEODCDaskGateway(EODCDaskGateway):
    def __init__(self, username, password):
        self._password = password
        super().__init__(username=username)

    def _authenticate(self):
        return self._password
    
def get_cluster_options(gateway):
    try:
        cluster_options = gateway.cluster_options()
    except Exception as e:
        print(f"Error cluster options: {e}")

def log_result(success):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "SUCCESS" if success else "FAILURE"
    with open("results/logs/test_DaskGateway.log", "a") as log_file:
        log_file.write(f"{timestamp} - {result}\n")

def create_and_connect_cluster(gateway):
    
    try:
        cluster = gateway.new_cluster()
        client = Client(cluster)
        cluster.scale(2)  
        return cluster, client
    except Exception as e:
        return None, None

def test_simple_computation(client):
    
    try:
        def add(x, y):
            return x + y
        future = client.submit(add, 5, 10)
        result = future.result()
        assert result == 15
        
    except Exception as e:
        return

def main():
    username = os.getenv("EODC_USERNAME")
    password = os.getenv("EODC_PASSWORD")

   # if not username or not password:
  #      log_result(False)  
#        raise ValueError("Error EODC_USERNAME or EODC_PASSWORD")

    with patch("getpass.getpass", return_value=password):     
        gateway = CustomEODCDaskGateway(username=username, password=password)
        get_cluster_options(gateway)
        cluster, client = create_and_connect_cluster(gateway)
        if client:
            test_simple_computation(client)
        if cluster:
            cluster.close()
                
        log_result(True)  
           
if __name__ == "__main__":
    main()