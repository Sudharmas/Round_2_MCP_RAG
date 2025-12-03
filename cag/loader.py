import os
import re
import chromadb
from chromadb.utils import embedding_functions

# 1. Setup Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_folder = os.path.join(project_root, "vector_db")

print(f"🔌 CAG: Connecting to Database at: {db_folder}")

# 2. Connect to Database
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=db_folder)
specs_col = client.get_or_create_collection(name="tech_specs", embedding_function=ef)
context_col = client.get_or_create_collection(name="product_context", embedding_function=ef)


def clean_string(s):
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()


def load_product_context(product_filter):
    print(f"\n📥 CAG: Request for '{product_filter}'")

    # 1. Get List of All Products in DB
    available_products = set()
    try:
        data = specs_col.get(include=['metadatas'])
        for m in data['metadatas']:
            if m and 'product' in m: available_products.add(m['product'])

        # Also check context col to be safe
        data_ctx = context_col.get(include=['metadatas'])
        for m in data_ctx['metadatas']:
            if m and 'product' in m: available_products.add(m['product'])

    except Exception as e:
        print(f"⚠️ CAG Warning: Could not scan DB: {e}")

    available_list = list(available_products)
    print(f"🔎 DB Contains: {available_list}")

    matched_product = None
    target = clean_string(product_filter)

    # 2. STRATEGY A: Exact/Partial Name Match
    for db_name in available_list:
        if target in clean_string(db_name) or clean_string(db_name) in target:
            matched_product = db_name
            print(f"✅ Found Name Match: '{matched_product}'")
            break

    # 3. STRATEGY B: Global Keyword Search (The Fix!)
    # If name match failed, maybe 'DM8SE' is hidden INSIDE another manual (like DM6PE)
    if not matched_product:
        print(f"🕵️ Name match failed. Scanning content for '{product_filter}'...")

        # Query the vector DB for the keyword
        results = specs_col.query(query_texts=[product_filter], n_results=1)

        if results['metadatas'][0]:
            # Found a document mentioning it! Grab the product name from metadata.
            found_product = results['metadatas'][0][0].get('product')
            print(f"✅ Found keyword '{product_filter}' inside product '{found_product}'!")
            matched_product = found_product

    # 4. STRATEGY C: Emergency Fallback (Last Resort)
    if not matched_product and available_list:
        print(f"⚠️ Search failed. Defaulting to first available: '{available_list[0]}'")
        matched_product = available_list[0]

    if not matched_product:
        return None

    # 5. Load Data
    spec_dump = specs_col.get(where={"product": matched_product})
    ctx_dump = context_col.get(where={"product": matched_product})

    full_text = [f"--- DATA FOR {matched_product} ---"]
    if spec_dump['documents']:
        full_text.append("--- SPECS ---")
        full_text.extend(spec_dump['documents'])
    if ctx_dump['documents']:
        full_text.append("--- CONTEXT ---")
        full_text.extend(ctx_dump['documents'])

    return "\n\n".join(full_text)