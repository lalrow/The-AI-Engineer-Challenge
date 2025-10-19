"""
Foundational Diagnostician - Retriever (AIE8 Sessions 6-10 Compliant)

Loads a PDF, chunks text using SemanticChunker for conceptual coherence,
embeds with langchain-openai, and upserts into Qdrant collection.

Requirements:
  qdrant-client>=1.7,<1.9
  langchain-openai>=0.3.7,<0.4
  pymupdf>=1.24.0

ENV:
  OPENAI_API_KEY=<your key>
  QDRANT_URL=./qdrant_local (default; persistent local instance)
  COLLECTION_NAME=science_curriculum_g3_g6 (default)

Usage:
  export OPENAI_API_KEY=sk-...
  uv run python projects/diagnostician-agent/retriever/load_pdf_to_qdrant.py \
    --pdf ./public/pdfs/grade3/bees.pdf
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

def _ensure_deps():
  missing: List[str] = []
  try:
    import fitz  # type: ignore
  except Exception:
    missing.append("pymupdf")
  try:
    import qdrant_client  # type: ignore
  except Exception:
    missing.append("qdrant-client")
  try:
    from langchain_openai import OpenAIEmbeddings  # type: ignore
  except Exception:
    missing.append("langchain-openai")
  try:
    from langchain_experimental.text_splitter import SemanticChunker  # type: ignore
  except Exception:
    missing.append("langchain-experimental")
  if missing:
    print(
      "Missing dependencies: " + ", ".join(missing) + "\n"
      "Install with: uv pip install qdrant-client>=1.7,<1.9 langchain-openai>=0.3.7,<0.4 pymupdf",
      file=sys.stderr,
    )
    sys.exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
  import fitz  # type: ignore
  doc = fitz.open(pdf_path)
  parts: List[str] = []
  for page in doc:
    parts.append(page.get_text("text"))
  doc.close()
  return "\n".join(p.strip() for p in parts if p and p.strip())


def chunk_text_with_langchain(text: str, api_key: str) -> List[str]:
  """
  Chunk text using SemanticChunker for conceptual coherence.
  This preserves semantic meaning (e.g., 'nectar → honey' process stays together).
  """
  from langchain_experimental.text_splitter import SemanticChunker
  from langchain_openai import OpenAIEmbeddings
  
  embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
  )
  splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
  )
  return splitter.split_text(text)


def embed_texts_with_langchain(texts: List[str], api_key: str) -> List[List[float]]:
  from langchain_openai import OpenAIEmbeddings
  embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
  )
  return [embeddings.embed_query(text) for text in texts]


def upsert_qdrant(collection: str, payloads: List[dict], vectors: List[List[float]], qdrant_url: str):
  from qdrant_client import QdrantClient
  from qdrant_client.models import VectorParams, Distance, PointStruct

  # Support URL or path-based Qdrant only (no :memory:)
  if str(qdrant_url).startswith("http"):
    client = QdrantClient(url=qdrant_url)
  elif os.path.isdir(qdrant_url) or "/" in qdrant_url or qdrant_url.endswith(".db"):
    client = QdrantClient(path=qdrant_url)
  else:
    print(f"❌ Invalid QDRANT_URL: {qdrant_url}. Must be a valid local path or http URL.", file=sys.stderr)
    sys.exit(1)

  # Create collection if not exists
  try:
    client.get_collection(collection_name=collection)
  except Exception:
    client.recreate_collection(
      collection_name=collection,
      vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE),
    )

  points = [
    PointStruct(id=idx, vector=vectors[idx], payload=payloads[idx])
    for idx in range(len(vectors))
  ]
  client.upsert(collection_name=collection, points=points)


def main():
  _ensure_deps()
  parser = argparse.ArgumentParser()
  parser.add_argument("--pdf", required=True, help="Path to PDF file")
  args = parser.parse_args()

  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    print("Missing OPENAI_API_KEY in environment", file=sys.stderr)
    sys.exit(1)

  qdrant_url = os.getenv("QDRANT_URL", "./qdrant_local")
  
  collection_name = os.getenv("COLLECTION_NAME", "science_curriculum_g3_g6")

  if not os.path.exists(args.pdf):
    print(f"PDF not found: {args.pdf}", file=sys.stderr)
    sys.exit(1)

  filename = os.path.basename(args.pdf)
  print(f"[retriever] Extracting text from: {args.pdf}")
  text = extract_text_from_pdf(args.pdf)
  print(f"[retriever] Text length: {len(text)} chars")

  print("[retriever] Chunking text with SemanticChunker (percentile=95)...")
  chunks = chunk_text_with_langchain(text, api_key)
  print(f"[retriever] Created {len(chunks)} semantic chunks")

  print("[retriever] Generating embeddings with langchain-openai...")
  vectors = embed_texts_with_langchain(chunks, api_key)
  print(f"[retriever] Generated {len(vectors)} embeddings")

  # Metadata structure per AIE8 Sessions
  payloads = [{
    "content": chunk,
    "metadata": {
      "source": filename,
      "topic": "pollination",  # TODO: extract from PDF or pass as arg
      "grade": 3,
      "strand": "life systems"
    }
  } for chunk in chunks]

  print(f"[retriever] Upserting into Qdrant collection: {collection_name}")
  upsert_qdrant(collection_name, payloads, vectors, qdrant_url)
  print(f"✅ Ingested {len(chunks)} chunks into {collection_name}")


if __name__ == "__main__":
  main()


