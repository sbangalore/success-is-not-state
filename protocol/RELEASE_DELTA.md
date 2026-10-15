# Release delta: harness/silent_noop.py

The protocol locks (`PROTOCOL_V1*.lock.json`) bind `experiments/agent_claims/silent_noop.py` to the SHA-256
`b80b7c88e4dc2f184bc36e5a1011cdacb9e843bea5df428ccbf88fe8b028809b`. That is the file the experiment ran.

The copy in `harness/silent_noop.py` has SHA-256 `8030b9bbeb0f4b97e14996768529c18c6d2e79aabc3c9c85d3b197e7c266dfc1`.
The two files differ in exactly one line, a code comment (line 16): one word naming an internal model gateway was replaced
with "provider route". No executable line differs. A reader with access to the original can confirm this with `diff`;
the locked hash is the original's, so `verify_frozen_protocol.py` reports a mismatch for this one file when run on the
released copy. Every other locked file matches.
