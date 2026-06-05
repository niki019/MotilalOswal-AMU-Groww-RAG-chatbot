import os
import sys
import datetime

# Change working directory to the directory containing cron_job.py to prevent path errors
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir:
    os.chdir(script_dir)
if script_dir not in sys.path:
    sys.path.append(script_dir)

from ingestion import run_ingestion

def main():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "ingestion.log")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Redirect stdout and stderr to log file for tracking execution
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n--- Ingestion Run Started at {timestamp} ---\n")
        # Keep references to original streams
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        
        sys.stdout = f
        sys.stderr = f
        
        try:
            run_ingestion()
            print("Run completed successfully.")
        except Exception as e:
            print(f"Run failed with exception: {e}")
        finally:
            # Restore streams
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
            
if __name__ == "__main__":
    main()
