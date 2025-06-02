import subprocess
import sys
import os
import time
from pathlib import Path
import logging
import psutil
import signal
import socket

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('services.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except socket.error:
            return True

def kill_process_on_port(port):
    try:
        cmd = f'netstat -ano | findstr ":{port}" | findstr "LISTENING"'
        output = subprocess.check_output(cmd, shell=True).decode()
        if output:
            pid = output.strip().split()[-1]
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                logger.info(f"Killed process on port {port}")
                return True
            except subprocess.CalledProcessError:
                logger.warning(f"Failed to kill process on port {port}")
        return False
    except subprocess.CalledProcessError:
        return False

def start_service(module, port, log_dir):
    if is_port_in_use(port):
        logger.warning(f"Port {port} is in use. Attempting to kill existing process...")
        if not kill_process_on_port(port):
            logger.error(f"Failed to free port {port}")
            return None

    log_file = os.path.join(log_dir, f"{module.replace('.', '_')}.log")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([os.getcwd(), env.get("PYTHONPATH", "")])
    
    cmd = [sys.executable, "-m", "uvicorn", f"{module}:app", "--host", "0.0.0.0", "--port", str(port)]
    
    try:
        with open(log_file, "w") as f:
            process = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            time.sleep(2)
            
            if process.poll() is None:
                logger.info(f"Started {module} on port {port}")
                return process
            else:
                logger.error(f"Service {module} failed to start")
                return None
    except Exception as e:
        logger.error(f"Failed to start {module}: {e}")
        return None

def main():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    services = [
        ("agents.api_agent", 8001),
        ("agents.scraping_agent", 6002),
        ("agents.retriever_agent", 6003),
        ("agents.analysis_agent", 6004),
        ("agents.language_agent", 6005),
        ("agents.voice_agent", 6006),
        ("orchestrator.workflow", 6007)
    ]
    
    processes = []
    for module, port in services:
        logger.info(f"Starting {module} on port {port}...")
        process = start_service(module, port, log_dir)
        if process:
            processes.append((module, port, process))
        else:
            logger.error(f"Failed to start {module}")
    
    if not processes:
        logger.error("No services were started successfully")
        return
    
    logger.info(f"Started {len(processes)} services")
    
    with open("service_ports.log", "w") as f:
        f.write("Service Ports:\n")
        for module, port, _ in processes:
            f.write(f"{module}: http://localhost:{port}\n")
    
    def signal_handler(signum, frame):
        logger.info("Stopping all services...")
        for module, port, process in processes:
            try:
                process.terminate()
                logger.info(f"Terminated {module}")
            except Exception as e:
                logger.error(f"Error stopping {module}: {e}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            for module, port, process in processes:
                if process.poll() is not None:
                    logger.error(f"{module} stopped unexpectedly")
                    signal_handler(None, None)
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
