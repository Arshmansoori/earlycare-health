"""Convenience runner to run EarlyCare backend pytest test suite."""
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
VENV_PYTEST = ROOT_DIR / "backend" / ".venv" / "Scripts" / "pytest.exe"
if not VENV_PYTEST.exists():
    VENV_PYTEST = ROOT_DIR / "backend" / ".venv" / "Scripts" / "python.exe"
    cmd = [str(VENV_PYTEST), "-m", "pytest", "tests/", "-v"] + sys.argv[1:]
else:
    cmd = [str(VENV_PYTEST), "tests/", "-v"] + sys.argv[1:]

if __name__ == "__main__":
    result = subprocess.run(cmd, cwd=str(ROOT_DIR / "backend"))
    sys.exit(result.returncode)
