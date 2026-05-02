"""Knowledge pack schema and validation helpers for EVY local RAG."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError


MANIFEST_NAME = "manifest.json"


class KnowledgePackDocument(BaseModel):
    """Single document entry inside a knowledge pack manifest."""

    id: str
    title: str = ""
    category: str = "general"
    path: Optional[str] = None
    text: Optional[str] = None
    checksum_sha256: Optional[str] = None
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgePackSignature(BaseModel):
    """Detached signature metadata placeholder for v1 knowledge packs."""

    type: str
    value: str
    key_id: Optional[str] = None


class KnowledgePackManifest(BaseModel):
    """Stable v1 manifest for EVY signed knowledge packs."""

    pack_id: str
    region: str
    created_at: str
    expires_at: str
    source_owner: str
    source_urls: List[str] = Field(default_factory=list)
    schema_version: str = "1.0"
    content_hash: Optional[str] = None
    emergency_priority: str = "normal"
    documents: List[KnowledgePackDocument]
    signature: Optional[KnowledgePackSignature] = None


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_datetime(value: str, field_name: str) -> Optional[str]:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return None
    except ValueError:
        return f"{field_name} must be an ISO-8601 datetime"


class KnowledgePackReader:
    """Read knowledge packs from a directory or zip file."""

    def __init__(self, pack_path: str | Path):
        self.pack_path = Path(pack_path)

    def read_text(self, relative_path: str) -> str:
        data = self.read_bytes(relative_path)
        return data.decode("utf-8")

    def read_bytes(self, relative_path: str) -> bytes:
        normalized = relative_path.replace("\\", "/").lstrip("/")
        if self.pack_path.is_dir():
            target = (self.pack_path / normalized).resolve()
            root = self.pack_path.resolve()
            try:
                target.relative_to(root)
            except ValueError:
                raise ValueError(f"Pack path escapes root: {relative_path}")
            return target.read_bytes()
        if zipfile.is_zipfile(self.pack_path):
            with zipfile.ZipFile(self.pack_path) as zf:
                return zf.read(normalized)
        raise ValueError(f"Knowledge pack must be a directory or zip file: {self.pack_path}")

    def load_manifest(self) -> KnowledgePackManifest:
        raw = self.read_text(MANIFEST_NAME)
        return KnowledgePackManifest.model_validate_json(raw)

    def iter_documents(self, manifest: KnowledgePackManifest) -> Iterable[Tuple[KnowledgePackDocument, str]]:
        for document in manifest.documents:
            if document.text is not None:
                text = document.text
            elif document.path:
                text = self.read_text(document.path)
            else:
                raise ValueError(f"Document {document.id} must define text or path")
            yield document, text


def compute_manifest_content_hash(reader: KnowledgePackReader, manifest: KnowledgePackManifest) -> str:
    """Compute stable hash across document IDs, text, and per-doc checksums."""
    digest = hashlib.sha256()
    for document, text in reader.iter_documents(manifest):
        digest.update(document.id.encode("utf-8"))
        digest.update(b"\0")
        digest.update(text.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def validate_knowledge_pack(
    pack_path: str | Path,
    *,
    require_signature: bool = False,
) -> Dict[str, Any]:
    """Validate manifest shape, document checksums, expiration fields, and signature presence."""
    errors: List[str] = []
    warnings: List[str] = []
    reader = KnowledgePackReader(pack_path)
    manifest: Optional[KnowledgePackManifest] = None

    try:
        manifest = reader.load_manifest()
    except (FileNotFoundError, KeyError, ValidationError, ValueError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "pack_path": str(pack_path),
            "errors": [f"Failed to load manifest: {exc}"],
            "warnings": [],
            "manifest": None,
        }

    for field_name in ("created_at", "expires_at"):
        error = _parse_datetime(getattr(manifest, field_name), field_name)
        if error:
            errors.append(error)

    if require_signature and manifest.signature is None:
        errors.append("signature is required")
    elif manifest.signature is None:
        warnings.append("signature is missing; pack is allowed only for development/import tests")

    document_count = 0
    try:
        for document, text in reader.iter_documents(manifest):
            document_count += 1
            if document.expires_at:
                error = _parse_datetime(document.expires_at, f"documents[{document.id}].expires_at")
                if error:
                    errors.append(error)
            if document.checksum_sha256:
                actual = _sha256_bytes(text.encode("utf-8"))
                if actual != document.checksum_sha256:
                    errors.append(f"checksum mismatch for document {document.id}")
    except Exception as exc:
        errors.append(str(exc))

    if manifest.content_hash:
        try:
            actual_content_hash = compute_manifest_content_hash(reader, manifest)
            if actual_content_hash != manifest.content_hash:
                errors.append("manifest content_hash does not match document content")
        except Exception as exc:
            errors.append(f"failed to compute content_hash: {exc}")

    return {
        "valid": not errors,
        "pack_path": str(pack_path),
        "errors": errors,
        "warnings": warnings,
        "document_count": document_count,
        "manifest": manifest.model_dump(mode="json"),
    }
