# Contributing to WhisperWriter

Thanks for your interest in contributing! This is a maintained fork of [savbell/whisper-writer](https://github.com/savbell/whisper-writer), and we welcome bug fixes, improvements, and feature contributions.

## Getting Started

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
3. Set up the development environment:
   ```bash
   uv venv --python 3.12
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   uv pip install -r requirements.txt
   ```
4. Make your changes and test manually with `python run.py`
5. Commit using [conventional commit](https://www.conventionalcommits.org/) messages:
   ```
   feat: add new post-processing option
   fix: resolve hotkey conflict on Linux
   docs: update configuration reference
   ```
6. Push and open a pull request

## Development Notes

- **Python version**: 3.12 is required (ctranslate2 doesn't support 3.13+).
- **PyQt5 + CUDA**: The Whisper model must be loaded *before* any PyQt5 import. Never reorder imports in `main.py`.
- **QThread cleanup**: `ResultThread` instances must be properly cleaned up between transcription cycles. Always disconnect signals and call `deleteLater()`.
- **No test suite yet**: We're working on it. For now, manually verify changes by running the app.

## Reporting Issues

When opening an issue, please include:
- Your OS and Python version
- Whether you're using local model or API mode
- Steps to reproduce the problem
- Any error output from the terminal

## Code Style

- Follow existing code conventions in the project
- Use type hints where practical
- Keep commits focused — one logical change per commit

## License

By contributing, you agree that your contributions will be licensed under the [GNU General Public License v3.0](LICENSE).
