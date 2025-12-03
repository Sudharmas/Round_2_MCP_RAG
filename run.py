import subprocess
import sys
import time
import os
import signal

# Define the paths to your servers
current_dir = os.path.dirname(os.path.abspath(__file__))
main_api_path = os.path.join(current_dir, "main.py")
mcp_server_path = os.path.join(current_dir, "mcp", "server.py")

processes = []


def signal_handler(sig, frame):
    print("\n\n🛑 Shutting down all Agentic Services...")
    for p in processes:
        p.terminate()
    sys.exit(0)


# Listen for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

print("=" * 60)
print("🚀 STARTING AGENTIC AI SYSTEM")
print("=" * 60)

try:
    # 1. Start Main Brain (RAG + CAG + UI) on Port 8000
    print(f"🔹 Launching Main Brain & UI (Port 8000)...")
    p1 = subprocess.Popen([sys.executable, main_api_path])
    processes.append(p1)

    # 2. Start MCP Server (External Tools) on Port 8001
    print(f"🔹 Launching MCP Server (Port 8001)...")
    p2 = subprocess.Popen([sys.executable, mcp_server_path])
    processes.append(p2)

    print("\n✅ System Online!")
    print("👉 UI & Chat:   http://127.0.0.1:8000")
    print("👉 API Docs:    http://127.0.0.1:8000/docs")
    print("👉 MCP Info:    http://127.0.0.1:8001/mcp/tools")
    print("\n(Press Ctrl+C to stop everything)")

    # Keep the script running to monitor processes
    p1.wait()
    p2.wait()

except Exception as e:
    print(f"❌ Error: {e}")
    for p in processes:
        p.terminate()