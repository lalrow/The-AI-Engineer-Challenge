"""
Phase 2 – RAGAS Evaluation Script
Evaluates Diagnostician Agent answers using RAGAS metrics.
This version mirrors Session 8 notebook logic.
"""

import os
import pandas as pd
import numpy as np
import json # Added for JSON output
from datasets import Dataset
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate
from ragas.metrics import faithfulness, context_precision, context_recall, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

# ----------------------------
# 0️⃣  Load Environment
# ----------------------------
load_dotenv()

# ----------------------------
# 1️⃣  Load Evaluation Data
# ----------------------------
print("📂 Loading evaluation datasets...")

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load baseline dataset (minimal answers)
baseline_path = os.path.join(script_dir, "baseline_eval.csv")
baseline_df = pd.read_csv(baseline_path)
# Parse retrieved_contexts as list (it's stored as string representation)
import ast
baseline_df['retrieved_contexts'] = baseline_df['retrieved_contexts'].apply(ast.literal_eval)
baseline_dataset = Dataset.from_pandas(baseline_df)

# Load grounded dataset (detailed answers)
grounded_path = os.path.join(script_dir, "grounded_eval.csv")
grounded_df = pd.read_csv(grounded_path)
grounded_df['retrieved_contexts'] = grounded_df['retrieved_contexts'].apply(ast.literal_eval)
grounded_dataset = Dataset.from_pandas(grounded_df)

print(f"✅ Loaded {len(baseline_df)} baseline examples")
print(f"✅ Loaded {len(grounded_df)} grounded examples")

# ----------------------------
# 2️⃣  Initialize Models
# ----------------------------
print("\n🤖 Initializing models (matching Diagnostician Agent config)...")
llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))

# ----------------------------
# 3️⃣  Define Metrics
# ----------------------------
metrics = [faithfulness, context_recall, context_precision, answer_relevancy]
print(f"📊 Evaluating with {len(metrics)} metrics: {[m.name for m in metrics]}")

# ----------------------------
# 4️⃣  Run Evaluation - Baseline
# ----------------------------
print("\n🚀 Running RAGAS Evaluation on BASELINE dataset...")
baseline_results = evaluate(
    dataset=baseline_dataset, 
    metrics=metrics, 
    llm=llm, 
    embeddings=embeddings
)
print("✅ Baseline evaluation complete!")

# ----------------------------
# 5️⃣  Run Evaluation - Grounded
# ----------------------------
print("\n🚀 Running RAGAS Evaluation on GROUNDED dataset...")
grounded_results = evaluate(
    dataset=grounded_dataset, 
    metrics=metrics, 
    llm=llm, 
    embeddings=embeddings
)
print("✅ Grounded evaluation complete!")

# ----------------------------
# 6️⃣  Display Results
# ----------------------------
print("\n" + "="*60)
print("📊 EVALUATION RESULTS")
print("="*60)

print("\n🔵 BASELINE Results (minimal answers):")
print(baseline_results)

print("\n🟢 GROUNDED Results (detailed answers):")
print(grounded_results)

# ----------------------------
# 7️⃣  Calculate Comparison Metrics
# ----------------------------
print("\n" + "="*60)
print("📈 COMPARISON: Baseline vs Grounded")
print("="*60)

# Extract mean scores - compute mean from the list of individual scores
# Create comparison dataframe
comparison_data = []
for metric in metrics:
    metric_name = metric.name
    # Get list of scores and compute mean
    baseline_scores_list = baseline_results[metric_name]
    grounded_scores_list = grounded_results[metric_name]
    
    baseline_score = np.mean(baseline_scores_list)
    grounded_score = np.mean(grounded_scores_list)
    delta = grounded_score - baseline_score
    
    comparison_data.append({
        "Metric": metric_name,
        "Baseline": f"{baseline_score:.3f}",
        "Grounded": f"{grounded_score:.3f}",
        "Δ (Improvement)": f"{delta:+.3f}"
    })

comparison_df = pd.DataFrame(comparison_data)
print("\n")
print(comparison_df.to_string(index=False))

# ----------------------------
# 8️⃣  Save Results
# ----------------------------
print("\n💾 Saving results...")

# Save detailed results
baseline_results_path = os.path.join(script_dir, "baseline_ragas_results.json")
grounded_results_path = os.path.join(script_dir, "grounded_ragas_results.json")
comparison_path = os.path.join(script_dir, "phase2_ragas_comparison.json")

baseline_results.to_pandas().to_json(baseline_results_path, orient="records", indent=2)
grounded_results.to_pandas().to_json(grounded_results_path, orient="records", indent=2)
comparison_df.to_json(comparison_path, orient="records", indent=2)

print(f"✅ Baseline results saved to: {baseline_results_path}")
print(f"✅ Grounded results saved to: {grounded_results_path}")
print(f"✅ Comparison saved to: {comparison_path}")

# ----------------------------
# 9️⃣  Summary
# ----------------------------
print("\n" + "="*60)
print("🎯 SUMMARY")
print("="*60)

# Calculate overall improvement
improvements = [float(row["Δ (Improvement)"]) for row in comparison_data]
avg_improvement = sum(improvements) / len(improvements)

print(f"\n📊 Average improvement across all metrics: {avg_improvement:+.3f}")

if avg_improvement > 0.3:
    print("✅ EXCELLENT: Grounded answers show significant improvement (>0.3)")
elif avg_improvement > 0.15:
    print("✅ GOOD: Grounded answers show moderate improvement (>0.15)")
else:
    print("⚠️  WARNING: Improvement is lower than expected (<0.15)")

print("\n🎉 RAGAS Evaluation Complete!")
print("📁 Results ready for Phase 2 reporting and Loom demo.")

