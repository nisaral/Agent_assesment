import subprocess
import os
import sys
import time

def run_service(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def main():
    project_dir = r"C:\Users\nisar\OneDrive\Desktop\vs1\proposal\AI_agent\finance-assistant"
    os.chdir(project_dir)

    # Activate virtual environment
    activate_cmd = r".\venv\Scripts\activate"
    python_path = f"$env:PYTHONPATH='{project_dir}'"

    services = [
        f"{python_path}; uvicorn agents.api_agent:app --port 8001",
        f"{python_path}; uvicorn agents.scraping_agent:app --port 6002",
        f"{python_path}; uvicorn agents.retriever_agent:app --port 6003",
        f"{python_path}; uvicorn agents.analysis_agent:app --port 6004",
        f"{python_path}; uvicorn agents.language_agent:app --port 6005",
        f"{python_path}; uvicorn agents.voice_agent:app --port 6006",
        f"{python_path}; uvicorn orchestrator.workflow:app --port 6007"
    ]

    processes = []
    for cmd in services:
        full_cmd = f"{activate_cmd} && {cmd}"
        process = run_service(full_cmd)
        processes.append(process)
        time.sleep(2)  # Stagger starts to avoid port conflicts

    print("All services started. Press Ctrl+C to stop.")
    try:
        while True:
            for process in processes:
                if process.poll() is not None:
                    print(f"Service {process.args} exited with code {process.returncode}")
                    return
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all services...")
        for process in processes:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    main()