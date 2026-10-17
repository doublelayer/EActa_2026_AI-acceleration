#!/usr/bin/env python3
"""Verify indexed article versions, image references, and review exports."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from extract_docx_comments import body_transcript


ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "article"
INDEX = ARTICLE / "version_index.md"
HASH_RE = re.compile(r"SHA-256 `([0-9a-fA-F]{64})`")
LINK_RE = re.compile(r"\]\(([^)]+)\)")
VERSION_RE = re.compile(r"^### Version (\d+)\s*$")
IMAGE_RE = re.compile(r"^\s*-\s*`([^`]+\.png)`\s*\(SHA-256 `([0-9a-fA-F]{64})`\)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def resolve_index_path(value: str) -> Path:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", value):
        raise ValueError(f"URL is not a local archive artifact: {value}")
    path = (ARTICLE / value.replace("/", "/")).resolve()
    if path != ARTICLE.resolve() and ARTICLE.resolve() not in path.parents:
        raise ValueError(f"Indexed path escapes article/: {value}")
    return path


def main() -> int:
    if not INDEX.is_file():
        print(f"FAIL: missing version index: {INDEX}", file=sys.stderr)
        return 1

    errors: list[str] = []
    checked: dict[Path, str] = {}
    indexed_sources: set[str] = set()
    version_entries: dict[int, dict[str, object]] = {}
    current_version: int | None = None

    for line_number, line in enumerate(INDEX.read_text(encoding="utf-8").splitlines(), start=1):
        heading = VERSION_RE.match(line)
        if heading:
            current_version = int(heading.group(1))
            version_entries.setdefault(current_version, {"images": {}, "draft": None, "source": None})
            continue
        if line.startswith("### ") or line.startswith("## "):
            current_version = None

        hash_match = HASH_RE.search(line)
        if not hash_match:
            continue
        expected = hash_match.group(1).lower()
        link_match = LINK_RE.search(line)

        if current_version is not None and not link_match:
            image_match = IMAGE_RE.match(line)
            if not image_match:
                errors.append(f"version_index.md:{line_number}: hash has no artifact path")
                continue
            name, expected = image_match.group(1), image_match.group(2).lower()
            relative = f"article_resources/v{current_version}/{name}"
            version_entries[current_version]["images"][relative] = expected
            artifact_path = resolve_index_path(relative)
        elif link_match:
            relative = link_match.group(1)
            try:
                artifact_path = resolve_index_path(relative)
            except ValueError as exc:
                errors.append(f"version_index.md:{line_number}: {exc}")
                continue
            if current_version is not None:
                entry = version_entries[current_version]
                if line.lstrip().startswith("- Source DOCX:"):
                    entry["source"] = relative
                    indexed_sources.add(Path(relative).name)
                elif line.lstrip().startswith("- Reconstructed draft:"):
                    entry["draft"] = relative
        else:
            errors.append(f"version_index.md:{line_number}: SHA-256 has no local path")
            continue

        if artifact_path in checked and checked[artifact_path] != expected:
            errors.append(f"version_index.md:{line_number}: conflicting hashes for {relative}")
        checked[artifact_path] = expected

    if not version_entries:
        errors.append("version_index.md contains no version sections")

    for path, expected in checked.items():
        if not path.is_file():
            errors.append(f"missing indexed file: {path.relative_to(ARTICLE)}")
            continue
        actual = digest(path)
        if actual != expected:
            errors.append(
                f"hash mismatch: {path.relative_to(ARTICLE)} expected {expected}, got {actual}"
            )

    indexed_docx = sorted(indexed_sources)
    actual_docx = sorted(path.name for path in (ARTICLE / "manuscript_versions").glob("*.docx"))
    if indexed_docx != actual_docx:
        missing = sorted(set(actual_docx) - set(indexed_docx))
        absent = sorted(set(indexed_docx) - set(actual_docx))
        if missing:
            errors.append(f"DOCX files missing from version index: {', '.join(missing)}")
        if absent:
            errors.append(f"indexed DOCX files missing from archive: {', '.join(absent)}")

    image_count = 0
    for version, entry in sorted(version_entries.items()):
        draft_relative = entry["draft"]
        if not isinstance(draft_relative, str):
            errors.append(f"v{version}: no reconstructed draft link in version index")
            continue
        draft = resolve_index_path(draft_relative)
        if not draft.is_file():
            continue
        referenced: set[str] = set()
        for target in MARKDOWN_IMAGE_RE.findall(draft.read_text(encoding="utf-8")):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target):
                errors.append(f"v{version}: external image reference in draft: {target}")
                continue
            image_path = (draft.parent / target).resolve()
            try:
                relative = image_path.relative_to(ARTICLE.resolve()).as_posix()
            except ValueError:
                errors.append(f"v{version}: image path escapes article/: {target}")
                continue
            prefix = f"article_resources/v{version}/"
            if not relative.startswith(prefix):
                errors.append(f"v{version}: image is outside its version folder: {relative}")
            referenced.add(relative)

        indexed_images = set(entry["images"])
        if referenced != indexed_images:
            errors.append(
                f"v{version}: draft/index image mismatch; unindexed refs={sorted(referenced-indexed_images)}, "
                f"unreferenced index entries={sorted(indexed_images-referenced)}"
            )

        resource_dir = ARTICLE / "article_resources" / f"v{version}"
        if not resource_dir.is_dir():
            errors.append(f"v{version}: missing resource folder")
            continue
        actual_images = {
            path.relative_to(ARTICLE).as_posix()
            for path in resource_dir.iterdir()
            if path.is_file()
        }
        if actual_images != referenced:
            errors.append(
                f"v{version}: resource folder does not equal draft references; "
                f"missing={sorted(referenced-actual_images)}, extra={sorted(actual_images-referenced)}"
            )
        image_count += len(referenced)

    review_exports = sorted((ARTICLE / "reviews").glob("review_v*.md"))
    review_total = 0
    insertion_total = 0
    deletion_total = 0
    exported_versions: set[int] = set()
    for export in review_exports:
        text = export.read_text(encoding="utf-8")
        filename_version = re.fullmatch(r"review_v(\d+)\.md", export.name)
        if not filename_version:
            errors.append(f"invalid versioned review filename: {export.name}")
            continue
        version = int(filename_version.group(1))
        exported_ids = {
            (int(comment_version), comment_id)
            for comment_version, comment_id in re.findall(
                r"^### DOCX-v(\d+)-C(\d+)\s*$", text, flags=re.MULTILINE
            )
        }
        count = len(exported_ids)
        declared = re.search(r"^- Word review comments: (\d+)\s*$", text, flags=re.MULTILINE)
        if not declared or count != int(declared.group(1)):
            errors.append(f"review comment count mismatch in {export.relative_to(ARTICLE)}")
        if any(comment_version != version for comment_version, _ in exported_ids):
            errors.append(f"review IDs do not match the version in {export.relative_to(ARTICLE)}")
        review_total += count
        exported_versions.add(version)

        source_ref = re.search(r"^- Source DOCX: `([^`]+)`\s*$", text, flags=re.MULTILINE)
        source_hash = re.search(
            r"^- Source DOCX SHA-256: `([0-9a-fA-F]{64})`\s*$", text, flags=re.MULTILINE
        )
        document_hash = re.search(
            r"^- Embedded document XML SHA-256: `([0-9a-fA-F]{64})`\s*$",
            text,
            flags=re.MULTILINE,
        )
        comments_hash = re.search(
            r"^- Embedded comments XML SHA-256: `(none|[0-9a-fA-F]{64})`\s*$",
            text,
            flags=re.MULTILINE,
        )
        projection_hash = re.search(
            r"^- DOCX text projection SHA-256: `([0-9a-fA-F]{64})`\s*$",
            text,
            flags=re.MULTILINE,
        )
        paragraph_declared = re.search(r"^- DOCX text paragraphs: (\d+)\s*$", text, flags=re.MULTILINE)
        insertion_declared = re.search(r"^- Tracked insertions: (\d+)\s*$", text, flags=re.MULTILINE)
        deletion_declared = re.search(r"^- Tracked deletions: (\d+)\s*$", text, flags=re.MULTILINE)
        if not all((source_ref, source_hash, document_hash, comments_hash, projection_hash,
                    paragraph_declared, insertion_declared, deletion_declared)):
            errors.append(f"missing full-DOCX provenance in {export.relative_to(ARTICLE)}")
            continue
        insertion_total += int(insertion_declared.group(1))
        deletion_total += int(deletion_declared.group(1))
        source_path = (export.parent / source_ref.group(1)).resolve()
        try:
            source_path.relative_to(ARTICLE.resolve())
        except ValueError:
            errors.append(f"review source DOCX escapes article/: {source_path}")
            continue
        if not source_path.is_file():
            errors.append(f"missing review source DOCX: {source_path}")
            continue
        if digest(source_path) != source_hash.group(1).lower():
            errors.append(f"source DOCX hash mismatch in {export.relative_to(ARTICLE)}")
            continue
        if source_path not in checked or checked[source_path] != source_hash.group(1).lower():
            errors.append(f"review source DOCX is not hash-indexed in version_index.md: {source_path.relative_to(ARTICLE)}")
            continue

        version_match = re.search(r"_v(\d+)\.docx$", source_path.name, re.IGNORECASE)
        if (
            not source_path.is_relative_to(ARTICLE / "manuscript_versions")
            or not version_match
            or int(version_match.group(1)) != version
        ):
            errors.append(f"review source version mismatch in {export.relative_to(ARTICLE)}")
            continue

        try:
            with ZipFile(source_path) as archive:
                document_xml = archive.read("word/document.xml")
                comments_xml = archive.read("word/comments.xml") if "word/comments.xml" in archive.namelist() else None
                comments_root = ET.fromstring(comments_xml) if comments_xml is not None else None
                document_root = ET.fromstring(document_xml)
                projection, paragraph_count = body_transcript(archive)
        except (KeyError, OSError, ET.ParseError) as exc:
            errors.append(f"cannot read full DOCX review source {source_path.name}: {exc}")
            continue

        actual_doc_hash = hashlib.sha256(document_xml).hexdigest()
        if actual_doc_hash != document_hash.group(1).lower():
            errors.append(f"document XML hash mismatch in {export.relative_to(ARTICLE)}")
        actual_comments_hash = hashlib.sha256(comments_xml).hexdigest() if comments_xml is not None else "none"
        if actual_comments_hash != comments_hash.group(1).lower():
            errors.append(f"comments XML hash mismatch in {export.relative_to(ARTICLE)}")
        if paragraph_count != int(paragraph_declared.group(1)):
            errors.append(f"DOCX paragraph count mismatch in {export.relative_to(ARTICLE)}")
        actual_insertions = len(document_root.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ins"))
        actual_deletions = len(document_root.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}del"))
        if actual_insertions != int(insertion_declared.group(1)):
            errors.append(f"tracked insertion count mismatch in {export.relative_to(ARTICLE)}")
        if actual_deletions != int(deletion_declared.group(1)):
            errors.append(f"tracked deletion count mismatch in {export.relative_to(ARTICLE)}")
        if hashlib.sha256(projection.encode("utf-8")).hexdigest() != projection_hash.group(1).lower():
            errors.append(f"DOCX text projection hash mismatch in {export.relative_to(ARTICLE)}")
        transcript = re.search(
            r"^<!-- BEGIN FULL DOCX TEXT -->\n(.*?)\n<!-- END FULL DOCX TEXT -->$",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        if not transcript or transcript.group(1) != projection:
            errors.append(f"full DOCX text is missing or changed in {export.relative_to(ARTICLE)}")

        source_comments = comments_root.findall(".//w:comment", {"w": WORD_NS}) if comments_root is not None else []
        source_ids = {
            (version, comment.attrib.get(f"{{{WORD_NS}}}id", ""))
            for comment in source_comments
        }
        if source_ids != exported_ids:
            errors.append(
                f"review comment ID mismatch in {export.relative_to(ARTICLE)}; "
                f"missing={sorted(source_ids-exported_ids)}, extra={sorted(exported_ids-source_ids)}"
            )

    for source_name in indexed_sources:
        version_match = re.search(r"_v(\d+)\.docx$", source_name, flags=re.IGNORECASE)
        if version_match and int(version_match.group(1)) not in exported_versions:
            errors.append(f"versioned DOCX has no full-DOCX review record: {source_name}")

    review_index = ARTICLE / "reviews" / "review_index.md"
    if review_index.is_file():
        declared_total = re.search(
            r"\*\*Total Word review comments: (\d+) across (\d+) full-DOCX review records\.\*\*",
            review_index.read_text(encoding="utf-8"),
        )
        if (
            not declared_total
            or review_total != int(declared_total.group(1))
            or len(review_exports) != int(declared_total.group(2))
        ):
            errors.append(
                f"review index totals do not match {review_total} comments in {len(review_exports)} full-DOCX review records"
            )

    if errors:
        print(f"FAIL: {len(errors)} archive integrity issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"PASS: {len(version_entries)} indexed versions, {len(indexed_docx)} DOCX files, "
        f"{image_count} referenced images, {len(checked)} indexed file hashes, "
        f"{review_total} Word review comments and {insertion_total} tracked insertions/"
        f"{deletion_total} tracked deletions across {len(review_exports)} full-DOCX review records."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
