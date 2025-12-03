# # import os
# # import uvicorn
# # import google.generativeai as genai
# # import chromadb
# # from fastapi import FastAPI, HTTPException
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.responses import FileResponse
# # from pydantic import BaseModel
# # from dotenv import load_dotenv
# # from langsmith import traceable
# #
# # # Import Tools
# # from rag.retrieve import search_database
# # from cag.loader import load_product_context
# #
# # load_dotenv(override=True)
# #
# # genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# # model = genai.GenerativeModel('gemini-2.5-flash')
# #
# # app = FastAPI(title="Agentic RAG + CAG Server")
# # app.mount("/static", StaticFiles(directory="static"), name="static")
# #
# # # DB Connection for scanning
# # current_dir = os.path.dirname(os.path.abspath(__file__))
# # db_folder = os.path.join(current_dir, "vector_db")
# # client = chromadb.PersistentClient(path=db_folder)
# # specs_col = client.get_or_create_collection("tech_specs")
# #
# #
# # def get_known_products():
# #     products = set()
# #     try:
# #         data = specs_col.get(include=['metadatas'])
# #         for m in data['metadatas']:
# #             if m and 'product' in m: products.add(m['product'])
# #     except:
# #         pass
# #     return list(products)
# #
# #
# # @app.get("/")
# # async def read_root():
# #     return FileResponse('static/index.html')
# #
# #
# # class QueryRequest(BaseModel):
# #     question: str
# #     product_filter: str
# #     mode: str = "auto"
# #
# #
# # @traceable(name="Gemini Generation")
# # def generate_answer(prompt):
# #     return model.generate_content(prompt).text.strip()
# #
# #
# # @traceable(name="Agent Router")
# # @app.post("/ask")
# # async def ask_agent(request: QueryRequest):
# #     print(f"\n🤖 Agent received: '{request.question}' | Filter: {request.product_filter}")
# #
# #     # --- STEP 0: NAME OVERRIDE (Keep this, it's good for known products) ---
# #     known_products = get_known_products()
# #     for prod in known_products:
# #         clean_prod = prod.lower().replace("-", "")
# #         clean_query = request.question.lower().replace("-", "")
# #         if clean_prod in clean_query and prod != request.product_filter:
# #             print(f"✨ SMART AGENT: Overriding filter to '{prod}'")
# #             request.product_filter = prod
# #             break
# #
# #     context_text = ""
# #     used_mode = request.mode
# #
# #     # --- ROUTER LOGIC ---
# #
# #     if request.mode == "cag":
# #         context_text = load_product_context(request.product_filter)
# #         if not context_text: return {"answer": "Product not found.", "mode_used": "error"}
# #
# #     elif request.mode == "rag":
# #         context_text = search_database(request.question, request.product_filter)
# #
# #     elif request.mode == "auto":
# #         if any(w in request.question.lower() for w in ["summarize", "explain", "overview"]):
# #             used_mode = "cag_summary"
# #             context_text = load_product_context(request.product_filter)
# #         else:
# #             # 1. Try RAG with Filter
# #             print(f"🔀 Router: Trying RAG for {request.product_filter}...")
# #             context_text = search_database(request.question, request.product_filter)
# #             used_mode = "rag"
# #
# #             # 2. Smart Escalation (CAG)
# #             if not context_text or context_text == "no details about this product":
# #                 print(f"⚠️ RAG missed data. Escalating to Deep Search (CAG)...")
# #                 full_context = load_product_context(request.product_filter)
# #                 if full_context:
# #                     context_text = full_context
# #                     used_mode = "cag_fallback"
# #
# #             # 3. GLOBAL FALLBACK (The Fix!)
# #             # If we still found nothing, maybe the user is asking about a product in a DIFFERENT file.
# #             # We search the ENTIRE database (Filter = None).
# #             if not context_text or context_text == "no details about this product":
# #                 print(f"🌍 Scope Failure. Trying GLOBAL SEARCH (Ignoring filter)...")
# #                 # Passing None removes the filter
# #                 global_result = search_database(request.question, None)
# #
# #                 if global_result and global_result != "no details about this product":
# #                     print("✅ Global Search found data!")
# #                     context_text = global_result
# #                     used_mode = "global_rag"
# #
# #     # --- GENERATION ---
# #     if not context_text or context_text == "no details about this product":
# #         return {"answer": "I cannot find this information.", "mode_used": used_mode}
# #
# #     prompt = f"""
# #     You are a technical expert.
# #     Context: {context_text[:50000]}
# #     User Question: {request.question}
# #     INSTRUCTIONS: Answer strictly based on the Context.
# #     """
# #
# #     try:
# #         final_answer = generate_answer(prompt)
# #         return {
# #             "answer": final_answer,
# #             "mode_used": used_mode,
# #             "context_preview": context_text[:200]
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))
# #
# #
# # if __name__ == "__main__":
# #     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
#
#
# import os
# import uvicorn
# import google.generativeai as genai
# import chromadb
# from fastapi import FastAPI, HTTPException
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from langsmith import traceable
#
# # Import Tools
# from rag.retrieve import search_database
# from cag.loader import load_product_context
#
# load_dotenv(override=True)
#
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# model = genai.GenerativeModel('gemini-2.5-flash')
#
# app = FastAPI(title="Agentic RAG + CAG Server")
# app.mount("/static", StaticFiles(directory="static"), name="static")
#
# # DB Connection for scanning
# current_dir = os.path.dirname(os.path.abspath(__file__))
# db_folder = os.path.join(current_dir, "vector_db")
# client = chromadb.PersistentClient(path=db_folder)
# specs_col = client.get_or_create_collection("tech_specs")
#
#
# def get_known_products():
#     products = set()
#     try:
#         data = specs_col.get(include=['metadatas'])
#         for m in data['metadatas']:
#             if m and 'product' in m: products.add(m['product'])
#     except:
#         pass
#     return list(products)
#
#
# @app.get("/")
# async def read_root():
#     return FileResponse('static/index.html')
#
#
# class QueryRequest(BaseModel):
#     question: str
#     product_filter: str
#     mode: str = "auto"
#
#
# @traceable(name="Gemini Generation")
# def generate_answer(prompt):
#     return model.generate_content(prompt).text.strip()
#
#
# @traceable(name="Agent Router")
# @app.post("/ask")
# async def ask_agent(request: QueryRequest):
#     print(f"\n🤖 Agent received: '{request.question}' | Filter: {request.product_filter}")
#
#     known_products = get_known_products()
#     clean_query = request.question.lower().replace("-", "")
#
#     # --- INTELLIGENT COMPARISON DETECTION (The Fix) ---
#
#     # 1. Count how many products are mentioned in the query
#     mentioned_products = []
#     for prod in known_products:
#         clean_prod = prod.lower().replace("-", "")
#         if clean_prod in clean_query:
#             mentioned_products.append(prod)
#
#     # 2. Check for Comparison Keywords
#     is_comparison = any(w in clean_query for w in ["compare", "vs", "difference", "different", "both", "between"])
#
#     # 3. Decision Logic
#     if len(mentioned_products) > 1 or is_comparison:
#         print(f"⚔️ COMPARISON DETECTED: {mentioned_products}")
#         print("🔓 DISABLING FILTER -> GLOBAL SEARCH MODE")
#         request.product_filter = None  # <--- CRITICAL: Remove filter to see ALL products
#
#     elif len(mentioned_products) == 1:
#         # Single product mentioned -> Smart Override
#         if mentioned_products[0] != request.product_filter:
#             print(f"✨ SMART OVERRIDE: Switching filter to '{mentioned_products[0]}'")
#             request.product_filter = mentioned_products[0]
#
#     # --- STANDARD ROUTER LOGIC ---
#     context_text = ""
#     used_mode = request.mode
#
#     if request.mode == "cag" and request.product_filter:
#         context_text = load_product_context(request.product_filter)
#
#     elif request.mode == "rag":
#         context_text = search_database(request.question, request.product_filter)
#
#     elif request.mode == "auto":
#         if any(w in clean_query for w in ["summarize", "explain", "overview"]) and request.product_filter:
#             used_mode = "cag_summary"
#             context_text = load_product_context(request.product_filter)
#         else:
#             # 1. Try RAG (Global or Filtered)
#             print(f"🔀 Router: Searching DB (Filter: {request.product_filter})...")
#             context_text = search_database(request.question, request.product_filter)
#             used_mode = "rag"
#
#             # 2. Smart Escalation (If filter was active but failed)
#             if (not context_text or "no details" in context_text) and request.product_filter:
#                 print(f"⚠️ Filtered Search failed. Escalating to Global Search...")
#                 context_text = search_database(request.question, None)  # Try Global
#                 used_mode = "rag_global_fallback"
#
#     # --- GENERATION ---
#     if not context_text or context_text == "no details about this product":
#         return {"answer": "I cannot find this information.", "mode_used": used_mode}
#
#     prompt = f"""
#     You are a technical expert.
#
#     Context:
#     {context_text[:50000]}
#
#     User Question: {request.question}
#
#     INSTRUCTIONS:
#     1. Answer strictly based on the Context.
#     2. If comparing two products, explicitly state the specs for BOTH.
#     3. If one product is missing from the context, state "I have data for [Product A] but not [Product B]."
#     """
#
#     try:
#         final_answer = generate_answer(prompt)
#         return {
#             "answer": final_answer,
#             "mode_used": used_mode,
#             "context_preview": context_text[:200]
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


import os
import uvicorn
import google.generativeai as genai
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from langsmith import traceable

from rag.retrieve import search_database
from cag.loader import load_product_context

load_dotenv(override=True)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI(title="Agentic RAG + CAG Server")
app.mount("/static", StaticFiles(directory="static"), name="static")

# DB Scan for Product Detection
current_dir = os.path.dirname(os.path.abspath(__file__))
client = chromadb.PersistentClient(path=os.path.join(current_dir, "vector_db"))
specs_col = client.get_or_create_collection("tech_specs")


def get_known_products():
    """Returns list of products currently in the DB"""
    products = set()
    try:
        data = specs_col.get(include=['metadatas'])
        for m in data['metadatas']:
            if m and 'product' in m: products.add(m['product'])
    except:
        pass
    return list(products)


@app.get("/")
async def read_root():
    return FileResponse('static/index.html')


class QueryRequest(BaseModel):
    question: str
    product_filter: Optional[str] = None  # Optional now
    mode: str = "auto"


@traceable(name="Gemini Generation")
def generate_answer(prompt):
    return model.generate_content(prompt).text.strip()


@traceable(name="Agent Router")
@app.post("/ask")
async def ask_agent(request: QueryRequest):
    print(f"\n🤖 Agent received: '{request.question}'")

    # --- 1. PRODUCT DETECTION ENGINE ---
    # We ignore the frontend filter (it's null) and derive it from the question.
    known_products = get_known_products()
    found_in_query = []

    clean_query = request.question.lower().replace("-", "").replace(" ", "")

    for prod in known_products:
        clean_prod = prod.lower().replace("-", "").replace(" ", "")
        if clean_prod in clean_query:
            found_in_query.append(prod)

    # --- 2. INTELLIGENT FILTERING LOGIC ---
    active_filter = None

    if len(found_in_query) == 0:
        print("🌍 No specific product detected -> GLOBAL SEARCH (All Products)")
        active_filter = None

    elif len(found_in_query) == 1:
        print(f"🎯 Detected Product: '{found_in_query[0]}' -> SPECIFIC FILTER")
        active_filter = found_in_query[0]

    else:
        print(f"⚔️ Comparison Detected ({found_in_query}) -> GLOBAL SEARCH")
        active_filter = None  # Comparison means we need ALL data

    # --- 3. ROUTER & RETRIEVAL ---
    context_text = ""
    used_mode = request.mode

    # Auto Mode Logic
    if request.mode == "auto":
        # Check for Summary Intent
        if any(w in request.question.lower() for w in ["summarize", "explain", "overview"]):
            if active_filter:
                # Summary of ONE product -> CAG
                print("📖 Summary Intent -> CAG Mode")
                used_mode = "cag_summary"
                context_text = load_product_context(active_filter)
            else:
                # Summary of EVERYTHING? -> RAG (CAG is too heavy for all products)
                print("📖 Broad Summary -> RAG Mode")
                used_mode = "rag_broad"
                context_text = search_database(request.question, None)
        else:
            # Standard Question
            print(f"🔍 Searching DB (Filter: {active_filter})...")
            context_text = search_database(request.question, active_filter)
            used_mode = "rag"

            # Escalation: If Specific Filter failed, try Global
            if (not context_text or "no details" in context_text) and active_filter:
                print("⚠️ Specific search failed. Retrying GLOBAL search...")
                context_text = search_database(request.question, None)
                used_mode = "rag_fallback_global"

    # Direct Modes (if user forces them via dropdown)
    elif request.mode == "cag":
        if active_filter:
            context_text = load_product_context(active_filter)
        else:
            # Cannot CAG without a specific product
            return {"answer": "For Deep Reading (CAG), please mention a specific product name in your question.",
                    "mode_used": "error"}

    elif request.mode == "rag":
        context_text = search_database(request.question, active_filter)

    # --- 4. ANSWER GENERATION ---
    if not context_text or context_text == "no details about this product":
        return {"answer": "I scanned the database but could not find information relevant to your query.",
                "mode_used": used_mode}

    prompt = f"""
    You are a technical expert.

    Context from Database:
    {context_text[:50000]} 

    User Question: {request.question}

    INSTRUCTIONS:
    1. Answer strictly based on the provided Context.
    2. If the user asked about a product not in the context, say "I don't have data on that."
    3. If comparing, list specs for all mentioned products clearly.
    """

    try:
        final_answer = generate_answer(prompt)
        return {
            "answer": final_answer,
            "mode_used": used_mode,
            "context_preview": context_text[:200]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)