# 🧠 Foundational Skill Diagnostician & Progress Narrator Agents  

> Developer-friendly Certification Challenge Submission (Ontario Science Focus)  
> 🎯 Diagnose → Guide → Narrate Progress • 🧩 Science-aligned RAG • 🛠️ Agentic Reasoning  

---

## 🟢 Task 1 — Defining Your Problem and Audience  

**Answering rubric question:**  
> “Write a succinct 1-sentence description of the problem.”  
> “Write 1-2 paragraphs on why this is a problem for your specific user.”  

Teachers and parents struggle to both **detect the root cause of learning gaps** and **track how a student’s understanding evolves over time**.  

Ontario educators often see a wrong answer but cannot easily tell *why* — vocabulary, reasoning, or prior-concept gaps. Without that diagnosis, feedback stays shallow. And even when they intervene, progress is hard to measure across weeks because report cards are snapshots, not narratives. Families need a tool that delivers both **diagnosis** (what to fix) and **trajectory** (is it improving?) to sustain continuous learning in Science and Math.  

---

## 🟢 Task 2 — Propose a Solution & Agentic Reasoning  

**Answering rubric question:**  
> “Propose a solution.”  
> “Describe the tools you plan to use in each part of your stack. Write one sentence on why you made each tooling choice.”  
> “Where will you use an agent or agents? What will you use ‘agentic reasoning’ for in your app?”  

Two cooperating agents form the foundation:  

1️⃣ **Foundational Skill Diagnostician Agent** — analyzes student answers, pinpoints conceptual gaps, and plans the next diagnostic step (*planning loop*).  
2️⃣ **Longitudinal Progress Narrator Agent** — summarizes chat + quiz logs into a *3-sentence progress note + Home Tip* (*reflective reasoning*).  

> **Agentic reasoning:**  
> • Diagnostician → *planning* next question or hint based on error pattern.  
> • Narrator → *reflection* across sessions to produce personalized, tone-controlled reports.  
> Together they deliver adaptive, curriculum-aligned, empathetic feedback.  

**Stack Overview**

| # | Component | Tool(s) Used | Why This Tool Was Chosen | Future Enhancement |
|:-:|:-----------|:-------------|:--------------------------|:------------------|
| 1 | **LLM** | **OpenAI GPT-4-mini** | Reliable reasoning at low latency and cost for teacher-style explanations. | 🔮 May upgrade to a larger model like **GPT-4-Turbo / Claude Opus** for richer diagnostic feedback. |
| 2 | **Embedding Model** | **text-embedding-3-small** | Compact vector size (1.5 k dim) with strong semantic coverage for educational text. | 🚀 Consider **text-embedding-3-large** or **Cohere Embed v3** for better cross-subject alignment. |
| 3 | **Orchestration / Agent Flow** | **LangGraph + LangChain** | Handles multi-step agent planning and reflection with composable node-based logic. | ♻️ Integrate a graph-based planner for adaptive dialogue branching. |
| 4 | **Vector Database** | **Qdrant (local persistent)** | Open-source, high-speed similarity search with reproducible local setup. | ☁️ Move to managed Qdrant Cloud or Pinecone for scale + analytics. |
| 5 | **Monitoring** | *(lightweight logs)* | Minimal in-app telemetry for prototype validation. | 📊 Add **LangSmith** for trace visualization and end-to-end evaluation tracking. |
| 6 | **Evaluation** | **RAGAS + custom pytest scripts** | Quantifies faithfulness, recall, precision, and relevancy metrics. | 📈 Automate daily metric refresh via LangSmith dashboards. |
| 7 | **User Interface** | **Next.js (frontend)** + **FastAPI (backend)** | Modern, modular stack enabling real-time quiz interaction and feedback. | 💬 Add speech input / voice feedback layer for accessibility. |
| 8 | **(Optional) Serving & Inference** | **Localhost** | Simple local hosting for demo; compatible with Dockerized pipelines. | ☁️ Deploy on **Vercel + Railway** with CI/CD for continuous updates. |

**Flow Diagram:**  
`![Flow Diagram](./docs/Figma_4_boxes.png)`  

---

## 🧩 Task 3 — Dealing with the Data  

> **Rubric Question 1:**  
> *Describe all of your data sources and external APIs, and describe what you’ll use them for.*  

> **Rubric Question 2:**  
> *Describe the default chunking strategy that you will use. Why did you make this decision?*  

> **Rubric Question 3 (Optional):**  
> *Will you need specific data for any other part of your application? If so, explain.*  

---

### **3a — Data Sources & External APIs**

| Component | Source / API | Purpose | Integration |
|:--|:--|:--|:--|
| **Primary RAG Data** | Ontario Science & Technology PDFs (Grades 3-6) — *Bees and Pollination*, *Water Cycle*, *Ecosystems* | Core reference corpus for the Diagnostician Agent. Each PDF contains curriculum-aligned lessons and examples that the agent retrieves to ground its feedback. | Loaded via `load_pdf_to_qdrant.py` into a persistent Qdrant collection (`science_curriculum_g3_g6`). |
| **External API Tool** | **Tavily Search API** | Acts as a web-search fallback if Qdrant retrieval fails or lacks coverage (for example, new Ontario curriculum updates or pollination examples not in PDFs). Registered but not actively invoked — available for future agentic expansion. | Imported via `langchain_tavily.TavilySearch(max_results=5)` and bound to the LangGraph model with `ChatOpenAI.bind_tools([retriever_tool, tavily_tool])`. |

**Internal components (not counted as external):** Qdrant vector database, FastAPI backend, Next.js frontend.

---

### **3b — Chunking Strategy 🧱**

We use the **SemanticChunker** from `langchain_experimental.text_splitter` with  
a **percentile breakpoint threshold of 95**, which groups text by **conceptual coherence** rather than fixed character limits.  
This preserves complete ideas and teaching segments instead of slicing through them mid-topic.

Science examples (*Bees & Pollination*, *Water Cycle*, *Ecosystems*) show that contextual continuity is key to accurate retrieval.  
Semantic chunking raised **faithfulness**, **context recall**, and **answer relevancy** in RAGAS tests.  

For instance, in the *Bees and Pollination* PDF, each paragraph forms a self-contained learning unit — such as *how pollen moves*, *role of insects*, or *importance for food production*.  
By letting the model detect these natural boundaries, the retriever stores meaningful segments that lead to higher-quality context during evaluation.  
The script implementing this (`load_pdf_to_qdrant.py`) embeds each semantic chunk with `text-embedding-3-small` before upserting into Qdrant.

---

### **3c — Optional Data Needs**

Future versions will aggregate ≈ 20 diagnostic sessions per student to build a **longitudinal progress summary**, tracking concept mastery and growth over time.  
These summaries will feed into a dashboard for parents and teachers to visualize learning progress and strengthen the feedback loop between tutor and student.  

---

✅ **Summary:**  
- **RAG Data:** Ontario curriculum PDFs stored in Qdrant  
- **External API:** Tavily Search (fallback available in LangGraph tool-belt)  
- **Chunking:** SemanticChunker (p95) for conceptual coherence — tested on *Bees & Pollination*  
- **Future Data:** Student progress records for longitudinal insights  


---

## 🟢 Task 4 — Building a Quick End-to-End Prototype  

**Answering rubric question:**  
> “Build an end-to-end prototype and deploy to local host with a front end (Vercel deployment not required).”  

✅ Completed prototype includes FastAPI backend, Next.js frontend, and Qdrant vector store integration.  
✅ Tested locally with OpenAI API and Cohere Reranker enabled.  

**Run Commands**

---

## 🟢 Task 5 — Creating a Golden Test Data Set & RAGAS Evaluation 🧪

**Answering rubric question:**  
> “Assess your pipeline using the RAGAS framework including key metrics faithfulness, response relevance, context precision, and context recall. Provide a table of your output results.”  
> “What conclusions can you draw about the performance and effectiveness of your pipeline with this information?”

### 📘 Example 1 — Baseline (Ungrounded)

**Prompt:** “What is pollination?”  
**Score:** 0.4796985490747969 (≈ 0.48)  
Correct definition but **minimal context** — omits pollinators and significance.  
Feedback → *Add why it matters (seed/fruit formation, human food systems) and mention other pollinators.*

---

### 📗 Example 2 — Grounded (With Curriculum Context)

**Prompt:** “What is pollination?”  
**Score:** 0.7966748581700177 (≈ 0.80)  
Comprehensive coverage — mechanism + bee role + human impact; misses minor details.  
Feedback → *Excellent — expand to non-bee pollinators and nectar cycle.*

---

### 📊 RAGAS Metric Comparison (Phase 2)

**Terminology:** `quiz_question_by_system`, `answer_by_teacher_agent`, `reference_answer`, `retrieved_contexts`  
📁 Results file: `phase2_ragas_comparison_rerank_20251018_231012.json`

| Metric | Baseline (Semantic) | Improved (Semantic + Reranker) | Δ (Improvement) | Meaning |
|:--|:--:|:--:|:--:|:--|
| **Faithfulness** | 0.850 | 0.900 | +0.050 | Answer better supported by retrieved chunks (no hallucination). |
| **Context Recall** | 0.883 | 0.883 | +0.000 | Full coverage maintained. |
| **Context Precision** | 1.000 | 1.000 | +0.000 | Noise-free retrieval preserved. |
| **Answer Relevancy** | 0.779 | 0.895 | +0.116 | Answer aligns more closely with curriculum truth. |

**📈 Metrics Diagram Placeholder:**  
`![Metrics Analysis](./docs/metrics_comparison.png)`

**Analysis Summary:**  
- **Faithfulness ↑ (+0.05)** → Fewer unsupported sentences.  
- **Answer Relevancy ↑ (+0.12)** → Better conceptual alignment (pollination → seeds → food systems).  
- Recall and Precision steady → Reranking improved ordering without loss or noise.  

---

## 🟢 Task 6 — Advanced Retrieval (5 Points)

**Answering rubric question:**  
> “Swap out base retriever with advanced retrieval methods.”

The base semantic retriever was enhanced with **Cohere Reranker**, which re-orders the top-k chunks by contextual similarity to the query.  
This improved **faithfulness (+0.05)** and **answer relevancy (+0.12)** without hurting recall or precision.  

📁 Reranker results file: `advanced_retrieval_cohere_eval_20251018.json`

| Metric | Before | After Rerank | Δ |
|:--|:--:|:--:|:--:|
| Faithfulness | 0.85 | 0.90 | +0.05 |
| Answer Relevancy | 0.78 | 0.89 | +0.11 |

---

## 🟢 Task 7 — Assessing Performance & Future Work 🗺️

**Answering rubric question:**  
> “How does the performance compare to your original RAG application? Test the new retrieval pipeline using the RAGAS frameworks to quantify any improvements. Provide results in a table.”  
> “Articulate the changes that you expect to make to your app in the second half of the course. How will you improve your application?”  

### Performance Comparison

| Metric | Original (Semantic) | Advanced (Reranker) | Δ |
|:--|:--:|:--:|:--:|
| Faithfulness | 0.85 | 0.90 | +0.05 |
| Answer Relevancy | 0.78 | 0.89 | +0.11 |
| Context Recall | 0.88 | 0.88 | 0 |
| Context Precision | 1.00 | 1.00 | 0 |

### Future Enhancements
- Track 20 diagnostic sessions per student (Oct 20 → Demo Day).  
- Aggregate feedback into a **consolidated progress report**.  
- Upload more Ontario Science PDFs (G3–G6).  
- Add a **dashboard** showing longitudinal progress, skill-gap map, and next practice suggestions.  
- Target metrics: **Faithfulness ≥ 0.9**, **Answer Relevancy ≥ 0.9** across expanded datasets.  

---

## 🟢 Final Submission Checklist ✅

| Item | Deliverable | Status |
|:--|:--|:--:|
| 1 | 5-minute loom demo (showing use case + workflow) | 🔜 Pending |
| 2 | Written document answering each rubric question | ✅ Complete |
| 3 | All relevant code in GitHub repo | ✅ Complete |
| 4 | Persistent Qdrant + API integration verified | ✅ Complete |

---


