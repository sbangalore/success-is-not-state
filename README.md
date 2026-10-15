# Replication package: "Success Is Not State"

Materials for the preprint *Success Is Not State: Read-After-Write Verification Catches Silent Tool Failures but
Not Delayed Ones* (S. Bangalore, 2026). GPT-5 on τ²-bench retail, 114 tasks, six arms, one trial per task and arm.

## Regenerate the numbers
    python3 analysis/replication_numbers.py > analysis/replication_numbers.out

Needs Python 3 and NumPy. It reads only `data/replication/` and reproduces `analysis/replication_numbers.out`
byte for byte (checked before release). Every count, rate and interval in the paper's results comes from that file.

## Contents
- `data/replication/`: the six arms' full conversation records, completion labels from the frozen judge, delayed-fault
  event logs, run manifest, protocol lock, judge fixture results and cost summary (compressed JSON).
- `analysis/`: `replication_numbers.py` (all results); `clean_replay.py` and `clean_replay.json` (result 5: write calls
  replayed into a clean environment; running it needs the pinned τ²-bench checkout below, not done in this package).
- `protocol/`: the frozen protocol, its four operational amendments, the frozen judge prompt (v4), the judge review, the
  judge fixtures, hash locks and `verify_frozen_protocol.py`.
- `harness/`: the fault implementations (`silent_noop.py`), run and replication support code, requirements and bundle hashes.
- `reviews/replication-v1/author-review/`: the 60-transcript human review of the judge and its adjudication.

## What is not here
- Model API keys, provider accounts and the job scheduler that ran the conversations. Rerunning the conversations costs
  about $100 in model calls and needs your own keys.
- τ²-bench itself: `sierra-research/tau2-bench`, MIT licence, commit `b7ea9074c1cba482b30687fecdb5c8425fd6f619`.
- Paths in the protocol documents that name an internal repository refer to the code now in `harness/` and `protocol/`.

## Limits stated in the paper
The human review of the judge was not fully blind: the reviewer had seen aggregate results and received AI feedback on
the first 20 cases. One agent, one domain and one trial: the intervals describe resampling over these 114 tasks.
The delayed fault is synthetic. See the paper's Limitations.

## One difference from the hashed source
`harness/silent_noop.py` differs from the file bound by the protocol lock in one code comment (the word naming the
provider route). The code is unchanged, so `verify_frozen_protocol.py` reports a hash mismatch for that file only.

## Licences
Code (`analysis/`, `harness/`): MIT, see `LICENSE`. Data, protocol and review records: CC BY 4.0, see `LICENSE-DATA`.
The preprint itself is distributed under arXiv's perpetual non-exclusive licence and is not part of this repository.

## Citation
Bangalore, S. (2026). Success Is Not State: Read-After-Write Verification Catches Silent Tool Failures but Not Delayed
Ones. Preprint; arXiv link to be added.
