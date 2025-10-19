# 🧠 Foundational Skill Diagnostician & Progress Narrator Agents

> Developer-friendly Certification Challenge Submission (Ontario Science Focus)  
> 🎯 Diagnose → Guide → Narrate Progress • 🧩 Science-aligned RAG • 🛠️ Agentic Reasoning

---

## 🟢 Task 1 — Defining the Problem & Audience

**Answering rubric question:**  
> “Write a succinct 1-sentence description of the problem.”  
> “Write 1–2 paragraphs on why this is a problem for your specific user.”

Teachers and parents struggle to both **detect the root cause of learning gaps** and **track how a student’s understanding evolves over time**.  

Ontario educators often see a wrong answer but cannot easily tell *why*—vocabulary, reasoning, or prior-concept gaps. Without that diagnosis, feedback stays shallow. And even when they intervene, progress is hard to measure across weeks because report cards are snapshots, not narratives.  
Families need a tool that delivers both **diagnosis** (what to fix) and **trajectory** (is it improving?) to sustain continuous learning in Science & Math.

---

## 🟢 Task 2 — Proposed Solution & Agentic Reasoning

**Answering rubric question:**  
> “Propose a solution and describe where you will use an agent or agents.  
> What will you use agentic reasoning for in your app?”

Two cooperating agents create a continuous feedback loop:  

1️⃣ **Foundational Skill Diagnostician Agent** — analyzes student answers, pinpoints conceptual gaps, and plans the next diagnostic step using a *planning loop*.  
2️⃣ **Longitudinal Progress Narrator Agent** — summarizes chat + quiz logs into a *3-sentence progress note + Home Tip*, using *reflective reasoning* over persistent memory.

> **Agentic reasoning:**  
> • Diagnostician → *planning* next question or hint based on error pattern.  
> • Narrator → *reflection* across sessions to produce personalized, tone-controlled reports.  
> Together they deliver adaptive, curriculum-aligned, empathetic feedback.

---

## 🟢 Task 3 — Dealing with Data (Chunking Strategy) 🧱

**Answering rubric question:**  
> “Describe the default chunking strategy you will use and why you made this decision.”

We use **semantic chunking** by meaning boundaries—section headers, paragraph shifts, and conceptual transitions—so each chunk remains a *complete teaching unit*.  

This suits Science PDFs such as *Bees and Pollination* where “pollen → seed → food chain” must stay intact. Fixed-window chunking often splits mid-concept; semantic chunking preserves coherence for retrieval.  
**Examples:**  
- In *Water Cycle*, “evaporation → condensation → precipitation” must appear together.  
- In *Ecosystems*, definitions + examples belong in one retrieval unit.  

Semantic chunking produced higher **faithfulness**, **context recall**, and **answer relevancy**, ensuring retrieval of concept-complete context like a teacher would provide.

---

## 🟢 Task 4 — End-to-End Prototype (Architecture Overview)

**Answering rubric question:**  
> “Describe the tools you plan to use in each part of your stack.  
> Write one sentence on why you made each tooling choice.”

| Layer | Tool | Rationale |
|:--|:--|:--|
| 🧠 LLM Core | **OpenAI GPT-4-mini**, **text-embedding-3-small** | Cost-efficient reasoning + high-quality embeddings |
| 🔄 Graph Flow | **LangGraph** | Orchestrates multi-agent planning + reflection |
| 🧩 Framework | **LangChain** | Provides retriever + tool abstractions |
| 🗂️ Vector Store | **Qdrant (persistent)** | Local reproducibility and fast vector search |
| ⚙️ Reranker | **Cohere Rerank** | Surfaces the most instructionally useful chunks |
| 🌐 Backend/UI | **FastAPI + Next.js** | Lightweight modular API + frontend |

**Architecture Diagram:**
![Architecture Diagram](./docs/architecture.png)

```mermaid
%% Quiz Flow Architecture Diagram (Mermaid)
%% GitHub-safe syntax (ASCII only)

flowchart LR

  subgraph FE[Frontend - Next.js]
    A[Read Page /read/:kidId] -->|POST /api/next-session| B(Create Next Session)
    B --> C[Reading Timer 5 min]
    C -->|Timer expired or Skip| D[Quiz UI MCQ]
    D --> E{Answer Selected?}
    E -->|Next| D
    E -->|Finish| F[Compute Score Percent]
    F -->|POST /api/sessions/complete| G(Complete Session)

    H[Quiz Page /quiz] -->|POST /api/diagnostician| I(Diagnostician API)
  end

  subgraph API[Next.js API Routes]
    B --> J[/api/next-session/]
    G --> K[/api/sessions/complete/]
    I --> L[/api/diagnostician/]
  end

  subgraph BE[Backend - FastAPI]
    L --> M[/api/search/]
    L --> N[/api/evaluate/]
    N --> O{agent_response JSON}
  end

  subgraph DATA[Data]
    P[Qdrant Vector DB]
    Q[Session and Quiz Store (frontend/lib/db)]
  end

  M --> P
  J --> Q
  G --> Q
  O --> I
  I --> H
```

---

## 🟢 Task 5 — Golden Dataset & RAGAS Evaluation 🧪

**Answering rubric question:**  
> “Provide at least one example of an evaluated answer and explain the score.”

### 📘 Example 1 — Baseline (Ungrounded)

**Prompt:** “What is pollination?”  
**Score:** 0.4796985490747969 (≈ 0.48)

Correct definition but **minimal context**—omits pollinators and significance.  
Feedback → *Add why it matters (seed/fruit formation, human food systems) and mention other pollinators.*

---

### 📗 Example 2 — Grounded (with Curriculum Context)

**Prompt:** “What is pollination?”  
**Score:** 0.7966748581700177 (≈ 0.80)

Comprehensive coverage—mechanism + bee role + human impact; misses minor details.  
Feedback → *Excellent—expand to non-bee pollinators and nectar cycle.*

---

### 📊 RAGAS Metric Comparison (Phase 2)

**Answering rubric question:**  
> “Show your quantitative evaluation and analysis.”

**Terminology:** `quiz_question_by_system`, `answer_by_teacher_agent`, `reference_answer`, `retrieved_contexts`  
📁 `phase2_ragas_comparison_rerank_20251018_231012.json`

| Metric | Baseline (Semantic) | Improved (Semantic + Reranker) | Δ (Improvement) | What It Means |
|:--|:--:|:--:|:--:|:--|
| **Faithfulness** | 0.850 | 0.900 | +0.050 | Answer better supported by retrieved chunks (no hallucination). |
| **Context Recall** | 0.883 | 0.883 | +0.000 | Full coverage maintained. |
| **Context Precision** | 1.000 | 1.000 | +0.000 | Noise-free retrieval preserved. |
| **Answer Relevancy** | 0.779 | 0.895 | +0.116 | Answer aligns more closely with curriculum truth. |

**📈 Metrics Analysis Placeholder:**  
`![Metrics Analysis](./docs/metrics_comparison.png)`

**Analysis:**  
- **Faithfulness ↑ (+0.05)** → Fewer unsupported sentences.  
- **Answer Relevancy ↑ (+0.12)** → Better conceptual alignment (pollination → seeds → food systems).  
- Recall & Precision steady → Reranking improved ordering without loss or noise.

---

## 🟢 Task 6 — Advanced Retrieval Technique

**Answering rubric question:**  
> “Explain what advanced retrieval or reranking you used and why.”

Layered **Cohere Reranker** on top of semantic chunking.  
It re-orders retrieved chunks by contextual similarity to the query, surfacing the most instructionally relevant paragraphs first.  
In our Diagnostician scenario, that means the agent reads the bee-pollination segment before definitions—boosting **faithfulness** and **relevancy** without changing coverage.

---

## 🟢 Task 7 — Assessing Performance & Future Work 🗺️

**Answering rubric question:**  
> “Summarize how you will assess ongoing performance and what you will improve next.”

- Continue logging **RAGAS metrics** per quiz to monitor drift.  
- From **Oct 20 → Demo Day (3 weeks):** track one learner’s 20 diagnostic interactions and generate a **consolidated progress report**.  
- Upload additional Ontario Science PDFs to expand curriculum coverage.  
- Add a **dashboard** showing longitudinal progress, skill-gap map, and next practice suggestions.  
- Target metrics: **Faithfulness ≥ 0.9**, **Answer Relevancy ≥ 0.9** across new datasets.

---

## 🧰 Stack Summary & Quick Run Guide

     ```bash
# Backend
uv run uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm install && npm run dev
```
