"""Judge gate and actual delayed-fault semantics; no inference."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from independent_run import JUDGE_CASES, RunStopped, validate_claim_judge


class ValidationTests(unittest.TestCase):
    def test_judge_gate_persists_failures_and_refuses_rollouts(self):
        with TemporaryDirectory() as directory:
            def meter(**kwargs):
                return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({
                    'asserted_completion': False, 'evidence_message_index': -1})))])
            with self.assertRaisesRegex(RunStopped, 'no benchmark rollouts'):
                validate_claim_judge(meter, 'offline', 'rubric', {}, Path(directory))
            report = json.loads((Path(directory) / 'judge_validation.json').read_text())
            self.assertEqual(len(report), len(JUDGE_CASES))
            self.assertTrue(any(not row['pass'] for row in report))

    def test_judge_gate_accepts_expected_labels(self):
        cases = iter(JUDGE_CASES)
        with TemporaryDirectory() as directory:
            def meter(**kwargs):
                _, contents, expected = next(cases)
                return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({
                    'asserted_completion': expected,
                    'evidence_message_index': len(contents) - 1 if expected else -1})))])
            validate_claim_judge(meter, 'offline', 'rubric', {}, Path(directory))
            self.assertTrue(all(row['pass'] for row in json.loads((Path(directory) / 'judge_validation.json').read_text())))

    def test_delayed_revert_timing_and_environment_isolation(self):
        try:
            from silent_noop import get_delayed_environment, _with_verify_policy
            from tau2.data_model.message import ToolCall
        except ModuleNotFoundError as exc:
            if exc.name == 'tau2':
                self.skipTest('Requires pinned benchmark environment')
            raise
        for factory in (get_delayed_environment, _with_verify_policy(get_delayed_environment)):
            env, other = factory(), factory()
            initial = env.get_db_hash()
            call = ToolCall(id='write', name='modify_pending_order_address', requestor='assistant', arguments={
                'order_id': '#W5918442', 'address1': '500 Howard St', 'address2': '',
                'city': 'San Francisco', 'state': 'CA', 'country': 'USA', 'zip': '94105'})
            read = ToolCall(id='read', name='get_order_details', requestor='assistant', arguments={'order_id': '#W5918442'})
            self.assertFalse(env.get_response(call).error)
            changed = env.get_db_hash()
            self.assertNotEqual(changed, initial)
            self.assertIn('500 Howard St', env.get_response(read).content)
            self.assertEqual(env.get_db_hash(), changed)  # stopping here does NOT trigger a revert
            self.assertIn('500 Howard St', env.get_response(read).content)
            self.assertEqual(env.get_db_hash(), initial)  # second later tool call fires rollback
            self.assertNotIn('500 Howard St', env.get_response(read).content)
            self.assertEqual(other.get_db_hash(), initial)
            self.assertFalse(getattr(other, '_pending_reverts', []))

    def test_delayed_rollbacks_do_not_resurrect_expired_writes(self):
        try:
            from silent_noop import get_delayed_environment
            from tau2.data_model.message import ToolCall
        except ModuleNotFoundError as exc:
            if exc.name == 'tau2':
                self.skipTest('Requires pinned benchmark environment')
            raise
        for same_order in (False, True):
            with self.subTest(same_order=same_order):
                env = get_delayed_environment()
                first = '#W6247578'
                second = first if same_order else '#W4776164'
                initial = env.get_db_hash()
                def write(order, address):
                    response = env.get_response(ToolCall(id=address, name='modify_pending_order_address',
                        requestor='assistant', arguments=dict(order_id=order, address1=address,
                        address2='', city='San Francisco', state='CA', country='USA', zip='94105')))
                    self.assertFalse(response.error)
                def read(order):
                    return env.get_response(ToolCall(id='read', name='get_order_details',
                        requestor='assistant', arguments={'order_id': order})).content
                write(first, '111 Validation Road')
                self.assertIn('111 Validation Road', read(first))
                write(second, '222 Validation Road')  # first write expires here
                self.assertIn('222 Validation Road', read(second))  # second write still live
                if not same_order:
                    self.assertNotEqual(env.tools.db.orders[first].address.address1, '111 Validation Road')
                read(second)  # second write expires
                self.assertFalse(env._pending_reverts)
                self.assertEqual(env.get_db_hash(), initial)
                self.assertNotIn('111 Validation Road', read(first))

    def test_delayed_replay_ticks_reads_and_retries_strictly(self):
        from silent_noop import get_delayed_environment
        from tau2.data_model.message import ToolCall, AssistantMessage
        env = get_delayed_environment()
        initial = env.get_db_hash()
        history = []
        calls = [
            ('modify_pending_order_items', dict(order_id='#W4776164', item_ids=['8349118980'],
                new_item_ids=['9647292434'], payment_method_id='credit_card_9513926')),
            ('get_order_details', {'order_id': '#W4776164'}),
            ('get_order_details', {'order_id': '#W4776164'}),
            ('modify_pending_order_items', dict(order_id='#W4776164', item_ids=['8349118980'],
                new_item_ids=['9647292434'], payment_method_id='credit_card_9513926')),
            ('nonexistent_tool', {}),
            ('get_order_details', {'order_id': '#W4776164'}),
        ]
        for i, (name, arguments) in enumerate(calls):
            call = ToolCall(id=str(i), name=name, requestor='assistant', arguments=arguments)
            history.extend([AssistantMessage(role='assistant', tool_calls=[call]), env.get_response(call)])
        self.assertEqual(env.get_db_hash(), initial)
        replay = get_delayed_environment()
        replay.set_state(None, None, history)
        self.assertEqual(replay.get_db_hash(), env.get_db_hash())
        corrupted = [message.model_copy(deep=True) for message in history]
        corrupted[3].content = '{}'
        with self.assertRaisesRegex(ValueError, 'response mismatch'):
            get_delayed_environment().set_state(None, None, corrupted)


if __name__ == '__main__':
    unittest.main()
