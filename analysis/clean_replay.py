#!/usr/bin/env python3
"""Clean replay (result 5): score every replication conversation by replaying its tool calls into an
unfaulted retail environment, the way tau2 scores natively, instead of into the faulty environment the
run used. No model calls. Needs tau2 at the pinned revision and its data directory:

    TAU2_DATA_DIR=<tau2-bench>/data <venv with tau2 b7ea9074c1>/bin/python analysis/clean_replay.py

Writes analysis/clean_replay.json, which replication_numbers.py reports. strict_replay is off because
the recorded tool outputs of faulted arms (reads that showed the write missing) differ from what a clean
environment returns; tau2's replay re-executes only the writes.
"""
import gzip, json
from pathlib import Path

from tau2.data_model.simulation import SimulationRun
from tau2.domains.retail.environment import get_environment, get_tasks
from tau2.evaluator.evaluator_env import EnvironmentEvaluator

HERE = Path(__file__).resolve().parent.parent
D = HERE / "data" / "replication"
ARMS = ("control", "fault", "delayed", "verify_control", "verify_fault", "verify_delayed")


def main():
    tasks = {str(t.id): t for t in get_tasks()}
    out = {}
    for arm in ARMS:
        with gzip.open(D / f"{arm}.json.gz", "rt") as f:
            sims = json.load(f)["simulations"]
        rows = {}
        for s in sims:
            sim = SimulationRun.model_validate(s)
            r = EnvironmentEvaluator.calculate_reward(get_environment, tasks[str(sim.task_id)], sim.messages,
                                                      strict_replay=False)
            recorded = ((s.get("reward_info") or {}).get("reward_breakdown") or {}).get("DB")
            rows[str(sim.task_id)] = {"clean_db": r.reward, "recorded_db": recorded}
        out[arm] = rows
        n = len(rows)
        print(f"{arm:16s} clean DB {sum(v['clean_db'] for v in rows.values()) / n:.3f}  "
              f"recorded DB {sum(v['recorded_db'] or 0 for v in rows.values()) / n:.3f}  (n={n})")
    (HERE / "analysis" / "clean_replay.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
