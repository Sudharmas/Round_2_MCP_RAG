import chromadb
from chromadb.utils import embedding_functions
import os

# 1. Setup Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_folder = os.path.join(project_root, "vector_db")

# 2. Connect to Database
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=db_folder)

specs_col = chroma_client.get_collection(name="tech_specs", embedding_function=ef)
context_col = chroma_client.get_collection(name="product_context", embedding_function=ef)


def search_database(query, product_filter=None):
    print(f"\n🔍 RAG Search: '{query}' | Filter: {product_filter}")

    where_filter = {"product": product_filter} if product_filter else None

    # Query Database (Fetch top 10 to ensure we catch relevant data)
    spec_results = specs_col.query(query_texts=[query], n_results=10, where=where_filter)
    ctx_results = context_col.query(query_texts=[query], n_results=10, where=where_filter)

    found_content = []

    # Threshold for relevance (1.5 is safe for MiniLM)
    STRICT_THRESHOLD = 1.5

    # Collect Specs
    if spec_results['documents'][0]:
        for doc, dist in zip(spec_results['documents'][0], spec_results['distances'][0]):
            if dist < STRICT_THRESHOLD:
                found_content.append(f"[SPEC] {doc}")

    # Collect Context
    if ctx_results['documents'][0]:
        for doc, dist in zip(ctx_results['documents'][0], ctx_results['distances'][0]):
            if dist < STRICT_THRESHOLD:
                found_content.append(f"[CTX] {doc}")

    if not found_content:
        return "no details about this product"

    return "\n\n".join(found_content)