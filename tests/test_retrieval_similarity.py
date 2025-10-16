import os
import requests
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# === Load environment and reference answers ===
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
BASELINE = open("tests/baseline_answer.txt").read().strip()
GROUND_TRUTH = open("tests/grounded_answer.txt").read().strip()

print("🧪 Running Retrieval + Semantic Grounding Test...")

# === Step 1 – Query backend retrieval ===
resp = requests.post(
    "http://localhost:8000/api/search",
    headers={"Content-Type": "application/json"},
    json={"query": "What is pollination?", "top_k": 2, "api_key": API_KEY},
)

if resp.status_code != 200:
    raise SystemExit(f"❌ Search endpoint failed: {resp.status_code} {resp.text}")

data = resp.json()
if not data or not data[0].get("text"):
    raise SystemExit("❌ Retrieval failed: no chunks returned from backend.")

retrieved_texts = [r["text"] for r in data]
retrieved_text = " ".join(retrieved_texts)

print("\n📚 Retrieved chunks:")
for i, chunk in enumerate(retrieved_texts, 1):
    print(f"--- Chunk {i} ---\n{chunk[:200]}...\n")

# === Step 2 – Compute embeddings ===
client = OpenAI(api_key=API_KEY)

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Baseline comparison
emb = client.embeddings.create(
    model="text-embedding-3-small", input=[BASELINE, retrieved_text]
)
vec1, vec2 = emb.data[0].embedding, emb.data[1].embedding
similarity_baseline = cosine(vec1, vec2)

# Grounded comparison
emb_gt = client.embeddings.create(
    model="text-embedding-3-small", input=[GROUND_TRUTH, retrieved_text]
)
vec3, vec4 = emb_gt.data[0].embedding, emb_gt.data[1].embedding
similarity_grounded = cosine(vec3, vec4)

# === Step 3 – Evaluate thresholds ===
print(f"🔍 Similarity (baseline): {similarity_baseline:.3f} | (grounded): {similarity_grounded:.3f}")

if similarity_baseline < 0.4 or similarity_grounded < 0.8:
    print("\nExpected baseline ≥ 0.4 and grounded ≥ 0.8")
    print("❌ Retrieval test failed: similarity thresholds not met.")
    raise SystemExit(1)

print("✅ Retrieval and semantic grounding test passed successfully!")
