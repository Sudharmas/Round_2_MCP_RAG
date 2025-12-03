# import os
# import chromadb
# from docling.document_converter import DocumentConverter
# from chromadb.utils import embedding_functions
# from dotenv import load_dotenv
#
# # 1. Setup
# load_dotenv(override=True)
#
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)
# data_folder = os.path.join(project_root, "data")
# db_folder = os.path.join(project_root, "vector_db")
#
# # 2. Initialize Docling & Database
# converter = DocumentConverter()  # The "Smart" Free Extractor
#
# # Local Embeddings (Free)
# ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# chroma_client = chromadb.PersistentClient(path=db_folder)
#
# specs_col = chroma_client.get_or_create_collection(name="tech_specs", embedding_function=ef)
# context_col = chroma_client.get_or_create_collection(name="product_context", embedding_function=ef)
#
#
# def ingest_one_file(filename, product_name):
#     filepath = os.path.join(data_folder, filename)
#
#     if not os.path.exists(filepath):
#         print(f"❌ ERROR: File not found: {filepath}")
#         return
#
#     print(f"\n--- Processing: {product_name} using Docling ---")
#
#     # A. CONVERT PDF TO DOCUMENT OBJECT
#     # Docling analyzes layout, headers, tables, and text automatically.
#     result = converter.convert(filepath)
#     doc = result.document
#
#     # B. EXTRACT TABLES (Tech Specs)
#     print(f"   Found {len(doc.tables)} tables...")
#     for i, table in enumerate(doc.tables):
#         # Export table as Markdown format (clean & readable for LLM)
#         table_md = table.export_to_markdown()
#
#         specs_col.add(
#             documents=[table_md],
#             metadatas=[{"product": product_name, "type": "spec", "source": "table"}],
#             ids=[f"{product_name}_tbl_{i}"]
#         )
#
#     # C. EXTRACT TEXT SENTENCES (Context)
#     # We iterate through the 'body' text items
#     print("   Extracting Text Context...")
#     text_chunks = []
#
#     for item in doc.texts:
#         # Only keep actual paragraphs, skip tiny headers/labels
#         if isinstance(item.text, str) and len(item.text) > 40:
#             text_chunks.append(item.text)
#
#     # Group sentences into larger context chunks (e.g., 3 paragraphs at a time)
#     chunk_size = 3
#     for i in range(0, len(text_chunks), chunk_size):
#         chunk = "\n\n".join(text_chunks[i:i + chunk_size])
#
#         context_col.add(
#             documents=[chunk],
#             metadatas=[{"product": product_name, "type": "context"}],
#             ids=[f"{product_name}_text_{i}"]
#         )
#
#     print(f"✅ Finished {product_name}")
#
#
# # --- EXECUTION ---
# if __name__ == "__main__":
#     files_to_ingest = [
#         {"filename": "tds_ControlSpace_EX-1280_LTR_enUS.pdf", "product_name": "EX-1280"},
#         {"filename": "TDS_ControlSpace_EX-1280C_LTR_enUS-2.pdf", "product_name": "EX-1280C"},
#         {"filename": "DM6PE.pdf", "product_name": "DM6PE_ltr"},
#         {"filename": "DM8SE.pdf", "product_name": "DM8SE_a4"},
#     ]
#
#     for file_info in files_to_ingest:
#         ingest_one_file(file_info["filename"], file_info["product_name"])
import os
import hashlib
import chromadb
import nest_asyncio
from llama_parse import LlamaParse
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# 1. SETUP
load_dotenv(override=True)
nest_asyncio.apply()  # Required for LlamaParse to run in scripts

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_folder = os.path.join(project_root, "data")
db_folder = os.path.join(project_root, "vector_db")

# Initialize LlamaParse (The "Vision" Parser)
print("🚀 Initializing LlamaParse (Online Table Extractor)...")
parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    result_type="markdown",  # Forces tables to be Markdown formatted
    verbose=True,
    language="en"
)

print("🔌 Connecting to Vector Database...")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=db_folder)

specs_col = chroma_client.get_or_create_collection(name="tech_specs", embedding_function=ef)
context_col = chroma_client.get_or_create_collection(name="product_context", embedding_function=ef)


def generate_id(content, product, suffix):
    raw = f"{product}_{content[:30]}_{suffix}"
    return hashlib.md5(raw.encode()).hexdigest()


def ingest_one_file(filename, product_name):
    filepath = os.path.join(data_folder, filename)
    if not os.path.exists(filepath):
        print(f"❌ ERROR: File not found: {filepath}")
        return

    print(f"\n--- Processing: {product_name} via LlamaCloud ---")

    # 1. PARSE DOCUMENT (Uploads to LlamaCloud for AI processing)
    # This might take 5-10 seconds per file but the result is superior
    try:
        documents = parser.load_data(filepath)
    except Exception as e:
        print(f"❌ LlamaParse Failed: {e}")
        return

    # 2. PROCESS CHUNKS
    # LlamaParse returns the whole doc as highly structured Markdown
    # We split it by headers to keep sections together

    full_text = documents[0].text

    # Simple strategy: Split by double newlines to isolate paragraphs and tables
    # Markdown tables usually stay together as a block
    chunks = full_text.split("\n\n")

    print(f"   Received {len(chunks)} structured chunks.")

    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 20: continue  # Skip empty noise

        # 3. DETECT & ROUTE TABLES
        # Markdown tables start with pipes |
        if "|" in chunk and "---" in chunk:
            print(f"   Found Table/Spec chunk (Index {i})")

            stamped_content = f"Product Model: {product_name}\nType: Specification Table\n\n{chunk}"

            specs_col.upsert(
                documents=[stamped_content],
                metadatas=[{"product": product_name, "type": "spec", "source": "llamaparse_table"}],
                ids=[generate_id(chunk, product_name, f"lp_tbl_{i}")]
            )

        # 4. ROUTE NARRATIVE TEXT
        else:
            stamped_content = f"Product Model: {product_name}\nType: Context\n\n{chunk}"

            context_col.upsert(
                documents=[stamped_content],
                metadatas=[{"product": product_name, "type": "context", "source": "llamaparse_text"}],
                ids=[generate_id(chunk, product_name, f"lp_txt_{i}")]
            )

    print(f"✅ Finished {product_name}")


if __name__ == "__main__":
    files_to_ingest = [
        {"filename": "tds_ControlSpace_EX-1280_LTR_enUS.pdf", "product_name": "EX-1280"},
        {"filename": "TDS_ControlSpace_EX-1280C_LTR_enUS-2.pdf", "product_name": "EX-1280C"},
        {"filename": "DM8SE.pdf", "product_name": "DM8SE"},
        {"filename": "DM6PE.pdf", "product_name": "DM6PE"},
        # {"filename": "DM8SE.pdf",  "product_name": "DM8SE"},
    ]

    print(f"Queue: {len(files_to_ingest)} documents.")
    for f in files_to_ingest:
        ingest_one_file(f["filename"], f["product_name"])