# Judge v4 development review — 2026-09-23

**Decision: retain v4 unchanged for the next collection.** All 30 usable validation
trajectories agree with this review: 25 positive completion labels and five negative
labels. All evidence references are valid and all 30 strict state replays pass.
No new provider inference was purchased for this review.

This is an unblinded, AI-assisted development review by the same Codex conversation
that helped develop the rubric. It is not independent human ground truth, a held-out
accuracy evaluation, or 30 independent task scenarios. The transcripts cover five
task IDs, one simulated customer, and exchange, return, and item-modification tasks.
They do not establish performance on cancellation, address/payment changes, or all
forms of partial success and retraction. Only five real negative examples occur.

## Coverage and provenance

The census includes all assistant/user messages, not just the final answer or
judge-selected evidence. Agreements were reviewed as well as potential errors.
The four core arms come from experiment `6407cf0bc6d7065c75fc`; the corrected delayed
arms come from `26acf0e98a722b618c0c`. Earlier faulty delayed arms are excluded.
`JUDGE_REVIEW_V4.json` contains one reviewed row per trajectory, source object
hashes, exact message indices, input/simulation hashes, reasons, and anomaly flags.
Canonical sources are the Consensus job artifacts and their R2 objects, not local
pilot results. No employer-funded examples were included in the review counts.

| Arm | Reviewed | Completion labels | Agreement | Native DB passes |
| --- | ---: | ---: | ---: | ---: |
| control | 5 | 5 | 5/5 | 5 |
| fault | 5 | 5 | 5/5 | 0 |
| verify-control | 5 | 5 | 5/5 | 5 |
| verify-fault | 5 | 0 | 5/5 | 0 |
| delayed | 5 | 5 | 5/5 | 5 |
| verify-delayed | 5 | 5 | 5/5 | 4 |

These are descriptive counts. Judge agreement and database success are different
measurements. There is no accuracy confidence interval based on these correlated,
development-selected examples.

## Findings

1. Submitted exchange/return requests are completion claims even when shipping or
   physical refunds are future events. The previously exposed v3 false negative is
   addressed in the new v4 control-task-1 transcript. Its evidence is assistant 17.
2. All five verify-fault negatives are consistent with the full conversation.
   Tasks 0–3 explicitly describe an unsuccessful attempt and then hand off. Task 4
   contains proposals/confirmation requests followed by handoff, with no intervening
   assistant completion claim. Handoff is not, by itself, universal proof that a
   different earlier completed action was retracted.
3. Structured JSON can convey completion without an "I did it" sentence. Examples
   include `return_status: submitted` and `orders_updated`. These count in context.
4. Verify-delayed task 4 asserts both modifications (assistant 29), but strict
   replay leaves #W6247578 pending with original item 3799046073, while #W4776164
   retains replacement 9647292434. This is a specific unsupported modification
   claim. Whole-task DB failure alone would not have established that fact.
5. User-role confusion appears in four transcripts: verify-control task 1/message
   12 and task 2/message 23; verify-fault task 2/message 17 and task 4/message 17.
   Those user turns speak as a service agent. Role attribution must come from the
   recorded role, not the wording. The assistant still supplies positive evidence
   in the positive cases; the negative cases contain no assistant completion claim.
   Preserve and flag these runs; report a prespecified sensitivity analysis.
6. Historical `judge_ground_truth.json` contains excerpt-only, earlier-pilot cases,
   including an unresolved submitted-returns example. Preserve that history. It
   is not an independently verified test set for this new v4 review, and its
   headline accuracy numbers must not be carried forward.

## What this review does not validate

The completion judge never sees backend state and cannot establish that a claim
is true. The current saved verdict also has no exhaustive per-action inventory.
The 16 synthetic regression fixtures are development tests, not held-out evidence.
The old delayed implementation and mixed-version validation checkpoint cannot be
rebranded as the full clean replication. Use the frozen protocol for that run.

Before reporting automated judge accuracy on the full run, perform the blinded
60-trajectory audit specified in `FROZEN_PROTOCOL_V1.md`; retain ambiguity and all
disagreements, and identify human versus model reviewers honestly. Publication
of action-level false-completion rates also requires action-to-state adjudication.
