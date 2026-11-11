from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parent/'live'))
from evidence import put_atomic,publish_next_plan,read,read_published,sha


class PlanPublicationTests(unittest.TestCase):
    def test_atomic_publication_is_complete_and_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'next-plan-001.private.json'
            original=dict(path='原生计划',payload='x'*524288)
            put_atomic(target,original)
            self.assertEqual(original,read(target))
            with self.assertRaises(FileExistsError):put_atomic(target,dict(changed=True))
            self.assertEqual(original,read(target))
            self.assertEqual([target],list(Path(directory).iterdir()))

    def test_plan_envelope_binds_the_complete_body_and_predecessor(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);plan=root/'plan.json';plan.write_text(json.dumps(dict(steps=[])))
            publish_next_plan(root,2,plan,requires_completed=1)
            envelope=read(root/'next-plan-002.private.json')
            self.assertEqual(str(plan.resolve()),envelope['path'])
            self.assertEqual(sha(plan),envelope['sha256'])
            self.assertEqual(1,envelope['requiresCompletedPlanSequence'])

    def test_legacy_incomplete_json_can_finish_inside_the_original_window(self):
        incomplete=json.JSONDecodeError('incomplete','',0)
        with patch('evidence.read',side_effect=[incomplete,dict(path='complete')]) as reader:
            with patch('evidence.time.sleep'):
                self.assertEqual(dict(path='complete'),read_published('synthetic'))
        self.assertEqual(2,reader.call_count)

    def test_invalid_json_has_a_finite_publication_wait(self):
        incomplete=json.JSONDecodeError('incomplete','',0)
        with patch('evidence.read',side_effect=incomplete):
            with patch('evidence.time.monotonic',side_effect=[0,1,6]),patch('evidence.time.sleep'):
                with self.assertRaises(json.JSONDecodeError):read_published('synthetic')

    def test_invalid_body_and_predecessor_never_publish_an_envelope(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);plan=root/'plan.json';plan.write_text('')
            with self.assertRaises(json.JSONDecodeError):publish_next_plan(root,1,plan)
            plan.write_text('{}')
            with self.assertRaises(RuntimeError):publish_next_plan(root,1,plan,requires_completed=1)
            self.assertFalse((root/'next-plan-001.private.json').exists())


if __name__=='__main__':unittest.main()
