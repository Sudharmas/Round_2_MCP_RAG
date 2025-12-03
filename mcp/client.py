import requests
import json

SERVER_URL = "http://127.0.0.1:8001"

def test_mcp_flow():
    print("\n--- 1. Discovering Tools ---")
    try:
        response = requests.get(f"{SERVER_URL}/mcp/tools")
        tools = response.json()['tools']
        print(f"✅ Found {len(tools)} tools:")
        for t in tools:
            print(f"   - {t['name']}: {t['description']}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    print("\n--- 2. Testing Tool: search_manuals (RAG) ---")
    payload_rag = {
        "name": "search_manuals",
        "arguments": {
            "query": "What is the input voltage?",
            "product": "EX-1280"
        }
    }
    resp_rag = requests.post(f"{SERVER_URL}/mcp/call", json=payload_rag)
    print("Answer:", resp_rag.json()['content'][0]['text'][:200] + "...")

    print("\n--- 3. Testing Tool: get_full_context (CAG) ---")
    payload_cag = {
        "name": "get_full_context",
        "arguments": {
            "product": "EX-1280"
        }
    }
    resp_cag = requests.post(f"{SERVER_URL}/mcp/call", json=payload_cag)
    content = resp_cag.json()['content'][0]['text']
    print(f"Answer: Received {len(content)} chars of full context.")

if __name__ == "__main__":
    test_mcp_flow()