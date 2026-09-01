import threading
import time
import urllib.request
import json
import sys
import os

# add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app

def run_server():
    # Run on a different port just to test without conflict
    app.run(port=5002, use_reloader=False)

threading.Thread(target=run_server, daemon=True).start()
time.sleep(2) # wait for server to start

try:
    response = urllib.request.urlopen('http://localhost:5002/api/opportunities')
    data = json.loads(response.read())
    print("API returned", len(data), "items.")
    if len(data) > 0:
        print("First item:", json.dumps(data[0], indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()

