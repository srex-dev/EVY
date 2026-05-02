"""Tests for optional SQLite RAG store."""
import hashlib
import json
from pathlib import Path

from backend.services.rag_service.sqlite_rag_store import SQLiteRAGStore


def _write_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "pack"
    docs_dir = pack_dir / "docs"
    docs_dir.mkdir(parents=True)
    text = "Emergency shelter opens at the north community center after storms."
    (docs_dir / "shelter.txt").write_text(text, encoding="utf-8")
    manifest = {
        "pack_id": "evy-local-emergency",
        "region": "us-test",
        "created_at": "2026-05-02T00:00:00Z",
        "expires_at": "2026-12-31T00:00:00Z",
        "source_owner": "EVY Test",
        "schema_version": "1.0",
        "documents": [
            {
                "id": "storm-shelter",
                "title": "Storm Shelter",
                "category": "emergency",
                "path": "docs/shelter.txt",
                "checksum_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "metadata": {"priority": "high"},
            }
        ],
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return pack_dir


def test_sqlite_store_add_document_and_search(tmp_path):
    store = SQLiteRAGStore(tmp_path / "rag.db")
    store.add_document(
        "water",
        "Boil water before drinking after a flood advisory.",
        title="Water Safety",
        category="health",
    )

    result = store.search("boil water", top_k=2)

    assert result.documents == ["Boil water before drinking after a flood advisory."]
    assert result.metadata[0]["category"] == "health"
    assert result.metadata[0]["source"] == "sqlite_fts"


def test_sqlite_store_imports_knowledge_pack_and_reports_health(tmp_path):
    store = SQLiteRAGStore(tmp_path / "rag.db")
    pack_dir = _write_pack(tmp_path)

    imported = store.import_pack(pack_dir)
    result = store.search("storm shelter", top_k=1, category="emergency")
    health = store.health()

    assert imported["imported"] is True
    assert imported["document_ids"] == ["storm-shelter"]
    assert result.documents
    assert result.metadata[0]["pack_id"] == "evy-local-emergency"
    assert health["document_count"] == 1
    assert health["fts5_available"] is True
    assert "sqlite_vec_available" in health


def test_sqlite_store_rejects_invalid_pack(tmp_path):
    store = SQLiteRAGStore(tmp_path / "rag.db")
    pack_dir = tmp_path / "bad-pack"
    pack_dir.mkdir()
    (pack_dir / "manifest.json").write_text("{}", encoding="utf-8")

    imported = store.import_pack(pack_dir)

    assert imported["imported"] is False
    assert imported["validation"]["valid"] is False
