"""Stable study identity: one checkpoint directory and allowance across runner revisions.

`run_id` hashes the whole manifest, so any code or lock change used to open a fresh
directory and repeat completed rollouts. A study binds once to a checkpoint run;
later revisions may change only code provenance, never scientific settings.
"""

import json
import os
import subprocess
import time

# Code provenance may change between attempts; every other manifest field is frozen.
PROVENANCE = frozenset({'runner_hash', 'recovery_hash', 'audit_support_hash', 'protocol_lock_sha256'})
# Reviewed adoption of a study that started before binding existed.
ADOPTED = {'replication-v1': '9f1f9959e72a6e656870'}


def science(manifest):
    return {k: v for k, v in manifest.items() if k not in PROVENANCE}


def _remote_has_marker(remote):
    result = subprocess.run(['rclone', 'lsf', remote, '--files-only', '--max-depth', '1'],
                            capture_output=True, text=True, timeout=60)
    if result.returncode == 3:  # Prefix absent: a genuine first run.
        return False
    if result.returncode:
        raise ValueError('Cannot verify remote study marker; refusing a fresh allowance')
    return 'study.json' in result.stdout.split()


def bind(root, study_id, manifest, run_id, remote=None):
    """Return the bound study record, creating it only when no prior study can exist."""
    marker = root / 'study.json'
    if marker.exists():
        bound = json.loads(marker.read_text())
    elif remote and _remote_has_marker(remote):
        raise ValueError('Remote study marker was not restored; refusing a fresh allowance')
    elif study_id in ADOPTED:
        previous = root / ADOPTED[study_id] / 'manifest.json'
        if not previous.exists():
            raise ValueError('Adopted study checkpoint is missing; restore is incomplete')
        bound = {'study_id': study_id, 'checkpoint_run': ADOPTED[study_id],
                 'science': science(json.loads(previous.read_text())), 'adopted': True}
    elif any(root.glob('*/usage.jsonl')):
        raise ValueError('Existing spending has no study binding; refusing a fresh allowance')
    else:
        bound = {'study_id': study_id, 'checkpoint_run': run_id, 'science': science(manifest)}
    if bound['study_id'] != study_id:
        raise ValueError('Output root belongs to study ' + bound['study_id'])
    if marker.exists() or bound.get('adopted'):
        checkpoint = root / bound['checkpoint_run']
        if not (checkpoint / 'manifest.json').is_file() or not (checkpoint / 'usage.jsonl').is_file():
            raise ValueError('Bound study checkpoint or ledger is missing; restore is incomplete')
    current = science(manifest)
    changed = sorted(k for k in set(current) | set(bound['science'])
                     if current.get(k) != bound['science'].get(k))
    if changed:
        raise ValueError('Frozen study settings changed: ' + ', '.join(changed))
    if not marker.exists():
        marker.write_text(json.dumps(bound, indent=2, sort_keys=True) + '\n')
        if remote:
            try:
                result = subprocess.run(['rclone', 'copyto', str(marker), remote.rstrip('/') + '/study.json'],
                                        capture_output=True, timeout=90)
                if result.returncode:
                    raise ValueError('Could not persist study marker before dispatch')
            except (OSError, subprocess.TimeoutExpired, ValueError):
                marker.unlink()
                raise ValueError('Could not persist study marker before dispatch') from None
    return bound


def start_attempt(path, manifest, write_json):
    """Append a durable attempt record; counters survive resubmission with the directory."""
    attempts = json.loads(path.read_text()) if path.exists() else []
    attempts.append({'attempt': len(attempts) + 1, 'started': time.time(),
                     'job_id': os.environ.get('CONSENSUS_JOB_ID'),
                     'provenance': {k: manifest.get(k) for k in sorted(PROVENANCE)}, 'arms': {}})
    write_json(path, attempts)
    return attempts


def record_cells(path, attempts, arm, planned, completed, write_json):
    """Before dispatch, record every assigned cell this attempt must still complete."""
    attempts[-1]['arms'][arm] = sorted(planned - completed)
    write_json(path, attempts)


def retry_report(attempts):
    """Per arm: cells attempted more than once, and total retries beyond the first attempt."""
    counts = {}
    for attempt in attempts:
        for arm, cells in attempt['arms'].items():
            for cell in cells:
                key = (arm, tuple(cell))
                counts[key] = counts.get(key, 0) + 1
    report = {}
    for (arm, cell), n in sorted(counts.items()):
        entry = report.setdefault(arm, {'retries': 0, 'retried_cells': []})
        if n > 1:
            entry['retries'] += n - 1
            entry['retried_cells'].append({'task_id': cell[0], 'trial': cell[1], 'attempts': n})
    return report
