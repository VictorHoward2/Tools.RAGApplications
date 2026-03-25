# Similar-issue pipeline

Data flow from CSV export through JSON stages to vector similarity search.

```mermaid
flowchart TB
    A([convert.csv2json])
    A --> B["<b>Raw JSON</b> — Defect_list.json<br/>────────────────────────<br/>Includes:<br/>case_code · type · title · request_reason · defect_type<br/>phenomena[] · root_cause · countermeasure<br/>resolution{…} · comments[]"]

    B -->|"Preprocessing"| D["<b>Preprocessed JSON</b> — Defect_list_rag.json<br/>────────────────────────<br/>Adds:<br/>search_text — title, phenomena, defect category<br/>evidence_text — important log lines from comments<br/>plus id, metadata, solution, evidence stats"]

    D --> E([Embedding])
    E --> F["<b>Vector index</b> — Defect_list_embeddings.json<br/>────────────────────────<br/>Adds: embedding[] per issue<br/>(BGE-M3, L2-normalized)"]

    F --> G([RAG -> Issue Similarity])

    classDef module fill:#EEF2FF,stroke:#4338CA,stroke-width:2px,color:#1E1B4B
    classDef file fill:#F8FAFC,stroke:#64748B,stroke-width:2px,color:#0F172A
    classDef runtime fill:#ECFDF5,stroke:#15803D,stroke-width:2px,color:#14532D

    class A,E module
    class B,D,F file
    class G runtime
```

Render in any Mermaid-capable viewer, or export PNG/SVG from [Mermaid Live Editor](https://mermaid.live/).

**Note:** `search_text` is built from title, observed symptoms, and defect category (`json2jsonRAG`); `evidence_text` uses filtered lines from the comment thread.
