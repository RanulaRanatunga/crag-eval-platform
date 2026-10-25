import sys
import io
import time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import phoenix as px

if __name__ == "__main__":
    session = px.launch_app(port=6006)
    print("Phoenix UI is running at http://localhost:6006")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping Phoenix...")
