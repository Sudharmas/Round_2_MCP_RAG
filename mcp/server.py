import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- CRITICAL PATH FIX ---
# This allows us to import 'rag' and 'cag' from the folder above
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import your LOCKED working modules
from rag.retrieve import search_database
from cag.loader import load_product_context

app = FastAPI(title="Agentic MCP Server")

# 1. Define the Tools Schema
# This tells other Agents exactly what arguments we need
MCP_TOOLS = [
    {
        "name": "search_manuals",
        "description": "Searches for specific technical facts (voltage, weight, errors) in product documentation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The technical question"},
                "product": {"type": "string", "description": "The product model (e.g., EX-1280)"}
            },
            "required": ["query", "product"]
        }
    },
    {
        "name": "get_full_context",
        "description": "Retrieves the full product manual for summarization or deep analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "The product model (e.g., EX-1280)"}
            },
            "required": ["product"]
        }
    }
]


# 2. Endpoint: List Tools (Discovery)
@app.get("/mcp/tools")
async def list_tools():
    return {"tools": MCP_TOOLS}


# 3. Endpoint: Call Tool (Execution)
class ToolCall(BaseModel):
    name: str
    arguments: dict


@app.post("/mcp/call")
async def call_tool(request: ToolCall):
    print(f"📞 MCP Call Received: {request.name} | Args: {request.arguments}")

    # TOOL A: RAG Search
    if request.name == "search_manuals":
        query = request.arguments.get("query")
        product = request.arguments.get("product")

        result = search_database(query, product)

        # Format strictly for MCP (text content)
        return {
            "content": [
                {"type": "text", "text": result}
            ]
        }

    # TOOL B: CAG Context Dump
    elif request.name == "get_full_context":
        product = request.arguments.get("product")

        # Uses your "Fail-Safe" loader
        result = load_product_context(product)

        if not result:
            return {"content": [{"type": "text", "text": "Product not found."}]}

        return {
            "content": [
                {"type": "text", "text": result[:50000]}  # Limit to prevent timeouts
            ]
        }

    else:
        raise HTTPException(status_code=404, detail="Tool not found")


# Run on Port 8001 (Distinct from Main API)
if __name__ == "__main__":
    print("🚀 MCP Server starting on Port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)