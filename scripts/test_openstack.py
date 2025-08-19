import os
import base64
from datetime import datetime
import openstack

LOG_DIR  = "results/logs"
LOG_FILE = os.path.join(LOG_DIR, "test_openstack.log")

def log_result(status: str, message: str = ""):
    """
    Format: YYYY-MM-DD HH:MM:SS, SUCCESS|FAILURE, <message>
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts}, {status}, {message}\n")

def main():
    cloud   = os.getenv("OPENSTACK_CLOUD", "eodc-appcred")
    image   = os.getenv("OPENSTACK_IMAGE_ID")
    flavor  = os.getenv("OPENSTACK_FLAVOR_ID")
    network = os.getenv("OPENSTACK_NETWORK_ID")
    secgrp  = os.getenv("OPENSTACK_SECURITY_GROUP", "default")
    name_prefix = os.getenv("E2E_VM_PREFIX", "vm-test")

    # Vorab-Check auf nötige Variablen
    missing = [k for k,v in {
        "OPENSTACK_IMAGE_ID": image,
        "OPENSTACK_FLAVOR_ID": flavor,
        "OPENSTACK_NETWORK_ID": network
    }.items() if not v]
    if missing:
        log_result("FAILURE", f"missing: {','.join(missing)}")
        return

    conn = None
    server = None
    try:
        conn = openstack.connect(cloud=cloud)

        vm_name = f"{name_prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        cloud_init = os.getenv("OPENSTACK_CLOUD_INIT", "#!/bin/bash\necho $((17 * 3)) > /tmp/result.txt\n")
        user_data_b64 = base64.b64encode(cloud_init.encode("utf-8")).decode("utf-8")

        server = conn.compute.create_server(
            name=vm_name,
            image_id=image,
            flavor_id=flavor,
            networks=[{"uuid": network}],
            security_groups=[{"name": secgrp}],
            user_data=user_data_b64
        )

        server = conn.compute.wait_for_server(
            server, status="ACTIVE", failures=["ERROR"], interval=5, wait=300
        )
        log_result("SUCCESS", server.name)

    except Exception as e:
        log_result("FAILURE", type(e).__name__)
    finally:
        try:
            if conn and server:
                conn.compute.delete_server(server.id)
        except Exception:
            pass

if __name__ == "__main__":
    main()
