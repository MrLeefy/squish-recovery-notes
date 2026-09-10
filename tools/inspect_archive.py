"""Read-only APK/IPA/ZIP layout inspection; no extraction or app execution."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


def digest_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(path, verify_crc=False, unity=False, max_bytes=1024**3):
    report = {'bytes': path.stat().st_size, 'sha256': digest_file(path)}
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = {entry.filename for entry in entries}
        report['zip'] = {
            'entries': len(entries),
            'unique_names': len(names) == len(entries),
            'declared_uncompressed_bytes': sum(entry.file_size for entry in entries),
            'crc_verified': False,
        }
        if verify_crc:
            if report['zip']['declared_uncompressed_bytes'] > max_bytes:
                raise ValueError('CRC scan exceeds --max-uncompressed-mib limit')
            failure = archive.testzip()
            report['zip']['crc_verified'] = failure is None
            report['zip']['first_crc_failure'] = failure
        report['native_architectures'] = sorted({
            parts[1] for name in names
            if len(parts := name.split('/')) >= 3 and parts[0] == 'lib'
            and name.endswith('.so')
        })
        main_files = sorted(name for name in names if name.endswith('/Data/mainData'))
        report['unity_layouts'] = []
        for main_file in main_files:
            prefix = main_file[:-len('mainData')]
            relative = {name[len(prefix):] for name in names if name.startswith(prefix)}
            layout = {
                'prefix': prefix,
                'main_data_present': True,
                'level_files': sorted(name for name in relative if re.fullmatch(r'level\d+(?:\.split\d+)?', name)),
                'resource_files': sorted(name for name in relative if re.fullmatch(r'(?:resources|sharedassets\d+)\.assets(?:\.split\d+)?', name)),
            }
            settings_name = prefix + 'settings.xml'
            if settings_name in names:
                if archive.getinfo(settings_name).file_size > 65536:
                    raise ValueError('Unexpectedly large settings.xml')
                raw = archive.read(settings_name)
                if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
                    raise ValueError('DTD/entity declarations are not supported')
                settings = ET.fromstring(raw)
                values = [node.text for node in settings if node.get('name') == 'useObb']
                layout['use_obb_values'] = values
            if unity:
                import UnityPy
                if archive.getinfo(main_file).file_size > min(max_bytes, 64 * 1024**2):
                    raise ValueError('mainData exceeds parser size limit')
                env = UnityPy.load(archive.read(main_file))
                layout['unity_version'] = env.file.unity_version
                layout['serialized_platform'] = int(env.file.target_platform)
                layout['build_scenes'] = [
                    obj.parse_as_dict().get('levels', [])
                    for obj in env.objects if obj.type.name == 'BuildSettings'
                ]
            report['unity_layouts'].append(layout)
        report['interpretation'] = (
            'Layout evidence only. No package/certificate validation, malware '
            'scan, license determination, or playability test was performed.'
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--verify-crc', action='store_true')
    parser.add_argument('--unity', action='store_true', help='Inspect Unity metadata with optional UnityPy')
    parser.add_argument('--max-uncompressed-mib', type=int, default=1024)
    args = parser.parse_args()
    if args.max_uncompressed_mib <= 0:
        parser.error('--max-uncompressed-mib must be positive')
    try:
        report = inspect(args.archive, args.verify_crc, args.unity,
                         args.max_uncompressed_mib * 1024**2)
    except ImportError:
        parser.exit(2, 'Optional --unity mode requires UnityPy.\n')
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError, RuntimeError) as error:
        parser.exit(2, f'Inspection failed: {error}\n')
    json.dump(report, sys.stdout, indent=2)
    print()
    if args.verify_crc and not report['zip']['crc_verified']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
