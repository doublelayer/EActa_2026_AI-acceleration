#!/usr/bin/env python3
"""Create a complete text-and-annotations review record from a versioned DOCX.

The historical filename is retained for compatibility. Each output contains a
text projection of the complete document body, native Word equations rendered
with explicit scripts, inline tracked insertions and deletions, and every
embedded Word comment with its paragraph anchor.
"""

from __future__ import annotations

import argparse
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
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": WORD_NS, "m": MATH_NS}
TAG = lambda name: f"{{{WORD_NS}}}{name}"
MATH_TAG = lambda name: f"{{{MATH_NS}}}{name}"


def child_named_from(element: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in element if child.tag == MATH_TAG(name)), None)


def revision_markup(element: ET.Element, text: str) -> str:
    """Wrap revision text with the Word metadata used in the review transcript."""
    kind = "INSERT" if element.tag == TAG("ins") else "DELETE"
    revision_id = element.attrib.get(TAG("id"), "?")
    author = element.attrib.get(TAG("author"), "not recorded")
    date = element.attrib.get(TAG("date"), "not recorded")
    return f"[[{kind} id={revision_id}; author={author}; date={date}: {text}]]"


def unsupported_math_markup(
    element: ET.Element, detail: str = "", content: str | None = None
) -> str:
    """Keep unknown math structures visible with their tag, attributes, and text."""
    local_name = element.tag.rsplit("}", 1)[-1]
    attributes = []
    for key, value in element.attrib.items():
        if key.startswith(f"{{{MATH_NS}}}"):
            attribute_name = f"m:{key.rsplit('}', 1)[-1]}"
        elif key.startswith(f"{{{WORD_NS}}}"):
            attribute_name = f"w:{key.rsplit('}', 1)[-1]}"
        else:
            attribute_name = key
        attributes.append(f"{attribute_name}={value}")
    metadata = "; ".join(part for part in [detail, *attributes] if part)
    suffix = f" {metadata}" if metadata else ""
    if content is None:
        content = "".join(math_text(child) for child in element)
    return f"[[UNSUPPORTED MATH m:{local_name}{suffix}: {content}]]"


def math_text(element: ET.Element) -> str:
    """Render native Word math and explicitly flag unsupported structures."""
    if element.tag in {TAG("ins"), TAG("del")}:
        return revision_markup(element, "".join(math_text(child) for child in element))

    local_name = element.tag.rsplit("}", 1)[-1]
    children = list(element)

    if local_name in {"sSub", "sSup", "sSubSup"}:
        base_node = child_named_from(element, "e")
        sub_node = child_named_from(element, "sub")
        sup_node = child_named_from(element, "sup")
        base = math_text(base_node) if base_node is not None else ""
        sub = math_text(sub_node) if sub_node is not None else ""
        sup = math_text(sup_node) if sup_node is not None else ""
        if sub:
            base += f"_{{{sub}}}"
        if sup:
            base += f"^{{{sup}}}"
        return base
    if local_name == "f":
        numerator_node = child_named_from(element, "num")
        denominator_node = child_named_from(element, "den")
        numerator = math_text(numerator_node) if numerator_node is not None else ""
        denominator = math_text(denominator_node) if denominator_node is not None else ""
        if numerator_node is None or denominator_node is None:
            return unsupported_math_markup(
                element,
                "incomplete fraction",
                f"num={numerator}; den={denominator}",
            )

        properties = child_named_from(element, "fPr")
        fraction_type_node = (
            child_named_from(properties, "type") if properties is not None else None
        )
        fraction_type = (
            fraction_type_node.attrib.get(MATH_TAG("val"), "bar")
            if fraction_type_node is not None
            else "bar"
        )
        if fraction_type != "bar":
            return unsupported_math_markup(
                element,
                f"type={fraction_type}",
                f"num={numerator}; den={denominator}",
            )
        return f"\\frac{{{numerator}}}{{{denominator}}}"
    if local_name == "eqArr":
        rows = [math_text(child) for child in children if child.tag == MATH_TAG("e")]
        return "\n".join(rows)
    if local_name == "oMath":

        def has_subscript(child: ET.Element, base_text: str, sub_text: str) -> bool:
            base = child_named_from(child, "e")
            sub = child_named_from(child, "sub")
            return (
                child.tag == MATH_TAG("sSub")
                and base is not None
                and math_text(base) == base_text
                and sub is not None
                and math_text(sub) == sub_text
            )

        def is_numbered_potential(child: ET.Element) -> bool:
            base = child_named_from(child, "e")
            sub = child_named_from(child, "sub")
            return (
                child.tag == MATH_TAG("sSub")
                and base is not None
                and math_text(base) == "U"
                and sub is not None
                and math_text(sub).isdigit()
            )

        numbered_potentials = [
            child
            for child in children
            if is_numbered_potential(child)
        ]
        first_math_child = next(
            (child for child in children if not child.tag.rsplit("}", 1)[-1].endswith("Pr")),
            None,
        )
        potential_numbers = [
            math_text(child_named_from(child, "sub")) for child in numbered_potentials
        ]
        separate_potentials = (
            len(potential_numbers) >= 4
            and potential_numbers[:4] == ["1", "2", "3", "4"]
            and numbered_potentials[0] is first_math_child
        )
        rendered: list[str] = []
        for index, child in enumerate(children):
            starts_second_scaling_relation = (
                has_subscript(child, "β", "O")
                and index + 2 < len(children)
                and math_text(children[index + 1]).strip() == "Δ"
                and has_subscript(children[index + 2], "G", "OOH")
            )
            starts_overpotential_relation = (
                has_subscript(child, "η", "ideal")
                and index > 0
                and "eV" in math_text(children[index - 1])
            )
            if separate_potentials and child in numbered_potentials and rendered:
                rendered[-1] = rendered[-1].rstrip()
                rendered.append("; ")
            elif starts_overpotential_relation and rendered:
                rendered[-1] = rendered[-1].rstrip()
                rendered.append("; ")
            rendered.append(math_text(child))
            if starts_second_scaling_relation:
                rendered.append(";")
        return "".join(rendered)
    if local_name in {"t", "delText"}:
        return element.text or ""
    if local_name.endswith("Pr") or local_name in {"ctrlPr", "jc"}:
        return ""
    if element.tag.startswith(f"{{{MATH_NS}}}") and local_name not in {
        "r",
        "e",
        "num",
        "den",
        "sub",
        "sup",
    }:
        return unsupported_math_markup(element)
    return "".join(math_text(child) for child in children)


def markup_text(element: ET.Element) -> str:
    """Render Word text, native equations, and tracked insertion/deletion markup."""
    chunks: list[str] = []

    def append(node: ET.Element) -> None:
        if node.tag in {TAG("ins"), TAG("del")}:
            payload: list[str] = []
            for child in node:
                before = len(chunks)
                append(child)
                payload.extend(chunks[before:])
                del chunks[before:]
            chunks.append(revision_markup(node, "".join(payload)))
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
        elif node.tag == MATH_TAG("oMath"):
            chunks.append(f"[[MATH: {math_text(node).strip()}]]")
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

    lines = [
        f"# DOCX review record for manuscript version {version}",
        "",
        "This record preserves a text projection of the complete archived DOCX, including readable native Word equations, inline tracked insertions and deletions, and all embedded Word comments with their anchor paragraphs. The source DOCX remains authoritative for page layout and visual details; embedded figures are marked in the text projection.",
        "",
        f"- Source DOCX: `{Path(os.path.relpath(docx, output_dir.resolve())).as_posix()}`",
        f"- DOCX text paragraphs: {paragraph_count}",
        f"- Word review comments: {len(comments)}",
        f"- Tracked insertions: {len(insertions)}",
        f"- Tracked deletions: {len(deletions)}",
        "",
        "## Full DOCX text and tracked changes",
        "",
        "Each paragraph is shown in document order. `[[MATH: ...]]` renders native Word equations in readable linear notation; unsupported math structures are marked `[[UNSUPPORTED MATH ...]]`. `[[INSERT ...]]` and `[[DELETE ...]]` retain the revision text, Word revision ID, author, and timestamp.",
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
