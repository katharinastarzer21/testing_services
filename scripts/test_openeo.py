
import os, random
from datetime import datetime
import openeo

LOG_DIR  = "results/logs"
LOG_FILE = os.path.join(LOG_DIR, "test_openeo.log")  

def log_result(status: str, message: str = ""):

    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts}, {status}, {message}\n")

def authenticate(conn: "openeo.Connection") -> bool:
    try:
        refresh = os.getenv("OPENEO_REFRESH_TOKEN")
        if refresh:
            conn.authenticate_oidc_refresh_token(refresh)
            return True

        token_path = os.path.expanduser("~/.openeo-refresh-token")
        if os.path.exists(token_path):
            with open(token_path, "r") as fh:
                tok = fh.read().strip()
            if tok:
                conn.authenticate_oidc_refresh_token(tok)
                return True

        conn.authenticate_oidc(client_id="openeo-platform-default-client")
        return True
    except Exception:
        return False

def get_random_collection(conn: "openeo.Connection"):
    try:
        cols = conn.list_collections()
        if not cols:
            return None
        ids = [c.get("id") for c in cols if isinstance(c, dict) and "id" in c]
        return random.choice(ids) if ids else None
    except Exception:
        return None

def test_collection(conn: "openeo.Connection", collection_id: str) -> bool:
    try:
        _ = conn.load_collection(collection_id)
        log_result("SUCCESS", f"collection: {collection_id}")
        return True
    except Exception:
        log_result("FAILURE", f"collection: {collection_id}")
        return False

def main():
    backend = os.getenv("OPENEO_BACKEND", "https://openeo.cloud")
    try:
        conn = openeo.connect(backend)
    except Exception as e:
        log_result("FAILURE", "connect failed")
        return

    if not authenticate(conn):
        log_result("FAILURE", "auth failed")
        return

    cid = get_random_collection(conn)
    if cid:
        test_collection(conn, cid)
    else:
        log_result("FAILURE", "no collection found")

if __name__ == "__main__":
    main()
