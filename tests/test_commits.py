import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('check_commits', Path(__file__).resolve().parents[1] / 'scripts/check_commits.py')
commits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(commits)


class CommitTests(unittest.TestCase):
    def test_accepts_scopes_breaking_changes_and_chinese(self):
        for subject in ['feat(release): package preview', 'fix!: change runtime location',
                        'docs: 更新安装说明', 'refactor(keyboard)!: replace event mapping']:
            with self.subTest(subject=subject):
                self.assertTrue(commits.valid(subject))

    def test_rejects_unstructured_or_empty_subjects(self):
        for subject in ['', 'Initial commit', 'Feat: add launcher', 'fix: ',
                        'fix:bad spacing', 'feat: ' + 'x' * 100]:
            with self.subTest(subject=subject):
                self.assertFalse(commits.valid(subject))
