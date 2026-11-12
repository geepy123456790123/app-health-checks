"""Check a public health endpoint and retain a daily status snapshot."""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HEALTH_URL = "https://samewhere.net/api/health"


def check():
    for attempt in range(4):
        try:
            response = subprocess.run(
                ["curl", "--fail", "--silent", "--show-error", "--max-time", "20", HEALTH_URL],
                check=True, capture_output=True, text=True,
            )
            payload = json.loads(response.stdout)
            if not isinstance(payload, dict) or payload.get("status") != "ok" or payload.get("release") != "production":
                raise ValueError("Unexpected health status or release")
            return "ok"
        except (OSError, ValueError, subprocess.SubprocessError):
            if attempt < 3:
                time.sleep(10)
    return "down"


def record(status, path=Path("status.json")):
    now = datetime.now(timezone.utc).isoformat()
    try:
        previous = json.loads(path.read_text())
    except (OSError, ValueError):
        previous = {}
    if previous.get("status") == status and str(previous.get("checked_at", ""))[:10] == now[:10]:
        return
    path.write_text(json.dumps({"service": "Samewhere", "status": status, "checked_at": now}, indent=2) + "\n")


if __name__ == "__main__":
    status = check()
    record(status)
    if status != "ok":
        print("::error::Samewhere production health failed after four attempts", file=sys.stderr)
        sys.exit(1)
    print("Samewhere production health: ok")
