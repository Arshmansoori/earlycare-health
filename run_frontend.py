"""Convenience runner to start EarlyCare Next.js frontend service."""
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"

if __name__ == "__main__":
    env = os.environ.copy()
    env["PATH"] = (
        r"C:\Program Files\nodejs;"
        r"C:\Users\arsh2\AppData\Local\Programs\Python\Python312;"
        r"C:\Users\arsh2\AppData\Local\Programs\Python\Python312\Scripts;"
        r"C:\Users\arsh2\AppData\Local\Programs\Git\cmd;"
        + env.get("PATH", "")
    )
    cmd = ["cmd.exe", "/c", "npm", "run", "dev"] + sys.argv[1:]
    subprocess.run(cmd, cwd=str(FRONTEND_DIR), env=env)
