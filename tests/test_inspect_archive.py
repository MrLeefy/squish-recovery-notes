"""Synthetic fixtures only; no proprietary game data is required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location(
    'inspect_archive', Path(__file__).resolve().parents[1] / 'tools/inspect_archive.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'example.apk'

    def write_archive(self, files):
        with zipfile.ZipFile(self.path, 'w') as archive:
            for name, value in files.items():
                archive.writestr(name, value)

    def test_reports_expansion_and_split_files_without_extracting(self):
        self.write_archive({
            'assets/bin/Data/mainData': b'synthetic',
            'assets/bin/Data/settings.xml': '<settings><bool name="useObb">True</bool></settings>',
            'assets/bin/Data/sharedassets0.assets.split0': b'synthetic',
            'lib/armeabi-v7a/example.so': b'not executable',
            '../../must-not-extract.txt': b'synthetic',
        })
        report = module.inspect(self.path, verify_crc=True)
        layout = report['unity_layouts'][0]
        self.assertEqual(layout['use_obb_values'], ['True'])
        self.assertEqual(layout['level_files'], [])
        self.assertEqual(report['native_architectures'], ['armeabi-v7a'])
        self.assertTrue(report['zip']['crc_verified'])
        self.assertEqual(list(Path(self.temp.name).iterdir()), [self.path])

    def test_refuses_crc_over_size_budget(self):
        self.write_archive({'large': b'x' * 100})
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            module.inspect(self.path, verify_crc=True, max_bytes=99)

    def test_rejects_entity_settings(self):
        self.write_archive({
            'assets/bin/Data/mainData': b'synthetic',
            'assets/bin/Data/settings.xml': '<!DOCTYPE settings [<!ENTITY x "value">]><settings/>',
        })
        with self.assertRaisesRegex(ValueError, 'DTD/entity'):
            module.inspect(self.path)

    def test_identifies_ipa_layout(self):
        self.write_archive({'Payload/Example.app/Data/mainData': b'synthetic',
                            'Payload/Example.app/Data/level0': b'synthetic'})
        report = module.inspect(self.path)
        self.assertEqual(report['unity_layouts'][0]['level_files'], ['level0'])


if __name__ == '__main__':
    unittest.main()
