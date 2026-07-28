from modules.startunit import StartTheProgram
from modules.progresswindow import run_with_progress
from modules import _global
import os

def main(): 
    if os.environ.get("AQUACROP_DEBUG_TRACE", "").strip():
        from modules.debugtrace import write_run_trace
        write_run_trace(_global.complete_path_dir)
    run_with_progress(StartTheProgram)

if __name__ == "__main__":
    main()
