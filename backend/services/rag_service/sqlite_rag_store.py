"""Optional SQLite-backed local RAG store for EVY.

The first version is deliberately FTS5-first. If sqlite-vec is installed, health
reports that vector search is available, but search remains FTS-compatible until
embeddings are wired in.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.shared.models import RAGResult
from backend.services.rag_service.knowledge_pack import KnowledgePackReader, validate_knowledge_pack


class SQLiteRAGStore:
    """Single-file local RAG store with FTS fallback."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vec_available = False
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    text TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    source_pack_id TEXT,
                    expires_at TEXT,
                    content_hash TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    id UNINDEXED,
                    title,
                    text,
                    category,
                    content='documents',
                    content_rowid='rowid'
                )
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                    INSERT INTO documents_fts(rowid, id, title, text, category)
                    VALUES (new.rowid, new.id, new.title, new.text, new.category);
                END
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, id, title, text, category)
                    VALUES('delete', old.rowid, old.id, old.title, old.text, old.category);
                END
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, id, title, text, category)
                    VALUES('delete', old.rowid, old.id, old.title, old.text, old.category);
                    INSERT INTO documents_fts(rowid, id, title, text, category)
                    VALUES (new.rowid, new.id, new.title, new.text, new.category);
                END
                """
            )
            try:
                import sqlite_vec  # type: ignore

                sqlite_vec.load(conn)
                self.vec_available = True
            except Exception:
                self.vec_available = False

    def import_pack(self, pack_path: str | Path, *, require_signature: bool = False) -> Dict[str, Any]:
        """Validate and import a knowledge pack."""
        validation = validate_knowledge_pack(pack_path, require_signature=require_signature)
        if not validation["valid"]:
            return {"imported": False, "validation": validation, "document_ids": []}

        reader = KnowledgePackReader(pack_path)
        manifest = reader.load_manifest()
        document_ids: List[str] = []
        with self._connect() as conn:
            for document, text in reader.iter_documents(manifest):
                metadata = {
                    **document.metadata,
                    "pack_id": manifest.pack_id,
                    "region": manifest.region,
                    "source_owner": manifest.source_owner,
                    "source_urls": manifest.source_urls,
                }
                conn.execute(
                    """
                    INSERT INTO documents (
                        id, title, text, category, metadata_json, source_pack_id, expires_at, content_hash
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        title=excluded.title,
                        text=excluded.text,
                        category=excluded.category,
                        metadata_json=excluded.metadata_json,
                        source_pack_id=excluded.source_pack_id,
                        expires_at=excluded.expires_at,
                        content_hash=excluded.content_hash
                    """,
                    (
                        document.id,
                        document.title,
                        text,
                        document.category,
                        json.dumps(metadata, sort_keys=True),
                        manifest.pack_id,
                        document.expires_at or manifest.expires_at,
                        document.checksum_sha256,
                    ),
                )
                document_ids.append(document.id)
        return {"imported": True, "validation": validation, "document_ids": document_ids}

    def add_document(
        self,
        doc_id: str,
        text: str,
        *,
        title: str = "",
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (id, title, text, category, metadata_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    text=excluded.text,
                    category=excluded.category,
                    metadata_json=excluded.metadata_json
                """,
                (doc_id, title, text, category, json.dumps(metadata or {}, sort_keys=True)),
            )

    def search(self, query: str, top_k: int = 3, category: Optional[str] = None) -> RAGResult:
        """Search using FTS5, falling back to LIKE if the query is not valid FTS syntax."""
        try:
            return self._fts_search(query, top_k, category)
        except sqlite3.OperationalError:
            return self._like_search(query, top_k, category)

    def _fts_search(self, query: str, top_k: int, category: Optional[str]) -> RAGResult:
        match_query = " ".join(token for token in query.replace('"', " ").split() if token)
        if not match_query:
            return RAGResult(documents=[], scores=[], metadata=[])

        sql = """
            SELECT d.text, d.metadata_json, d.category, d.title, bm25(documents_fts) AS rank
            FROM documents_fts
            JOIN documents d ON d.rowid = documents_fts.rowid
            WHERE documents_fts MATCH ?
        """
        params: List[Any] = [match_query]
        if category:
            sql += " AND d.category = ?"
            params.append(category)
        sql += " ORDER BY rank LIMIT ?"
        params.append(top_k)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return self._rows_to_result(rows, source="sqlite_fts")

    def _like_search(self, query: str, top_k: int, category: Optional[str]) -> RAGResult:
        sql = """
            SELECT text, metadata_json, category, title, 1.0 AS rank
            FROM documents
            WHERE lower(text || ' ' || title || ' ' || category) LIKE ?
        """
        params: List[Any] = [f"%{query.lower()}%"]
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += " LIMIT ?"
        params.append(top_k)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return self._rows_to_result(rows, source="sqlite_like")

    def _rows_to_result(self, rows: List[sqlite3.Row], source: str) -> RAGResult:
        documents: List[str] = []
        scores: List[float] = []
        metadata: List[Dict[str, Any]] = []
        for row in rows:
            documents.append(row["text"])
            rank = float(row["rank"])
            score = 1.0 / (1.0 + max(rank, 0.0))
            scores.append(score)
            row_metadata = json.loads(row["metadata_json"] or "{}")
            row_metadata.update(
                {
                    "category": row["category"],
                    "title": row["title"],
                    "source": source,
                    "vector_available": self.vec_available,
                }
            )
            metadata.append(row_metadata)
        return RAGResult(documents=documents, scores=scores, metadata=metadata)

    def health(self) -> Dict[str, Any]:
        with self._connect() as conn:
            document_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        return {
            "backend": "sqlite",
            "db_path": str(self.db_path),
            "document_count": document_count,
            "fts5_available": True,
            "sqlite_vec_available": self.vec_available,
        }
