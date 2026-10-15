"""Read-only protocol/source integrity check; no credentials or model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def verify(lock_path, consensus_root, tau_root):
    raw = lock_path.read_bytes()
    expected_lock_hash = lock_path.with_suffix('.sha256').read_text().split()[0]
    if hashlib.sha256(raw).hexdigest() != expected_lock_hash:
        raise ValueError('Lock checksum mismatch; create a versioned amendment')
    lock = json.loads(raw)
    failures = []
    for section, root in [('document_files', lock_path.parent),
                          ('consensus_files', consensus_root), ('tau_files', tau_root)]:
        for relative, expected in lock[section].items():
            path = root / relative
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                failures.append(f'{section}: {relative} missing or changed')
    revision = subprocess.check_output(['git', '-C', str(tau_root), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(tau_root), 'status', '--porcelain'], text=True).strip()
    if revision != lock['tau_revision'] or dirty:
        failures.append('Benchmark checkout is dirty or at a different revision')
    if len(lock['task_ids']) != 114 or len(set(lock['task_ids'])) != 114:
        failures.append('Expected 114 unique frozen task IDs')
    if len(lock['task_ids']) * len(lock['arms']) * lock['trials'] != lock['planned_rollouts']:
        failures.append('Rollout count mismatch')
    return lock, failures


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, default=Path(__file__).with_name('PROTOCOL_V1.lock.json'))
    p.add_argument('--consensus-root', required=True, type=Path)
    p.add_argument('--tau-root', required=True, type=Path)
    args = p.parse_args()
    try:
        lock, failures = verify(args.lock, args.consensus_root, args.tau_root)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}')
        return 1
    if failures:
        print('\n'.join('FAIL: ' + item for item in failures))
        return 1
    print(f"PASS: {lock['protocol_id']}; {lock['planned_rollouts']} planned rollouts; files match freeze.")
    print('Integrity only: paid launch gates remain pending; this check does not execute or authorize a job.')
    print('Lock SHA-256: ' + hashlib.sha256(args.lock.read_bytes()).hexdigest())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
