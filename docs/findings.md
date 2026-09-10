# Technical findings

## Installation and startup are separate

The examined Android APK installed on a Samsung SM-X200 running Android 14 after using Android's documented testing exception for legacy target SDKs. It then stopped at the Disney Digital Books splash screen because the gameplay scene could not be loaded.

The manifest targeted API 22. The `useObb` setting was true. The APK contained the startup data and six split pieces of `sharedassets0.assets`, but no gameplay level file. The missing scene was `MickeyTest`.

Installing the same small APK again, using a store update link, or raising a manifest version cannot reconstruct missing gameplay assets.

## Cross-platform data was related, but not interchangeable

A surviving iOS 1.8 copy used Unity 4.6.8p1 and contained the same two scene names as the Android 1.6 copy: `BootStrap` and `MickeyTest`. Its archive contained a gameplay level, additional resource/asset files, and streaming media.

That was a useful preservation lead, not a drop-in Android expansion. The differences included texture formats, script assembly/namespace references, script registrations, serialized fields, and platform startup resources. The Android managed runtime and iOS IL2CPP executable also differed fundamentally.

A local experiment adapting data to the existing Android runtime reached gameplay. Omitting Android's startup files during an early experimental rebuild caused a native crash; restoring the omitted splash image and player connection configuration allowed scene loading. Four serialized field-layout mismatches were subsequently corrected. This is evidence from one experiment, not a generally validated conversion method.

## Observed result and limitations

On the single Android 14 tablet, startup, character sculpting, a squisher interaction, and loading a saved creation after an update/restart were observed. Two engine type messages also seen with the original APK remained. Some archived scene components had missing-script references.

No claim is made about every game feature, language, device, long session, camera export, or current Android release. The original runtime contains 32-bit ARM and x86 libraries. Changing a target SDK does not turn those into 64-bit libraries or update Unity's native engine.

The experiment did not establish a right to redistribute the game. Its binaries, assets, patches and private diagnostic logs are not supplied here. This repository cannot install or recreate that experimental build.

## Useful references

- [Android 14 behavior changes](https://developer.android.com/about/versions/14/behavior-changes-all): legacy target installation restrictions.
- [Android 15 behavior changes](https://developer.android.com/about/versions/15/behavior-changes-all): target installation restrictions and native page-size considerations.
- [UnityPy](https://github.com/K0lb3/UnityPy): independent Unity serialized-file inspection library.

Research date: September 9, 2026. Store availability, device software and platform requirements can change.
