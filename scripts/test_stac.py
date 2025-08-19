#!/usr/bin/env python3
# tests/stac/test_stac_e2e.py

import os
import sys
import requests
from datetime import datetime
from typing import Tuple, Optional

STAC_URL   = os.getenv("STAC_BASE_URL", "https://dev.stac.eodc.eu/api/v1")
LOG_DIR    = "results/logs"
LOGFILE    = os.path.join(LOG_DIR, "test_stac.log")  

TIMEOUT_SECS          = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_COLLECTIONS_CHECK = int(os.getenv("MAX_COLLECTIONS_CHECK", "50"))
DOWN_THRESHOLD_COUNT  = int(os.getenv("DOWN_THRESHOLD_COUNT", "3"))
DOWN_THRESHOLD_RATIO  = float(os.getenv("DOWN_THRESHOLD_RATIO", "0.5")) 
ECHO_TO_STDOUT        = os.getenv("ECHO_TO_STDOUT", "1") == "1"

def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_line(status: str, message: str = ""):
    """
    Exaktes Format für den Parser:
    YYYY-MM-DD HH:MM:SS, SUCCESS|FAILURE, <message>
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    line = f"{now_ts()}, {status}, {message}"
    if ECHO_TO_STDOUT:
        print(line, flush=True)
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def get_json(url: str) -> dict:
    r = requests.get(url, timeout=TIMEOUT_SECS)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {}

def check_item_for_collection(base: str, col_id: str) -> Tuple[bool, Optional[str]]:
    base = base.rstrip("/")

    get_json(f"{base}/collections/{col_id}")  
    try:
        d = get_json(f"{base}/collections/{col_id}/items?limit=1")
        feats = d.get("features", [])
        if feats:
            return True, feats[0].get("id", "unknown")
        else:
            return True, "none"
    except Exception:
        return True, "none (items request failed)"

def main() -> int:
    try:
        data = get_json(f"{STAC_URL.rstrip('/')}/collections")
        collections = data.get("collections", [])
    except Exception:
        log_line("FAILURE", "endpoint: /collections not reachable")
        return 2

    if not collections:
        log_line("SUCCESS", "endpoint: /collections reachable, collections: 0")
        return 0

    collections = collections[:MAX_COLLECTIONS_CHECK]

    not_callable_count = 0
    checked = 0

    for col in collections:
        checked += 1
        col_id = col.get("id", "<unknown>")
        try:
            ok, item_note = check_item_for_collection(STAC_URL, col_id)
            if ok:
                log_line("SUCCESS", f"collection: {col_id}, item: {item_note}")
            else:
                not_callable_count += 1
                log_line("FAILURE", f"collection: {col_id}, reason: collection endpoint not reachable")
        except Exception:
            not_callable_count += 1
            log_line("FAILURE", f"collection: {col_id}, reason: collection endpoint not reachable")

    ratio = (not_callable_count / checked) if checked else 0.0
    if (not_callable_count >= DOWN_THRESHOLD_COUNT) or (ratio >= DOWN_THRESHOLD_RATIO):
        return 1
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        try:
            log_line("FAILURE", f"unexpected error")
        finally:
            sys.exit(3)
