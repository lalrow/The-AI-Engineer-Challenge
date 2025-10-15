"""
Foundational Diagnostician - Retriever Scaffold

Loads a PDF, chunks text, embeds with OpenAI, and upserts into an
in-memory Qdrant collection for quick local experimentation.

Requirements (install if missing):
  pip install qdrant-client==1.9.* openai==1.* pymupdf

ENV:
  OPENAI_API_KEY=<your key>

Usage:
  uv run python projects/diagnostician-agent/retriever/load_pdf_to_qdrant.py \
    --pdf ./public/pdfs/grade3/bees.pdf \
    --collection diagnostician-local
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable, List


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
  if missing:
    print(
      "Missing dependencies: " + ", ".join(missing) + "\n"
      "Install with: pip install qdrant-client==1.9.* pymupdf openai==1.*",
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


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
  words = text.split()
  chunks: List[str] = []
  i = 0
  step = max(1, chunk_size - overlap)
  while i < len(words):
    chunk = " ".join(words[i : i + chunk_size]).strip()
    if chunk:
      chunks.append(chunk)
    i += step
  return chunks


def embed_texts(texts: Iterable[str], api_key: str) -> List[List[float]]:
  import urllib.request
  import urllib.error

  url = "https://api.openai.com/v1/embeddings"
  headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
  }
  body = {
    "model": "text-embedding-3-small",
    "input": list(texts),
  }
  req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
  try:
    with urllib.request.urlopen(req) as resp:
      data = json.loads(resp.read().decode("utf-8"))
      return [item["embedding"] for item in data.get("data", [])]
  except urllib.error.HTTPError as e:
    detail = e.read().decode("utf-8", errors="ignore")
    raise RuntimeError(f"OpenAI embedding error {e.code}: {detail}")


def upsert_qdrant(collection: str, payloads: List[dict], vectors: List[List[float]]):
  from qdrant_client import QdrantClient
  from qdrant_client.http.models import VectorParams, Distance, PointStruct

  client = QdrantClient(":memory:")

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
  parser.add_argument("--collection", default="diagnostician-local")
  args = parser.parse_args()

  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    print("Missing OPENAI_API_KEY in environment", file=sys.stderr)
    sys.exit(1)

  if not os.path.exists(args.pdf):
    print(f"PDF not found: {args.pdf}", file=sys.stderr)
    sys.exit(1)

  print(f"[retriever] Extracting text from: {args.pdf}")
  text = extract_text_from_pdf(args.pdf)
  print(f"[retriever] Text length: {len(text)} chars")

  chunks = chunk_text(text)
  print(f"[retriever] Chunks: {len(chunks)}")

  print("[retriever] Generating embeddings...")
  vectors = embed_texts(chunks, api_key)
  print(f"[retriever] Received {len(vectors)} vectors")

  payloads = [{"content": c, "source": os.path.basename(args.pdf)} for c in chunks]
  print(f"[retriever] Upserting into Qdrant collection: {args.collection}")
  upsert_qdrant(args.collection, payloads, vectors)
  print("✅ Done")


if __name__ == "__main__":
  main()


