# quartz_sync.py
import os
import sys
import shutil
import subprocess

def to_posix(path: str) -> str:
    # Convert "C:\foo\bar" -> "/c/foo/bar" for Git Bash
    drive, rest = os.path.splitdrive(os.path.abspath(path))
    drive_letter = drive.rstrip(":").lower()
    return f"/{drive_letter}{rest.replace('\\', '/')}"

def stream(cmd, env=None):
    print(f"[INFO] Running: {' '.join(cmd)}\n")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="")
        proc.wait()
        return proc.returncode
    except FileNotFoundError as e:
        print(f"[ERROR] Command not found: {e}")
        return 127
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_dir)
    print(f"[INFO] Working dir: {repo_dir}")

    # Locate npx
    npx = shutil.which("npx")
    if npx is None:
        # Common Windows installs
        candidates = [
            r"C:\Program Files\nodejs\npx.cmd",
            r"C:\Program Files (x86)\nodejs\npx.cmd",
            os.path.expandvars(r"%USERPROFILE%\AppData\Roaming\npm\npx.cmd"),
        ]
        for p in candidates:
            if os.path.exists(p):
                npx = p
                break

    # Locate git (to decide whether to use Git Bash)
    git = shutil.which("git")

    # Locate Git Bash
    bash = None
    for p in [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        os.path.expandvars(r"%LocalAppData%\Programs\Git\bin\bash.exe"),
    ]:
        if os.path.exists(p):
            bash = p
            break

    if npx is None:
        print("\n[ERROR] 'npx' was not found.")
        print("        Install Node.js, or add npx to your PATH.")
        input("\nPress Enter to close...")
        sys.exit(1)

    print(f"[INFO] npx: {npx}")
    print(f"[INFO] git: {git or 'not on PATH'}")
    print(f"[INFO] Git Bash: {bash or 'not found'}\n")

    # Prefer direct npx. If git is missing but Git Bash exists, run inside bash.
    if git is None and bash is not None:
        posix_dir = to_posix(repo_dir)
        cmd = [bash, "--login", "-i", "-lc", f"cd '{posix_dir}' && npx quartz sync"]
    else:
        cmd = [npx, "quartz", "sync"]

    code = stream(cmd)
    print(f"\n[INFO] Exit code: {code}")
    input("\nPress Enter to close...")
    sys.exit(code)

if __name__ == "__main__":
    main()
