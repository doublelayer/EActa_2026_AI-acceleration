#!/usr/bin/env python3
"""Create a complete text-and-annotations review record from a versioned DOCX.

The historical filename is retained for compatibility. Each output contains a
text projection of the complete document body, inline tracked insertions and
deletions, and every embedded Word comment with its paragraph anchor.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "article"
DOCX_DIR = ARTICLE / "manuscript_versions"
DEFAULT_OUTPUT = ARTICLE / "reviews"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WORD_NS}
TAG = lambda name: f"{{{WORD_NS}}}{name}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markup_text(element: ET.Element) -> str:
    """Render Word text while explicitly preserving insertion/deletion markup."""
    chunks: list[str] = []

    def append(node: ET.Element) -> None:
        if node.tag in {TAG("ins"), TAG("del")}:
            kind = "INSERT" if node.tag == TAG("ins") else "DELETE"
            revision_id = node.attrib.get(TAG("id"), "?")
            author = node.attrib.get(TAG("author"), "not recorded")
            date = node.attrib.get(TAG("date"), "not recorded")
            payload: list[str] = []
            for child in node:
                before = len(chunks)
                append(child)
                payload.extend(chunks[before:])
                del chunks[before:]
            text = "".join(payload)
            chunks.append(f"[[{kind} id={revision_id}; author={author}; date={date}: {text}]]")
        elif node.tag in {TAG("t"), TAG("delText")}:
            chunks.append(node.text or "")
        elif node.tag == TAG("tab"):
            chunks.append("\t")
        elif node.tag in {TAG("br"), TAG("cr")}:
            chunks.append("\n")
        elif node.tag == TAG("drawing"):
            chunks.append("[embedded figure/image]")
        elif node.tag == TAG("object"):
            chunks.append("[embedded object]")
        else:
            for child in node:
                append(child)

    append(element)
    return "".join(chunks)


def story_parts(archive: zipfile.ZipFile) -> list[str]:
    names = set(archive.namelist())
    ordered = ["word/document.xml"] if "word/document.xml" in names else []
    for fixed in ("word/footnotes.xml", "word/endnotes.xml"):
        if fixed in names:
            ordered.append(fixed)
    extras = [
        name
        for name in names
        if re.fullmatch(r"word/(?:header|footer)\d+\.xml", name)
    ]
    ordered.extend(sorted(extras, key=lambda value: (value.split("/")[-1].rstrip(".xml"), value)))
    return ordered


def body_transcript(archive: zipfile.ZipFile) -> tuple[str, int]:
    """Return ordered visible text from the document and other text stories."""
    blocks: list[str] = []
    paragraph_count = 0
    for part in story_parts(archive):
        root = ET.fromstring(archive.read(part))
        paragraphs = root.findall(".//w:p", NS)
        if not paragraphs:
            continue
        if part != "word/document.xml":
            blocks.extend([f"[{part}]", ""])
        for paragraph in paragraphs:
            paragraph_count += 1
            text = markup_text(paragraph)
            if text.strip():
                blocks.append(f"P{paragraph_count:05d}  {text}")
            else:
                blocks.append(f"P{paragraph_count:05d}")
        blocks.append("")
    return "\n".join(blocks).rstrip(), paragraph_count


def comment_anchors(document: ET.Element, comment_id: str) -> list[str]:
    matches: list[str] = []
    marker_tags = {TAG("commentRangeStart"), TAG("commentRangeEnd"), TAG("commentReference")}
    parents = {child: parent for parent in document.iter() for child in parent}
    containers: list[ET.Element] = []
    for marker in document.iter():
        if marker.tag not in marker_tags or marker.attrib.get(TAG("id")) != comment_id:
            continue
        ancestor = parents.get(marker)
        while ancestor is not None:
            if ancestor.tag == TAG("p"):
                containers.append(ancestor)
                break
            if ancestor.tag in {TAG("sdt"), TAG("sdtContent")}:
                if ancestor.findall(".//w:p", NS):
                    containers.append(ancestor)
                    break
            ancestor = parents.get(ancestor)

    for container in containers:
        text = markup_text(container)
        if text and text not in matches:
            matches.append(text)
    return matches


def fence_for(text: str) -> str:
    longest = max((len(run) for run in re.findall(r"~+", text)), default=0)
    return "~" * max(5, longest + 1)


def export(docx: Path, output_dir: Path, overwrite: bool = False) -> Path:
    docx = docx.resolve()
    archive_root = DOCX_DIR.resolve()
    try:
        docx.relative_to(archive_root)
    except ValueError as exc:
        raise ValueError(
            f"Reviewed DOCX must be its versioned file under article/manuscript_versions/: {docx}"
        ) from exc

    version_match = re.search(r"_v(\d+)\.docx$", docx.name, re.IGNORECASE)
    if not version_match:
        raise ValueError(f"Cannot determine version from {docx.name}")
    version = version_match.group(1)

    with zipfile.ZipFile(docx) as archive:
        document_xml = archive.read("word/document.xml")
        document_root = ET.fromstring(document_xml)
        body_text, paragraph_count = body_transcript(archive)
        comments_xml = archive.read("word/comments.xml") if "word/comments.xml" in archive.namelist() else None
        comments_root = ET.fromstring(comments_xml) if comments_xml is not None else None
        comments = comments_root.findall(".//w:comment", NS) if comments_root is not None else []
        insertions = document_root.findall(".//w:ins", NS)
        deletions = document_root.findall(".//w:del", NS)

    author_counts: Counter[str] = Counter()
    for change in [*insertions, *deletions]:
        author_counts[change.attrib.get(TAG("author"), "(not recorded)")] += 1

    comments_hash = hashlib.sha256(comments_xml).hexdigest() if comments_xml is not None else "none"
    lines = [
        f"# DOCX review record for manuscript version {version}",
        "",
        "This record preserves a text projection of the complete archived DOCX, including inline tracked insertions and deletions, followed by all embedded Word comments and their anchor paragraphs. The source DOCX remains authoritative for page layout and visual details; embedded figures are marked in the text projection.",
        "",
        f"- Source DOCX: `{Path(os.path.relpath(docx, output_dir.resolve())).as_posix()}`",
        f"- Source DOCX SHA-256: `{sha256(docx)}`",
        f"- Embedded document XML SHA-256: `{hashlib.sha256(document_xml).hexdigest()}`",
        f"- Embedded comments XML SHA-256: `{comments_hash}`",
        f"- DOCX text paragraphs: {paragraph_count}",
        f"- DOCX text projection SHA-256: `{hashlib.sha256(body_text.encode('utf-8')).hexdigest()}`",
        f"- Word review comments: {len(comments)}",
        f"- Tracked insertions: {len(insertions)}",
        f"- Tracked deletions: {len(deletions)}",
        "",
        "## Full DOCX text and tracked changes",
        "",
        "Each paragraph is shown in document order. `[[INSERT ...]]` and `[[DELETE ...]]` retain the revision text, Word revision ID, author, and timestamp.",
        "",
    ]
    fence = fence_for(body_text)
    lines.extend([
        f"{fence}text",
        "<!-- BEGIN FULL DOCX TEXT -->",
        body_text,
        "<!-- END FULL DOCX TEXT -->",
        fence,
        "",
        "## Tracked-change authors",
        "",
    ])
    if author_counts:
        lines.extend(f"- {author}: {count} tracked insertions/deletions" for author, count in sorted(author_counts.items()))
    else:
        lines.append("No tracked insertions or deletions were embedded in the DOCX.")
    lines.extend(["", "## Word comments", ""])

    for comment in comments:
        comment_id = comment.attrib.get(TAG("id"), "")
        author = comment.attrib.get(TAG("author"), "")
        timestamp = comment.attrib.get(TAG("date"), "")
        body = markup_text(comment)
        anchors = comment_anchors(document_root, comment_id)
        fence = fence_for(body + "".join(anchors))
        lines.extend(
            [
                f"### DOCX-v{version}-C{comment_id}",
                "",
                f"- Author: {author or '(not recorded)'}",
                f"- Timestamp: {timestamp or '(not recorded)'}",
            ]
        )
        if anchors:
            lines.extend(["- Anchored paragraph(s):", "", f"{fence}text", *anchors, fence])
        else:
            lines.append("- Anchored paragraph: no comment range or reference paragraph found.")
        lines.extend(["", "- Comment text:", "", f"{fence}text", body, fence, ""])
    if not comments:
        lines.append("No Word comments were embedded in this DOCX.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"review_v{version}.md"
    content = "\n".join(lines).rstrip() + "\n"
    if output.exists():
        if output.read_text(encoding="utf-8") == content:
            return output
        if not overwrite:
            raise FileExistsError(
                f"Refusing to overwrite {output}; inspect it or rerun with --overwrite."
            )
    output.write_text(content, encoding="utf-8", newline="\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--docx",
        type=Path,
        help="The versioned DOCX in article/manuscript_versions/; version comes from its filename.",
    )
    parser.add_argument("--versions", nargs="*", help="Optional version numbers to export")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing DOCX review record after inspecting the source changes.",
    )
    args = parser.parse_args()

    wanted = {str(value) for value in args.versions} if args.versions else None
    exported = 0
    if args.docx:
        docx = args.docx if args.docx.is_absolute() else ROOT / args.docx
        output = export(docx, args.output_dir, overwrite=args.overwrite)
        print(output.relative_to(ROOT))
        exported += 1
    else:
        for docx in sorted(DOCX_DIR.glob("*.docx")):
            match = re.search(r"_v(\d+)\.docx$", docx.name, re.IGNORECASE)
            if not match or (wanted is not None and match.group(1) not in wanted):
                continue
            output = export(docx, args.output_dir, overwrite=args.overwrite)
            print(output.relative_to(ROOT))
            exported += 1

    print(f"Exported {exported} complete DOCX review record(s).")


if __name__ == "__main__":
    main()
