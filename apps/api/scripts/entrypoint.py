"""Container entrypoint: migrate DB, then start uvicorn."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    print("Running database migrations...", flush=True)
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    reload = os.getenv("UVICORN_RELOAD", "true").lower() in {"1", "true", "yes"}
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    if reload:
        cmd.append("--reload")

    print(f"Starting: {' '.join(cmd)}", flush=True)
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Migration failed with exit code {exc.returncode}", file=sys.stderr)
        sys.exit(exc.returncode)
