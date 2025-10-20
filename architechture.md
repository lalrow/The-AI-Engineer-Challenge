%%{init: {"theme":"base","themeVariables":{"primaryColor":"#ffffff","primaryBorderColor":"#ff0000","primaryTextColor":"#000000","lineColor":"#ff0000","arrowheadColor":"#ff0000","fontSize":"16px","fontFamily":"Arial"},"flowchart":{"curve":"linear","nodeSpacing":50,"rankSpacing":70}}}%%
flowchart TD
    A1["① Frontend – Quiz Submit Button"]
    A2["② Next.js API Route – /api/diagnostician"]
    A3["③ FastAPI Endpoint – /api/search"]
    A4["④ Retriever – Qdrant + SemanticChunker"]
    A5["⑤ FastAPI Endpoint – /api/evaluate"]
    A6["⑥ Agent Graph Builder – build_graph_with_api_key()"]
    A7["⑦ Agent Node 1 – Retrieve Context"]
    A8["⑧ Agent Node 2 – Diagnose (Embeddings + LLM)"]
    A9["⑨ Frontend – Display Feedback & Score"]

    A1 --> A2 --> A3 --> A4 --> A5 --> A6 --> A7 --> A8 --> A9
