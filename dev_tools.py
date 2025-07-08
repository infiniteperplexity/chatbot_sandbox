import subprocess
import os
import signal

def kill_chainlit_processes():
    """Don't blame me, Copilot wrote this."""
    try:
        # Use pgrep to find Chainlit processes more safely
        result = subprocess.run(['pgrep', '-f', 'chainlit run'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            current_pid = os.getpid()  # Get current process PID to avoid killing ourselves          
            for pid_str in pids:
                if pid_str.strip():
                    pid = int(pid_str.strip())
                    # Don't kill the current process or its parent
                    if pid != current_pid and pid != os.getppid():
                        try:
                            print(f"Killing Chainlit process with PID: {pid}")
                            os.kill(pid, signal.SIGTERM)
                        except ProcessLookupError:
                            print(f"Process {pid} already terminated")
                        except PermissionError:
                            print(f"Permission denied to kill process {pid}")
        else:
            print("No existing Chainlit processes found")
    except FileNotFoundError:
        # If pgrep is not available, try pkill
        try:
            result = subprocess.run(['pkill', '-f', 'chainlit run'], capture_output=True, text=True)
            if result.returncode == 0:
                print("Killed existing Chainlit processes using pkill")
            elif result.returncode == 1:
                print("No existing Chainlit processes found")
            else:
                print(f"pkill returned error code: {result.returncode}")
        except FileNotFoundError:
            print("Neither pgrep nor pkill available - cannot kill existing processes")
    except Exception as e:
        print(f"Error while trying to kill Chainlit processes: {e}")


def launch_chainlit_app(app_path='app.py', kill_existing=True, headless=True):
    """Launch the Chainlit app with the specified path."""
    if not os.path.exists(app_path):
        print(f"App file {app_path} does not exist.")
        return
    if kill_existing:
        kill_chainlit_processes()
    
    print(f"Starting Chainlit app: {app_path}")
    print("App will be available at http://localhost:8000")
    if headless:
        print("Running in headless mode - browser will NOT open automatically")
    print("To stop the app, interrupt the kernel or restart it")
    print("=" * 50)
    
    # Add --headless flag to prevent automatic browser opening
    headless_flag = " --headless" if headless else ""
    command = f"cd {os.getcwd()} && chainlit-env/bin/python -m chainlit run {app_path} --host 0.0.0.0 --port 8000{headless_flag}"
    os.system(command)