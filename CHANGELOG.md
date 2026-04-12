# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

> This is a fork of [savbell/whisper-writer](https://github.com/savbell/whisper-writer). Changes below marked with **(fork)** are specific to this fork.

## [2.0.0] - Unreleased

### Added
- New settings window to configure WhisperWriter.
- New main window to either start the keyboard listener or open the settings window.
- New continuous recording mode ([upstream #40](https://github.com/savbell/whisper-writer/issues/40)).
- New option to play a sound when transcription finishes ([upstream #40](https://github.com/savbell/whisper-writer/issues/40)).
- **(fork)** Windows CUDA DLL auto-discovery in `run.py`.
- **(fork)** GitHub Actions CI workflow for linting and validation.
- **(fork)** `pyproject.toml` for project metadata.
- **(fork)** Contributing guidelines.

### Fixed
- **(fork)** Long-session slowdown: `ResultThread` objects and Qt signal connections were accumulating across transcription cycles without cleanup. After 12-24+ hours, hundreds of orphaned QThread objects and stacked signal connections caused progressive typing slowdown. Fixed by disconnecting signals and calling `deleteLater()` on previous `ResultThread` before creating a new one.
- **(fork)** Pynput/evdev listener thread leak: `PynputBackend.start()` and `EvdevBackend.start()` created new listener threads on each call without stopping existing ones. In non-continuous recording modes, every transcription cycle leaked two pynput threads (keyboard + mouse). Fixed by calling `stop()` at the start of each backend's `start()` method.
- **(fork)** CUDA/PyQt5 segfault on Windows: Model is now loaded before any PyQt5 import to avoid GPU context conflicts.
- **(fork)** Hotkey false triggers: Unknown keys no longer default to SPACE, preventing phantom activations.

### Changed
- Migrated status window from `tkinter` to `PyQt5`.
- Migrated from JSON to YAML for configuration storage.
- Upgraded to latest versions of `openai` and `faster-whisper`, including support for local API ([upstream #32](https://github.com/savbell/whisper-writer/issues/32)).
- **(fork)** Version bump to 2.0.0 to reflect significant divergence from upstream.

### Removed
- No longer using `keyboard` package to listen for key presses.

## [1.0.1] - 2024-01-28

### Added
- New message to identify whether Whisper was being called using the API or running locally.
- Additional hold-to-talk ([upstream PR #28](https://github.com/savbell/whisper-writer/pull/28)) and press-to-toggle recording methods ([upstream #21](https://github.com/savbell/whisper-writer/issues/21)).
- New configuration options to:
  - Choose recording method (defaulting to voice activity detection).
  - Choose which sound device and sample rate to use.
  - Hide the status window ([upstream PR #28](https://github.com/savbell/whisper-writer/pull/28)).

### Changed
- Migrated from `whisper` to `faster-whisper` ([upstream #11](https://github.com/savbell/whisper-writer/issues/11)).
- Migrated from `pyautogui` to `pynput` ([upstream PR #10](https://github.com/savbell/whisper-writer/pull/10)).
- Migrated from `webrtcvad` to `webrtcvad-wheels` ([upstream PR #17](https://github.com/savbell/whisper-writer/pull/17)).
- Changed default activation key combo from `ctrl+alt+space` to `ctrl+shift+space`.
- Changed to using a local model rather than the API by default.
- Revamped README.md.

### Fixed
- Local model is now only loaded once at start-up, rather than every time the activation key combo was pressed.
- Default configuration now auto-chooses compute type for the local model to avoid warnings.
- Graceful degradation to CPU if CUDA isn't available ([upstream PR #30](https://github.com/savbell/whisper-writer/pull/30)).
- Removed long prefix of spaces in transcription ([upstream PR #19](https://github.com/savbell/whisper-writer/pull/19)).

## [1.0.0] - 2023-05-29

### Added
- Initial release of WhisperWriter by [Sav Bell](https://github.com/savbell).
- Added CHANGELOG.md.

### Changed
- Updated Whisper Python package; the local model is now compatible with Python 3.11.

[2.0.0]: https://github.com/verbumeng/whisper-writer/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/verbumeng/whisper-writer/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/verbumeng/whisper-writer/releases/tag/v1.0.0
