# EVY Knowledge Packs And SQLite RAG

This document defines the first pre-hardware knowledge-pack artifact and the optional SQLite RAG path.

Status: v1 software scaffold is implemented and covered by tests. It is not yet the default runtime RAG backend, and it has not been benchmarked on Raspberry Pi hardware.

## Why This Exists

EVY needs local emergency and community information that can be inspected, expired, backed up, and eventually verified before import. A SQLite-first RAG path gives the first lilEVY node a one-file knowledge store with keyword search now and optional vector search later.

## Knowledge-Pack Shape

A v1 knowledge pack can be a directory or zip file:

```text
knowledge-pack/
  manifest.json
  docs/
    shelter.txt
    water.txt
```

Minimum `manifest.json` fields:

```json
{
  "pack_id": "evy-local-emergency-us-ks",
  "region": "us-ks",
  "created_at": "2026-05-02T00:00:00Z",
  "expires_at": "2026-12-31T00:00:00Z",
  "source_owner": "Local emergency office",
  "source_urls": ["https://example.invalid/source"],
  "schema_version": "1.0",
  "emergency_priority": "normal",
  "documents": [
    {
      "id": "storm-shelter",
      "title": "Storm Shelter",
      "category": "emergency",
      "path": "docs/shelter.txt",
      "checksum_sha256": "sha256-of-document-text",
      "metadata": {
        "priority": "high"
      }
    }
  ],
  "signature": {
    "type": "development-sha256",
    "value": "signature-placeholder",
    "key_id": "dev-key"
  }
}
```

Implemented fields:

- `pack_id`
- `region`
- `created_at`
- `expires_at`
- `source_owner`
- `source_urls`
- `schema_version`
- `emergency_priority`
- per-document `id`, `title`, `category`, `path`, `text`, `checksum_sha256`, `expires_at`, and `metadata`
- optional `signature`

Validation currently checks manifest shape, ISO-8601 date fields, document readability, document checksums, optional content hash, and signature presence when required. The signature is a placeholder artifact for now; a stronger TUF-style approach remains a later field-readiness item.

## SQLite RAG Interface

Code entrypoint:

- `backend/services/rag_service/sqlite_rag_store.py`

Stable methods:

- `import_pack(pack_path, require_signature=False)`
- `search(query, top_k=3, category=None)`
- `health()`

Feature flags:

```bash
RAG_BACKEND=sqlite
SQLITE_RAG_ENABLED=true
SQLITE_RAG_DB_PATH=/data/lilevy/sqlite_rag.db
KNOWLEDGE_PACK_REQUIRE_SIGNATURE=false
```

The default remains `RAG_BACKEND=chroma` and `SQLITE_RAG_ENABLED=false`, so existing RAG behavior is preserved.

Service endpoints when SQLite RAG is enabled:

- `GET /sqlite-rag/health`
- `POST /sqlite-rag/import-pack`
- `POST /sqlite-rag/search`

Example import body:

```json
{
  "pack_path": "/data/knowledge-packs/evy-local-emergency-us-ks.zip",
  "require_signature": false
}
```

Example search body:

```json
{
  "query": "storm shelter",
  "top_k": 3,
  "filter_metadata": {
    "category": "emergency"
  }
}
```

## Plus Code Metadata

SMS parsing now preserves Plus Codes as structured location metadata:

```json
{
  "location": {
    "plus_code": "86HVCWC8+R9",
    "normalized": "86HVCWC8+R9",
    "source": "sms_plus_code"
  }
}
```

The parser also adds the normalized code to `plus_codes` and `locations` for compatibility with older callers.

## Validation

Validate the repo sample pack:

```bash
python scripts/validate_knowledge_pack.py --require-signature
```

Validate, import into SQLite, and run a sample search:

```bash
python scripts/validate_knowledge_pack.py --require-signature --import-sqlite --search "boil water"
```

Run retrieval tuning against the sample pack:

```bash
python scripts/tune_llm_rag_prompts.py --llm-url http://127.0.0.1:1
```

Default report:

- `data/lilevy/software_reports/knowledge_pack_validation_report.json`

Sample pack:

- `examples/knowledge_packs/evy_local_emergency_sample/`

Sample tuning cases:

- `examples/evaluation/llm_rag_tuning_cases.json`

Run the focused tests:

```bash
python -m pytest backend/tests/test_knowledge_pack.py backend/tests/test_knowledge_pack_script.py backend/tests/test_sqlite_rag_store.py backend/tests/test_sms_gateway.py -q
```

Run the curated suite:

```bash
python scripts/test_software_suite.py --stage regression
```

## Remaining Work

- Add real pack signing and verification policy.
- Build a sample production-style local emergency pack.
- Add optional embeddings and sqlite-vec vector tables.
- Benchmark SQLite RAG against current Chroma/document-manager search.
- Decide when, or whether, SQLite becomes the default lilEVY RAG backend.
