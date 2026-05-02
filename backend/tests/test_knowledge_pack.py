"""Tests for EVY knowledge-pack validation."""
import hashlib
import json
import zipfile
from pathlib import Path

from backend.services.rag_service.knowledge_pack import validate_knowledge_pack


def _write_pack(tmp_path: Path, *, checksum: str | None = None, signature: dict | None = None) -> Path:
    pack_dir = tmp_path / "sample-pack"
    docs_dir = pack_dir / "docs"
    docs_dir.mkdir(parents=True)
    text = "Shelter is available at the community center."
    (docs_dir / "shelter.txt").write_text(text, encoding="utf-8")
    checksum = checksum or hashlib.sha256(text.encode("utf-8")).hexdigest()
    manifest = {
        "pack_id": "evy-test-pack",
        "region": "us-test",
        "created_at": "2026-05-02T00:00:00Z",
        "expires_at": "2026-12-31T00:00:00Z",
        "source_owner": "EVY Test",
        "source_urls": ["https://example.invalid/source"],
        "schema_version": "1.0",
        "documents": [
            {
                "id": "shelter",
                "title": "Shelter",
                "category": "emergency",
                "path": "docs/shelter.txt",
                "checksum_sha256": checksum,
            }
        ],
        "signature": signature,
    }
    if signature is None:
        manifest.pop("signature")
    (pack_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return pack_dir


def test_validate_directory_pack_with_missing_signature_warning(tmp_path):
    pack_dir = _write_pack(tmp_path)

    result = validate_knowledge_pack(pack_dir)

    assert result["valid"] is True
    assert result["document_count"] == 1
    assert "signature is missing" in result["warnings"][0]


def test_validate_pack_requires_signature_when_configured(tmp_path):
    pack_dir = _write_pack(tmp_path)

    result = validate_knowledge_pack(pack_dir, require_signature=True)

    assert result["valid"] is False
    assert "signature is required" in result["errors"]


def test_validate_pack_detects_checksum_mismatch(tmp_path):
    pack_dir = _write_pack(tmp_path, checksum="0" * 64)

    result = validate_knowledge_pack(pack_dir)

    assert result["valid"] is False
    assert "checksum mismatch for document shelter" in result["errors"]


def test_validate_zip_pack_with_signature(tmp_path):
    pack_dir = _write_pack(
        tmp_path,
        signature={"type": "development-sha256", "value": "abc123", "key_id": "test-key"},
    )
    zip_path = tmp_path / "sample-pack.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for path in pack_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(pack_dir))

    result = validate_knowledge_pack(zip_path, require_signature=True)

    assert result["valid"] is True
    assert result["document_count"] == 1
