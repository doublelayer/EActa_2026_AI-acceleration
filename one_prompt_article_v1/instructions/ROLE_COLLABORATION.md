# Manuscript development by cooperating roles

## Purpose

One initiating prompt starts a complete manuscript-development run. Roles take successive turns on a shared manuscript, question each other's interpretations, revise the text, and check the revisions. The human author does not need to issue a new instruction for each turn. Internal drafts and review cycles belong to that single run.

This is a reusable orchestration method. Obtain scientific facts, the journal, the voice profile, protected author decisions, and output requirements from the supplied article packet. This file contains no article results or manuscript sentences.

## Shared working material

Maintain one current manuscript with stable section and paragraph identifiers, an evidence map, an author-decision checklist, and an issue log. Save internal checkpoints so each change has an identifiable source. Checkpoint identifiers are internal revision numbers, not new public manuscript version numbers.

An issue contains: identifier, originating role, affected paragraph or claim, concrete concern, supporting source or rule, requested action, responsible role, author response, verification, and status. Use open, addressed-awaiting-check, closed, or human-decision-needed. An author response alone does not close an issue; the originating role or an appropriate independent checker confirms the correction.

Each turn records its input checkpoint, files read, decisions, actual text changes or actionable review findings, output checkpoint, and open issues. A review may return no changes when the manuscript passes its remit, but must identify what it checked. Do not fabricate dialogue, agent participation, agreement, or tests.

## Responsibilities

| Role | Contribution and boundary |
|---|---|
| Librarian | Resolves the permitted sources and protects the distinction between facts, methods, and current files. |
| Scientific auditor | Verifies scientific quantities and their evidential status; sends unsupported interpretations back for correction. |
| Programmer | Produces the requested reproducible analyses and responds to numerical issues within the declared method. |
| Artist | Produces or places the approved figures and checks whether captions describe their actual content. |
| Supervisor | Maintains the contribution hierarchy and resolves conflicting recommendations through evidence and author decisions. |
| Author | Writes the full article, answers review findings, and integrates corrections into one consistent narrative. |
| Expert | Checks literature claims against supplied sources and supplies the precise evidence needed for revision. |
| Builder | Constructs the document and verifies equations, links, figures, and permitted formatting. |
| Style editor | Improves the manuscript's language and paragraph continuity within the selected voice and scientific meaning. |
| Release auditor | Independently checks the final deliverable and the completion of every substantive issue. |
| Journal editor | Reads the supplied journal guidelines before drafting, shares a source-linked requirement map, and checks scope, contribution, structure, and compliance throughout revision. |
| Scientific reviewer | Challenges scientific reasoning, reproducibility, and whether the conclusions follow from the evidence. |

The last two roles extend the ten operational roles. A journal editor and scientific reviewer are simulated roles, not actual journal staff or external peer reviewers. The scientific reviewer assesses inference; the scientific auditor checks calculations and provenance. The style editor edits language; the journal editor assesses the article as a publishable scientific argument.

## Role turns within one run

Preparation: the Librarian resolves the inputs; the scientific auditor, Programmer, and Artist establish the scientific evidence and approved illustrations as required by the task. The Expert checks the needed literature. The Supervisor produces a section-purpose and claim map. The Author writes a complete first draft. This draft is the starting point for collaboration, not the deliverable.

During preparation, the Journal editor reads the author-guideline PDF supplied with the prompt and provides its applicable requirements before the Supervisor plans the sections or the Author drafts. The requirement map includes source pages/sections, article-type applicability, and the difference between required and recommended items. The reusable role knows how to interpret and check guidelines; it does not assume fixed rules for every journal. Explicit author exceptions are recorded and checked rather than silently removed. All roles use the same resolved requirement map.

Round 1, argument and structure: the Journal editor reads the complete draft and proposes specific structural changes. The Scientific reviewer then examines the same draft and the editor's concerns, recording agreement or disagreement with reasons. The Expert and Scientific auditor answer evidence questions. The Supervisor reconciles conflicting recommendations. The Author revises the complete draft and answers every issue. The originating reviewers check the affected passages and their surrounding argument.

Round 2, explanation and voice: the Style editor edits the current draft for scientific clarity, connected paragraphs, controlled terminology, and the selected authorial voice. The Journal editor checks that the Abstract, Introduction, Results, and Conclusions still express one contribution. The Scientific reviewer checks that edits preserved meaning and scope. The Author integrates these edits, reads the document as a whole, and resolves discontinuities. Reviewers verify their issues against the new checkpoint.

Round 3, verification and release: the Builder makes the complete document. The Release auditor inspects both the prose and the rendered or structurally inspected document, with the scientific and journal reviews available. Each defect returns to its responsible role. The Author reconciles any prose change; the Builder rebuilds; the Release auditor checks the corrected artifact. End with one released manuscript, not three public versions unless requested.

The rounds have different purposes; they are not three indiscriminate rewrites. Preserve passages that already work. A role does not need to edit every paragraph to demonstrate participation. Every substantive change triggers checks on its evidence, affected cross-references, and paragraph continuity.

## Interaction and disagreement

Address questions to the role that can answer them. The Expert answers source-attribution questions, the Scientific auditor answers numerical questions, and the Author explains the intended argument. Record these exchanges concisely in the issue log. Recommendations require a concrete passage, reason, and expected improvement; general requests to make text stronger are insufficient.

The Supervisor resolves conflicts by the authority order and available evidence, not by majority vote. Style cannot overrule a scientific fact or an explicit author decision. A reviewer cannot expand the study's research aims solely to satisfy personal preference. Necessary scope statements belong where they affect interpretation, not repeatedly across every section.

Ask the human only for a missing scientific fact or consequential decision that the supplied inputs cannot resolve. Continue independent work while that issue remains open. Never invent an answer to keep the process moving. Internal uncertainty about wording, paragraph order, or the application of an explicit rule is handled within the team.

## Execution with available agents

When separate agents are available and authorized, use distinct agents for the Author and the critical review roles. Give each a bounded task, the same authoritative input packet, the current checkpoint, and relevant open issues. Take manuscript-editing turns serially; only one role writes the shared draft at a time. A reviewer may return proposed changes instead of directly editing it. Independent evidence checks can run concurrently when they cannot overwrite the manuscript.

A reviewer checks the latest checkpoint, not a remembered earlier draft. Persist handoffs on disk so context limits or agent replacement cannot lose unresolved tasks. If separate agents are unavailable, one model may take explicitly separated role turns; record that execution mode honestly. Multiple roles within one model are not independent human verification.

## Completion and bounded revision

The three rounds form the default complete cycle. Afterward, repair only identified defects; avoid unrequested stylistic churn. Repeat the relevant reviewer check after each repair. If a substantive dispute remains after two targeted repair attempts, record the evidence and the precise missing decision and retain a review candidate rather than claiming an approved release. Other completed work remains available.

Completion requires a complete manuscript, source-linked scientific claims, preserved author decisions, closed substantive issues, and the requested document checks. Human scientific approval and any claim of no subsequent manual correction remain pending until actually observed. Record the initial prompt, role turns, checkpoints, model/tool metadata available to the run, and final artifacts. One prompt means one human initiation with internal collaboration, not one unreviewed model response.


## Selected run policy

PROMPT.txt supplies current facts and the execution contract. Use the registered local project data files; relevant web research remains authorized when needed. Preserve supplied notebooks and use working copies for execution. The root `Electrochimica_Acta_research_article_refernce.docx` is reserved for comparison after generation and excluded from drafting inputs. Any historical offline examples in a reusable profile yield to this selected run policy.
