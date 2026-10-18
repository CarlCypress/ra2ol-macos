import configparser
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location('ra2ol', Path(__file__).resolve().parents[1] / 'scripts/ra2ol.py')
ra2ol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra2ol)


class ConfigTests(unittest.TestCase):
    def test_overrides_and_unrelated_settings_survive(self):
        text = '; comment\r\n[ddraw]\r\nwidth=0\r\nrenderer=auto\r\n[gamemd-ares]\r\nwidth=800\r\nWIDTH=900\r\n'
        output = ra2ol.update_ini(text, {s: {'width': 2304, 'height': 1296} for s in ra2ol.GAME_SECTIONS})
        config = configparser.RawConfigParser(); config.read_string(output)
        for section in ra2ol.GAME_SECTIONS:
            self.assertEqual(config.getint(section, 'width'), 2304)
            self.assertEqual(config.getint(section, 'height'), 1296)
        self.assertEqual(config.get('ddraw', 'renderer'), 'auto')
        self.assertIn('; comment', output)

    def test_display_writes_backup_and_both_copies(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); game = base / 'game'; (game / 'HT').mkdir(parents=True)
            for folder in [game, game / 'HT']:
                (folder / 'RA2MD.ini').write_bytes(b'[Video]\r\nScreenWidth=800\r\n')
                (folder / 'ddraw.ini').write_bytes(b'[ddraw]\r\nwidth=0\r\nrenderer=auto\r\n')
            ra2ol.configure_display(base, game, 2304, 1296)
            for folder in [game, game / 'HT']:
                config = configparser.RawConfigParser(); config.read(folder / 'ddraw.ini')
                self.assertEqual(config.getint('gamemd-ares', 'width'), 2304)
                self.assertEqual(config.get('ddraw', 'renderer'), 'auto')
            backup = next((base / 'diagnostics').iterdir())
            self.assertEqual((backup / 'ddraw.ini').read_bytes(), b'[ddraw]\r\nwidth=0\r\nrenderer=auto\r\n')
            self.assertTrue((backup / 'HT/RA2MD.ini').exists())

    def test_missing_renderer_config_leaves_game_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); (base / 'RA2MD.ini').write_text('[Video]\nScreenWidth=800\n')
            with self.assertRaises(ValueError): ra2ol.configure_display(base, base, 2304, 1296)
            self.assertEqual((base / 'RA2MD.ini').read_text(), '[Video]\nScreenWidth=800\n')

    def test_setup_refuses_existing_directory_before_downloads(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(ra2ol, 'require_mac'), patch.object(ra2ol, 'fetch') as download:
            with self.assertRaises(FileExistsError):
                from argparse import Namespace
                ra2ol.setup(Namespace(base=Path(temp), cache=Path(temp)))
            download.assert_not_called()

    def test_wrong_cached_checksum_never_overwrites_it(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp); spec = ra2ol.LOCK['installer']; path = cache / spec['filename']
            path.write_bytes(b'corrupt')
            with self.assertRaises(ValueError): ra2ol.fetch('installer', cache)
            self.assertEqual(path.read_bytes(), b'corrupt')

    def test_wine_environment_does_not_inherit_injected_libraries(self):
        with patch.dict('os.environ', {'DYLD_INSERT_LIBRARIES': '/unknown.dylib', 'WINEDLLPATH': '/other'}):
            env = ra2ol.wine_env(Path('/tmp/example'))
        self.assertNotIn('DYLD_INSERT_LIBRARIES', env)
        self.assertNotIn('WINEDLLPATH', env)
        self.assertEqual(env['WINEPREFIX'], '/private/tmp/example/prefix' if Path('/tmp').resolve() == Path('/private/tmp') else '/tmp/example/prefix')


class ArchiveTests(unittest.TestCase):
    def test_verified_zip_member_only(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('wine/wow64cpu.dll', b'verified')
            archive.writestr('CrossOver.app/other', b'not installed')
        spec = {'url': 'https://example.invalid/test.zip', 'member': 'wine/wow64cpu.dll',
                'sha256': hashlib.sha256(b'verified').hexdigest()}
        with tempfile.TemporaryDirectory() as temp, patch.dict(ra2ol.LOCK, wow64cpu=spec), patch.object(ra2ol, 'RemoteZip', return_value=io.BytesIO(buffer.getvalue())):
            result = ra2ol.fetch_wow64cpu(Path(temp))
            self.assertEqual(result.read_bytes(), b'verified')
            self.assertEqual([p.name for p in Path(temp).iterdir()], ['wow64cpu.dll'])

    def test_wrong_zip_module_hash_is_not_saved(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive: archive.writestr('wine/wow64cpu.dll', b'changed')
        spec = {'url': 'https://example.invalid/test.zip', 'member': 'wine/wow64cpu.dll', 'sha256': '0' * 64}
        with tempfile.TemporaryDirectory() as temp, patch.dict(ra2ol.LOCK, wow64cpu=spec), patch.object(ra2ol, 'RemoteZip', return_value=io.BytesIO(buffer.getvalue())):
            with self.assertRaises(ValueError): ra2ol.fetch_wow64cpu(Path(temp))
            self.assertFalse((Path(temp) / 'wow64cpu.dll').exists())


if __name__ == '__main__': unittest.main()
