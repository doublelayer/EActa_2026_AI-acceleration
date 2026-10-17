# Full DOCX review records by manuscript version

Every archived manuscript version has a `review_vN.md` source record. It contains a text projection of the complete DOCX, with tracked insertions and deletions marked inline, followed by all embedded Word comments and their anchor paragraphs. The DOCX remains authoritative for layout and figures; inspect it and its versioned image resources when reviewing visual content.

The archive was transcribed on 2026-10-17. Comment counts and tracked-change counts below describe markup found in each source DOCX. Tracked changes are not Word comment threads and should not be mislabeled as reviewer comments. Their text, author, timestamp, and Word revision ID are preserved inline in the full text projection.

| Version | Word comments | Tracked insertions | Tracked deletions | Comment IDs | Full-DOCX review record |
|---|---:|---:|---:|---|---|
| v28 | 0 | 0 | 0 | None | [`review_v28.md`](review_v28.md) |
| v29 | 0 | 0 | 0 | None | [`review_v29.md`](review_v29.md) |
| v30 | 0 | 418 | 426 | None | [`review_v30.md`](review_v30.md) |
| v31 | 0 | 0 | 0 | None | [`review_v31.md`](review_v31.md) |
| v32 | 0 | 0 | 0 | None | [`review_v32.md`](review_v32.md) |
| v33 | 0 | 0 | 0 | None | [`review_v33.md`](review_v33.md) |
| v34 | 0 | 0 | 0 | None | [`review_v34.md`](review_v34.md) |
| v35 | 22 | 34 | 31 | `DOCX-v35-C0` through `DOCX-v35-C21` | [`review_v35.md`](review_v35.md) |
| v36 | 0 | 0 | 0 | None | [`review_v36.md`](review_v36.md) |
| v37 | 4 | 19 | 13 | `DOCX-v37-C0` through `DOCX-v37-C3` | [`review_v37.md`](review_v37.md) |
| v38 | 0 | 0 | 0 | None | [`review_v38.md`](review_v38.md) |
| v39 | 0 | 310 | 310 | None | [`review_v39.md`](review_v39.md) |
| v40 | 0 | 336 | 335 | None | [`review_v40.md`](review_v40.md) |
| v41 | 0 | 337 | 335 | None | [`review_v41.md`](review_v41.md) |
| v42 | 0 | 321 | 323 | None | [`review_v42.md`](review_v42.md) |
| v43 | 1 | 40 | 27 | `DOCX-v43-C37` | [`review_v43.md`](review_v43.md) |
| v44 | 0 | 21 | 24 | None | [`review_v44.md`](review_v44.md) |
| v45 | 0 | 2 | 4 | None | [`review_v45.md`](review_v45.md) |
| v46 | 0 | 0 | 0 | None | [`review_v46.md`](review_v46.md) |
| v47 | 12 | 82 | 59 | `DOCX-v47-C0` through `DOCX-v47-C11` | [`review_v47.md`](review_v47.md) |
| v48 | 2 | 0 | 0 | `DOCX-v48-C0` through `DOCX-v48-C1` | [`review_v48.md`](review_v48.md) |
| v49 | 13 | 106 | 81 | `DOCX-v49-C0` through `DOCX-v49-C12` | [`review_v49.md`](review_v49.md) |
| v52 | 0 | 89 | 84 | None | [`review_v52.md`](review_v52.md) |
| v53 | 0 | 0 | 0 | None | [`review_v53.md`](review_v53.md) |

**Total Word review comments: 54 across 24 full-DOCX review records.** The records also preserve 2,115 tracked insertions and 2,052 tracked deletions. v52 has no Word comment threads, but it does have 89 insertions and 84 deletions; those are included in [`review_v52.md`](review_v52.md). These counts describe archived markup; they are not new reviewer feedback.

## Workflow for new versions

When a versioned DOCX is first archived, create its full-DOCX review record with:

```powershell
python tools/extract_docx_comments.py --docx article/manuscript_versions/Electrochimica_Acta_research_article_draft_vN.docx
```

The historical script name is retained. It writes the entire document text with tracked insertions/deletions marked inline, then all Word comments with their authors, timestamps, and anchored paragraphs. Add the generated review path to `article/version_index.md`, and update this index with comment and revision counts.

Reviewers may comment on the DOCX in Google Drive or another review service. Before the next version starts, replace the matching archived DOCX with the reviewed copy. Regenerate the same record with `--overwrite`, inspect the changed transcript, and refresh both indexes. If there are no comments, the full-DOCX record still exists and reports zero comments; it also preserves tracked changes when present.

The next generation run reads the latest version's Markdown draft, paired reviewed DOCX, and `review_vN.md`, every `UNRESOLVED` item in that version's `Review-item dispositions` block in `version_index.md`, plus applicable user-supplied reviews. Import those indexed items into the fresh run ledger; the version index must supply their IDs, requests, open reasons, and provenance so no previous run folder is required. The ledger also covers every Word comment, tracked insertion/deletion, and reviewer text change in the DOCX relative to the Markdown. Preserve Word IDs; assign stable `DOCX-DIFF-Pxxx` IDs to unmarked text deltas. Decide and record each item's disposition; only the resulting review-driven changes enter the next Markdown/DOCX pair. Keep comments distinct from tracked edits. Older records remain for provenance and are consulted only when a current item points to them. Preserve user-supplied review files byte-for-byte. Do not create persistent release-review or prior-run handoff files.
