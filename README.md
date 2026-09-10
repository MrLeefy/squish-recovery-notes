# Squish: Mickey Mouse Clubhouse — recovery notes

Independent technical notes about diagnosing an incomplete installation of **Squish: Mickey Mouse Clubhouse**, also known as **Clay Maker: Mickey Mouse Clubhouse**.

**This repository contains no game download.** It provides an original read-only inspection tool and findings that may help people understand why a surviving installation stops at the Disney Digital Books splash screen. It is not affiliated with Disney or an official update.

## The useful finding

In the Android copy examined here, the small APK contained the engine and startup scene but was configured to use an external expansion file. The gameplay scene was absent. Installing that APK successfully, or changing its Android target version, did not supply the missing game data.

The diagnostic log was:

```text
Level 'MickeyTest' (1) couldn't be loaded because it has not been added to the build settings.
```

That error explains this particular splash-screen stall. Other files or devices can have different failures.

| Property of the examined Android copy | Observed value |
| --- | --- |
| Package | `com.disneydigitalbooks.claymakermmch_goo` |
| Listed version | 1.6, version code 8 |
| APK bytes | 21,204,328 |
| Unity | 4.6.4p3 |
| Native architectures | 32-bit ARM and x86 |
| Expansion setting | `useObb=True` |
| Startup/gameplay scene names | `BootStrap`, `MickeyTest` |

The original Android expansion was **not located** in this investigation. A surviving iOS edition contained related gameplay data; a local compatibility experiment reached sculpting and squishing on one Android 14 tablet. That result does not establish redistribution rights, general device compatibility, or a publicly supported build. See [findings](docs/findings.md).

## Inspect your own file

Requires Python 3.10 or newer. The basic inspection uses only the Python standard library, does not run the app, and does not extract archive contents.

```sh
python tools/inspect_archive.py /path/to/your-copy.apk
```

It reports SHA-256, byte size, native architectures, expansion settings, and the presence of known Unity startup/gameplay files. It can also summarize the layout of a local IPA or ZIP. File layout alone cannot prove authenticity, completeness, or playability.

Optional CRC verification reads every archive member, up to a configurable uncompressed-size limit:

```sh
python tools/inspect_archive.py /path/to/your-copy.apk --verify-crc
```

Optional Unity metadata inspection requires [UnityPy](https://github.com/K0lb3/UnityPy):

```sh
python -m pip install UnityPy==1.25.3
python tools/inspect_archive.py /path/to/your-copy.apk --unity
```

The optional mode reads `mainData` to report the serialized Unity version, platform identifier, and BuildSettings scene names. It does not load native or managed game code. Like any parser of untrusted files, run it with appropriate isolation.

## What to check before trying random fixes

1. Record the file hash and distinguish an actual downloaded file from an app-listing page.
2. Inspect the archive for gameplay data and expansion settings.
3. Separate installation rejection from runtime failure. Android target-version restrictions and missing scenes are different problems.
4. Capture the app's own startup error. Avoid publishing a full device log, which can contain private information.
5. Check architecture support on the intended device. A newer Android version does not imply support for every old native library.
6. Keep a backup of any existing saved creations before replacing an installation.

A URL badge is not a malware scan of a file. A clean file scan is not proof of authenticity or compatibility.

## Scope and licensing

The [MIT license](LICENSE) applies to this repository's original utility and writing, to the extent copyright exists. It does **not** license Disney's game, characters, artwork, audio, proprietary code, or third-party dependencies. Naming the game here identifies the subject of the investigation.

There are no APKs, IPAs, OBBs, extracted assets, decompiled game source, signing keys, binary patches, download mirrors, or purchase-unlock tools in this repository. Please do not contribute those materials or personal device logs. See [contributing](CONTRIBUTING.md) and [rights and publication notes](docs/rights.md).

This is a diagnostic reference, not a promise of a working download or legal clearance to modify or redistribute a game.
