import os
import requests
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

def test_retrieval_similarity():
    # === Load environment and reference answers ===
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    baseline = open("tests/baseline_answer.txt").read().strip()
    ground_truth = open("tests/grounded_answer.txt").read().strip()

    print("🧪 Running Retrieval + Semantic Grounding Test...")

    # === Step 1 – Query backend retrieval ===
    resp = requests.post(
        "http://localhost:8000/api/search",
        headers={"Content-Type": "application/json"},
        json={"query": "What is pollination?", "top_k": 2, "api_key": api_key},
    )

    assert resp.status_code == 200, f"Search endpoint failed: {resp.status_code} {resp.text}"

    data = resp.json()
    assert data and data[0].get("text"), "Retrieval failed: no chunks returned from backend."

    retrieved_texts = [r["text"] for r in data]
    retrieved_text = " ".join(retrieved_texts)

    print("\n📚 Retrieved chunks:")
    for i, chunk in enumerate(retrieved_texts, 1):
        print(f"--- Chunk {i} ---\n{chunk[:200]}...\n")

    # === Step 2 – Compute embeddings ===
    client = OpenAI(api_key=api_key)

    def cosine(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # Baseline comparison
    emb = client.embeddings.create(
        model="text-embedding-3-small", input=[baseline, retrieved_text]
    )
    vec1, vec2 = emb.data[0].embedding, emb.data[1].embedding
    similarity_baseline = cosine(vec1, vec2)

    # Grounded comparison
    emb_gt = client.embeddings.create(
        model="text-embedding-3-small", input=[ground_truth, retrieved_text]
    )
    vec3, vec4 = emb_gt.data[0].embedding, emb_gt.data[1].embedding
    similarity_grounded = cosine(vec3, vec4)

    # === Step 3 – Evaluate thresholds ===
    print(f"🔍 Similarity (baseline): {similarity_baseline:.3f} | (grounded): {similarity_grounded:.3f}")

    assert similarity_baseline >= 0.4, f"Retrieval test failed: baseline similarity {similarity_baseline:.3f} < 0.4"
    assert similarity_grounded >= 0.8, f"Retrieval test failed: grounded similarity {similarity_grounded:.3f} < 0.8"
    assert similarity_baseline <= 0.7, f"Retrieval test failed: baseline similarity {similarity_baseline:.3f} > 0.7"

    print("✅ Retrieval and semantic grounding test passed successfully!")
