# Protocol v1 operational amendment 02: interruption recovery

Status: declared recovery policy, implementation/verification pending. No paid resume until a new source lock includes this amendment and the checked implementation. Original protocol and amendment 01 remain immutable. This is a post-start amendment; report its timing, not a retrospective preregistration.

## Complete every assigned cell

Every task interrupted before a durable complete trajectory is retried from the same initial task state using identical frozen model IDs, prompts, tool settings, seed, evaluation and output limits. Keep all failed/partial attempts with task, arm, attempt number and interruption cause. Use the first complete valid trajectory; never select among completed outcomes or rerun an unfavorable valid outcome. Where a complete trajectory already exists, recover only the missing evaluation/judgment, not the trajectory.

Report retries per arm, affected task IDs, failures and remaining incomplete cells. Retry counters survive job resubmission. Do not drop interrupted tasks: long-running tasks may be systematically different. If budget or operational safety blocks a required retry, retain the assigned cell as incomplete and stop; a partial study remains descriptive. No unlimited automatic retry loop is introduced.

## Reservation headroom before continuation

Current recorded spend: $14.5579925; remaining under $150: $135.4420075. With 80 simultaneous calls, average reservation must be <= $1.69302509375. These are bounds from the runner's current reservation rates, not new provider price quotes.

| Model | 80 calls: output component | Maximum input-bound units per call, 80 equal calls | Maximum input-bound units, 80 lost + 80 equal retries |
| --- | ---: | ---: | ---: |
| GPT-5 | $13.10720 | 1,223,348 | 546,138 |
| GPT-4.1 | $5.24288 | 406,872 | 195,244 |
| Sonnet | $7.37280 | 133,405 | 62,862 |

Input-bound units are serialized UTF-8 bytes plus 4096 framing allowance plus 1024 per message, charged at the runner's conservative input token rate. They are not measured input tokens. Mixed-model batches require summing individual reservations. The last column assumes the lost and retry calls have equal reservations and no other spending; it is not a promise of recovery capacity.

For example, at 100,000 input-bound units per call, 80 calls reserve $23.1072 (GPT-5), $37.24288 (GPT-4.1), or $103.3728 (Sonnet). A lost Sonnet wave plus an identical retry wave would need $206.7456 and cannot fit the current remainder.

Before resume, compute reservations from restored pending work and report maximum/summed admission demand, retained uncertain charges and remaining headroom. Continue this check as prompts grow and spending rises. Record budget-admission waits and effective concurrency. If reservation enforcement binds below planned 80-way concurrency, stop for a declared operational concurrency amendment before continuing. Provider quota pacing and fewer than 80 remaining tasks are distinct from budget throttling. Do not shrink output caps or lower conservative reservation bounds without a justified, declared change.

A started-call reservation must be durably committed remotely before its HTTP request is sent. On uncertain interruption, charge the full validated input/output reservation exactly once against the same study allowance, leaving actual billing unknown. Missing reservation/checkpoint evidence blocks retry.

## Resume gates

Repair and test checkpoint upload/restore; implement persistent retry counts and stable study spending; verify complete existing artifacts; compute headroom; generate a versioned source lock and wire the launcher to it. Amendment 01's non-Spot requirement remains until a separately declared placement change passes these gates. This document alone does not enable reclaimable execution.

## Standard-only execution decision (2026-09-27)

For this resume, generic worst-case charging and unattended recovery (design step 5c) are deferred. Standard capacity remains required. Any new unresolved provider call stops for manual reconciliation; recording a durable reservation does not itself authorize continuation. The worst-case charging paragraph above describes the future recovery requirement, not implemented behavior in this revision. No Spot permission is added.

Attempt reporting begins with this revision; earlier attempts are not retrospectively reconstructed. Recorded cell assignments are conservative attempted-work counts, not proof each cell reached a provider. The study lock is local; cross-machine exclusion relies on the governed job system. Restore validation and an eligible Standard route remain required before paid dispatch.
