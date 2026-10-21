"""Convenience runner to start EarlyCare FastAPI backend service."""
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = ROOT_DIR / "backend" / ".venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)

if __name__ == "__main__":
    cmd = [
        str(VENV_PYTHON),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
    ] + sys.argv[1:]
    subprocess.run(cmd, cwd=str(ROOT_DIR / "backend"))
