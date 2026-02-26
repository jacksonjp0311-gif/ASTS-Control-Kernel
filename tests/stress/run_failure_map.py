import subprocess, sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

def run(script):
    print(">>", script)
    subprocess.check_call([sys.executable, script], cwd=os.path.dirname(__file__))

def main():
    run("sweep_alpha.py")
    run("sweep_drift_amp.py")
    run("sweep_threshold.py")

if __name__ == "__main__":
    main()
