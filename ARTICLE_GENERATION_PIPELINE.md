# Article generation, review, and version update pipeline

This guide describes the ongoing manuscript workflow in `one_prompt_article_v1`. It is a review-driven versioning process: each new version starts from the latest archived draft and resolves review items from its reviewed DOCX. It does not start a new article from scratch.

## Summary of steps

1. Read and verify the latest version's Markdown draft, DOCX, review record, and indexes.
2. After human review, replace that version's archived DOCX with the reviewed copy and extract its text, comments, and tracked changes into `review_vN.md`.
3. Create a run-specific ledger of comments, tracked edits, and direct DOCX text changes relative to the Markdown draft.
4. Resolve only those review items; generate the next numbered Markdown draft and a clean DOCX with aligned article text.
5. Archive the pair and its review record, update both indexes and recorded hash metadata, then verify the archive.

## Detailed workflow

### 1. Establish the current version

Use `one_prompt_article_v1/article/version_index.md` and the files in `article/manuscript_versions/` to identify the highest archived version. Read its Markdown draft in `article/drafts/`, matching DOCX, corresponding `article/reviews/review_vN.md`, and `article/reviews/review_index.md`. Read user-supplied review files when applicable, preserving their names and contents. Run `python tools/verify_article_archive.py` and save the result in a new `inputs/run_.../` folder.

Never reuse a version number. At the time this guide was written, the archive ends at v52, so the next number is v53; determine it from the archive each time rather than relying on this note.

### 2. Import the human review

Reviewers work directly in the versioned DOCX, for example in Google Drive. When review is complete, put the returned DOCX in the repository, replacing the DOCX for that same version. Update its recorded hash as provenance in `article/version_index.md`, then regenerate that version's record:

```powershell
python tools/extract_docx_comments.py --docx article/manuscript_versions/Electrochimica_Acta_research_article_draft_vN.docx --overwrite
```

The `review_vN.md` record preserves the full DOCX text, tracked insertions and deletions, Word comments, and comment anchors. Update the comment/revision counts in `article/reviews/review_index.md` and the corresponding recorded hash in `article/version_index.md` as provenance before starting the next version. Keep `review_vN.md` even when the DOCX contains no comments; it remains the version's source record.

### 3. Turn review markup into a change ledger

Compare the latest Markdown draft with the reviewed DOCX. In the new run's ledger, include:

- Every Word comment, preserving its ID, wording, author/date when available, and anchored passage.
- Every tracked insertion or deletion, preserving its Word revision ID and distinguishing it from a comment.
- Direct reviewer text changes visible in the DOCX compared with the Markdown. Assign stable ledger IDs such as `DOCX-DIFF-P001` when Word provides no ID.

For each item, record the affected passage, requested disposition, exact change made, or reason it remains unresolved. If the intended change is ambiguous, ask the author rather than guessing.

### 4. Resolve review items only

Use the latest Markdown as the editable text base and the reviewed DOCX plus `review_vN.md` as the review source. Make only changes needed to resolve the current items and local coherence affected by those changes. Do not add unrelated claims, sections, citations, analyses, figures, or stylistic rewrites. Consult registered scientific sources only when an item requires factual verification. If an item needs unsupported new evidence, analysis, or an author decision, mark it unresolved and ask the author.

If there are no actionable review items, carry the text forward unchanged into the next numbered version and report that no review-driven content changes were needed. Reuse the latest version's image resources for routine revisions; do not rerun notebooks or calculations unless a specific authorized review item requires it.

### 5. Generate the next version

Save the next editable draft as `article/drafts/article_draft_vN.md`. Generate `article/manuscript_versions/Electrochimica_Acta_research_article_draft_vN.docx` from that Markdown. Their article text must align at generation. The new DOCX should be clean of carried-over comments and tracked revisions; the source review and dispositions remain in the review record and run ledger.

Create `article/reviews/review_vN.md` from the generated DOCX. Keep only image assets used by that version in `article/article_resources/vN/`. Add the paths and informational SHA-256 values for the version's draft, DOCX, review record, and applicable image resources to `article/version_index.md`. Update `article/reviews/review_index.md` with the version's comments, tracked edits, and IDs. The archive verifier checks file presence and archive structure; it does not compare these whole-file hashes.

### 6. Verify and return the DOCX for review

Run `python tools/verify_article_archive.py` after updating the archive. Confirm the DOCX opens, its article text matches the Markdown, each review item has a recorded disposition or unresolved status, indexed files are present, and archive structure and review-record content are consistent. Hashes recorded in the indexes and review records are informational only; the archive verifier does not compare them. Keep ledgers, integrity results, and other run-specific records under `inputs/run_.../`.

The archived DOCX is then the review copy for the next human review. When reviewers return it, repeat step 2 for that same version before creating another version.

## Files that are not part of the workflow

Do not create `article/reviews/prior_run_review.md`, `article/reviews/release_review_vN.md`, or another persistent handoff/release-review file. `review_index.md` and `version_index.md` provide archive navigation; the run-specific ledger provides the current change mapping. The root comparison file `Electrochimica_Acta_research_article_refernce.docx` is excluded from drafting and DOCX construction; it is retained for human comparison.

## Package instructions

The operative package instructions are `one_prompt_article_v1/PROMPT.txt`, `one_prompt_article_v1/AGENTS.md`, and `one_prompt_article_v1/article/READ_ME.md`. Follow them if this guide and the package workflow ever diverge.
