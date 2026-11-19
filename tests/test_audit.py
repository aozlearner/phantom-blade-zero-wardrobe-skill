import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/pbz-wardrobe-mods'
spec = importlib.util.spec_from_file_location('audit_stage', SKILL / 'scripts/audit_stage.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.game, self.stage = self.root / 'game', self.root / 'stage'
        self.game.mkdir()
        self.stage.mkdir()
        self.original = b'working mod'
        for directory in [self.game, self.stage]:
            (directory / 'keep.js').write_bytes(self.original)
        self.baseline = self.root / 'baseline.json'
        self.row = {'relative': 'keep.js', 'sha256': hashlib.sha256(self.original).hexdigest()}
        self.baseline.write_text(json.dumps([self.row]), encoding='utf-8')

    def run_audit(self):
        return audit.audit(self.baseline, self.game, self.stage)

    def assert_blocker(self, kind):
        result = self.run_audit()
        self.assertFalse(result['ok'])
        self.assertIn(kind, [x['kind'] for x in result['blockers']])

    def test_identical_baseline(self):
        r = self.run_audit()
        self.assertTrue(r['ok'])
        self.assertEqual(r['plannedWrites'], [])

    def test_add_replace_without_mutation(self):
        (self.stage / 'keep.js').write_bytes(b'fixed')
        (self.stage / 'added.js').write_bytes(b'new')
        r = self.run_audit()
        self.assertTrue(r['ok'])
        self.assertEqual({x['action'] for x in r['plannedWrites']}, {'add', 'replace'})
        self.assertEqual((self.game / 'keep.js').read_bytes(), self.original)
        self.assertFalse((self.game / 'added.js').exists())

    def test_live_drift(self):
        (self.game / 'keep.js').write_bytes(b'user edit')
        self.assert_blocker('live_baseline_drift')

    def test_unmanaged_collision_even_if_same_content(self):
        for directory in [self.game, self.stage]:
            (directory / 'added.js').write_bytes(b'new')
        self.assert_blocker('unmanaged_target_collision')

    def test_accidental_stage_deletion(self):
        (self.stage / 'keep.js').unlink()
        (self.stage / 'other.js').write_bytes(b'new')
        self.assert_blocker('missing_from_full_stage')

    def test_missing_live_file(self):
        (self.game / 'keep.js').unlink()
        self.assert_blocker('missing_live_baseline')

    def test_unsafe_paths(self):
        for name in ['../escape', 'C:\\escape', '\\\\server\\share', 'a:stream', 'a/../b', 'a./b']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                audit.relative_name(name)

    def test_case_collision(self):
        self.baseline.write_text(json.dumps([self.row, dict(self.row, relative='KEEP.JS')]))
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_utf16_manifest(self):
        self.baseline.write_bytes(json.dumps([self.row]).encode('utf-16'))
        self.assertTrue(self.run_audit()['ok'])

    def test_overlapping_roots(self):
        with self.assertRaises(ValueError):
            audit.audit(self.baseline, self.game, self.game)


if __name__ == '__main__':
    unittest.main()
