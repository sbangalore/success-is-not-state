# Protocol v1 operational amendment 01

Scientific protocol, model IDs, task set, rubric, six arms, seed and analysis are unchanged.
User requested launch after reviewing the frozen protocol. This amendment supplies
the logging, durable checkpoints and governed capacity gates required by v1.

- Archive exact completion-judge messages/schema, raw response, returned model and usage.
  Every attempt gets a new file, including invalid verdicts and repeated fixture calls.
- Derive delayed expiry events by strict all-call replay; no added live tool calls.
- Upload each completed native trajectory checkpoint before reporting task completion;
  upload failures stop further inference admissions.
- Gate execution on checksums and a no-inference allocation probe holding 80 isolated
  delayed environments. Require >=4 CPUs, >=6 GiB available RAM and <=4 GiB probe peak.
- Fixed research:agent_claims_replication job: cloud worker, 4 CPUs/8 GiB requested,
  15 GiB scratch, non-spot provisioning, $5 infrastructure placement maximum, four-hour
  timeout. This is separate from the $150 cumulative model soft cap and $5.89664525
  prior validation cost. Never run the full study on the control-plane host.
- New replication-v1 namespace; no validation reuse. Existing small jobs unchanged.

The allocation probe does not guarantee peak full-run memory or one-hour throughput.
The runtime must pass capacity and 16 judge fixtures before collecting trajectories.
The original v1 lock is preserved alongside the amended source lock.

After all 684 labels complete, automatically prepare the frozen deterministic
60-transcript human-review packet and separate private key. No model supplies the
human labels. This implements the existing publication audit, not a new experiment.
