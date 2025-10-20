%%{init: {
  'theme': 'base',
  'themeVariables': { 
    'primaryColor': '#ffffff',
    'primaryBorderColor': '#ff0000',
    'primaryTextColor': '#000000',
    'lineColor': '#ff0000',
    'arrowheadColor': '#ff0000',
    'fontSize': '18px',
    'fontFamily': 'Arial'
  },
  'flowchart': { 
    'nodeSpacing': 60, 
    'rankSpacing': 80,
    'curve': 'linear'
  }
}}%%
flowchart LR
    A1["① CLICK SUBMIT<br/>IN QUIZ UI"]
    A2["② FRONTEND POSTS<br/>TO /diagnostician"]
    A3["③ NEXT.JS CALLS<br/>FASTAPI /search"]

    B1["④ FASTAPI SEARCH<br/>INVOKES RETRIEVER"]
    B2["⑤ QDRANT RETURNS<br/>TOP-K CHUNKS"]
    B3["⑥ NEXT.JS BUILDS<br/>CONTEXT STRING"]

    C1["⑦ FASTAPI POSTS<br/>TO /evaluate"]
    C2["⑧ AGENT RUNS<br/>RETRIEVE + DIAGNOSE"]
    C3["⑨ FRONTEND SHOWS<br/>FEEDBACK"]

    A1 --> A2 --> A3
    A1 --> B1
    A2 --> B2
    A3 --> B3
    B1 --> B2 --> B3
    B1 --> C1
    B2 --> C2
    B3 --> C3
    C1 --> C2 --> C3

    style A1 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000
    style A2 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000
    style A3 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000

    style B1 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000
    style B2 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000
    style B3 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000

    style C1 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000
    style C2 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000
    style C3 fill:#ffffff,stroke:#ff0000,stroke-width:2px,color:#000000
