import os
import hashlib
import json
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import pypdf  

from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Suppress the Windows symlink warning noise completely
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "true"

# ==========================================
# 1. PATH RESOLUTION & SETUP
# ==========================================
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent 
load_dotenv(project_root / ".env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env")

# Set up clean production data cache path
cache_dir = project_root / "data" / "cache"
cache_dir.mkdir(parents=True, exist_ok=True)
# HASH_CACHE_FILE = cache_dir / "ingestion_hash_cache.json"


# ==========================================
# 2. DYNAMIC ENVIRONMENT ROUTING
# ==========================================
EMBEDDINGS_MODEL_SETTING = os.getenv("Embeddings_model", "LOCAL").strip().upper()
# if Embeddings_model is not provided then will go for local
if EMBEDDINGS_MODEL_SETTING == "OPENROUTER":
    print("🤖 Mode: Utilizing Cloud OpenAI Embeddings (1536 Dim)...")
    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    INDEX_NAME = "fde-sop-index-openrouter"  # Isolated OpenAI Index
    TARGET_DIMENSION = 1536
    HASH_CACHE_FILE = cache_dir / "ingestion_hash_cache_openrouter.json"
else:
    # Read the explicit model identifier casing string from the .env parameters
    local_model_target = os.getenv("Local_Embedding_Model", "BAAI/bge-m3").strip()
    
    print(f"🤗 Mode: Local Fallback Settings Activated. Launching [{local_model_target}] (1024 Dim)...")
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=local_model_target,   # Passes parameter dynamically
        model_kwargs={'device': 'cpu'} # embedding model so keeps on CPU
    )
    INDEX_NAME = "fde-sop-index-local"   # Isolated Local Model Index
    TARGET_DIMENSION = 1024              # Standard width for BGE-M3
    HASH_CACHE_FILE = cache_dir / "ingestion_hash_cache_local.json" 

hash_cache = {}
if HASH_CACHE_FILE.exists():
    try:
        with open(HASH_CACHE_FILE, "r") as f:
            hash_cache = json.load(f)
    except Exception:
        hash_cache = {}

# ==========================================
# 3. PINECONE PROVISIONING
# ==========================================
print(f"Connecting to Pinecone Index Target: [{INDEX_NAME}]...")
pc = Pinecone(api_key=PINECONE_API_KEY) # Initialize the Pinecone client

existing_indexes = pc.list_indexes().names()

# Self-healing verification in case an index was created with a wrong legacy dimension
if INDEX_NAME in existing_indexes:
    desc = pc.describe_index(INDEX_NAME)
    if desc.dimension != TARGET_DIMENSION:
        print(f"⚠️ Fixing tracking: Purging mismatched {desc.dimension} dim index...")
        pc.delete_index(INDEX_NAME) # if dimension is not = TARGET_DIMENSION, then it will delete the index
        existing_indexes = [name for name in existing_indexes if name != INDEX_NAME]
        # if the index is deleted, we will create a new one. if INDEX_NAME not in existing_indexes: then it will create a new one

if INDEX_NAME not in existing_indexes:
    print(f"Creating isolated target index: {INDEX_NAME} ({TARGET_DIMENSION} Dim)...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=TARGET_DIMENSION, 
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index_client = pc.Index(INDEX_NAME)
vector_store = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
 # using this we can push the data to pinecone

# ==========================================
# 4. ROBUST POLYMORPHIC PARSER
# ==========================================
def parse_and_chunk_document(doc_path: Path) -> list[Document]:
    ext = doc_path.suffix.lower()
    raw_chunks: list[Document] = [] # list of multiple langchain documents, different sections of files saves here
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
    
    if ext == ".md":
        headers_to_split_on = [("#", "Header_1"), ("##", "Header_2"), ("###", "Header_3")] #splitting header with multiple ##
        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        raw_text = doc_path.read_text(encoding="utf-8")
        header_docs = md_splitter.split_text(raw_text) # splitting header on the basis of line 108
        raw_chunks = text_splitter.split_documents(header_docs)
        
    elif ext == ".txt":
        raw_text = doc_path.read_text(encoding="utf-8")
        raw_docs = [Document(page_content=raw_text)]
        raw_chunks = text_splitter.split_documents(raw_docs)
        
    elif ext == ".pdf":
        pdf_docs = []
        try:
            with open(doc_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        pdf_docs.append(Document(page_content=page_text, metadata={"page_number": page_num + 1}))
            raw_chunks = text_splitter.split_documents(pdf_docs)
        except Exception as e:
            print(f"  ❌ Error parsing PDF {doc_path.name}: {e}")
            return []
        
    elif ext in [".csv", ".xlsx"]: # no resursive text splitter for these otherwwise it will be very messy
        try:
            df = pd.read_csv(doc_path) if ext == ".csv" else pd.read_excel(doc_path)
        except Exception as e:
            print(f"  ❌ Error reading table: {e}")
            return []
            
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_items = [
                f"{str(col)}: {str(val)}" 
                for col, val in row_dict.items() 
                if pd.notna(val) and str(val).strip() != ""
            ]
            
            if row_items:
                row_text = " | ".join(row_items)
                doc_item = Document(page_content=row_text, metadata={"row_index": int(idx)})
                raw_chunks.append(doc_item)

    # sanity check
    valid_chunks = []
    for chunk in raw_chunks:
        clean_text = chunk.page_content.strip() # removing space
        if clean_text:
            chunk.page_content = clean_text
            valid_chunks.append(chunk)
            
    return valid_chunks

# ==========================================
# 5. INCREMENTAL PIPELINE WITH BATCHING
# ==========================================
policy_dir = project_root / "data" / "policy"
target_patterns = ["*.md", "*.txt", "*.pdf", "*.csv", "*.xlsx"]
current_files = {}
for pattern in target_patterns:
    for file_path in policy_dir.glob(pattern):
        current_files[file_path.name] = file_path

# this is local thing, no need for CI/CD
print(f"Found {len(current_files)} policy file(s) in {policy_dir}...")

updated_cache = {}
cache_modified = False

cached_filenames = set(hash_cache.keys()) # for the first time it is empty
current_filenames = set(current_files.keys())
deleted_files = cached_filenames - current_filenames # any difference in files means deleted

for deleted_file in deleted_files:
    print(f"🗑️ Detected deleted file: {deleted_file}. Purging from Pinecone...")
    try:
        index_client.delete(filter={"source_file": {"$eq": deleted_file}})
        cache_modified = True
    except Exception as e:
        print(f"  ❌ Failed to purge {deleted_file}: {e}")
# for deleted files, we do not require embeddings but for updated/modified files we need embeddings

for file_name, file_path in current_files.items():
    file_bytes = file_path.read_bytes()
    file_hash = hashlib.md5(file_bytes).hexdigest() # creating hash of files
    updated_cache[file_name] = file_hash
    
    if hash_cache.get(file_name) == file_hash:
        print(f"✨ Skipped (Unchanged): {file_name}")
        continue
        
    print(f"🔄 Processing updates: {file_name}...")
    cache_modified = True
    
    try:
        try:
            index_client.delete(filter={"source_file": {"$eq": file_name}}) #then first delete the index from DB
        except Exception:
            pass 
        
        chunks = parse_and_chunk_document(file_path)
        if not chunks:
            print(f"  ⚠️ No valid text chunks extracted from {file_name}.")
            continue

        #add metadata and add to vector store
        #chunk is langchain document
        explicit_ids = []
        for idx, chunk in enumerate(chunks):
            chunk.metadata["source_file"] = file_name
            chunk.metadata["file_format"] = file_path.suffix.replace(".", "").upper()
            chunk.metadata["document_type"] = "Compliance Asset"
            explicit_ids.append(f"{file_name}-chunk-{idx}") 

        # we are ingesting in batches of 100 bcz there can be rate limiter and gives error
        batch_size = 100
        total_chunks = len(chunks)
        print(f"  📤 Upserting {total_chunks} chunk(s) in batches of {batch_size}...")
        
        for i in range(0, total_chunks, batch_size):
            batch_docs = chunks[i : i + batch_size]
            batch_ids = explicit_ids[i : i + batch_size]
            vector_store.add_documents(documents=batch_docs, ids=batch_ids)
            
    except Exception as e:
        print(f"❌ Error during ingestion of {file_name}: {e}")
        updated_cache.pop(file_name, None)

# ==========================================
# 6. SYNC HASH CACHE
# ==========================================
if cache_modified:
    with open(HASH_CACHE_FILE, "w") as f:
        json.dump(updated_cache, f, indent=4)
    print("✅ Ingestion & cache update complete.")
else:
    print("🌴 Index is already up-to-date.")