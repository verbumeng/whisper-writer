# Security Policy

## Supported Versions

Only the latest `main` branch of this fork is actively maintained. If you're on
an older release, please update before filing a security report.

| Version | Supported |
| ------- | --------- |
| `2.x`   | ✅        |
| `1.x`   | ❌        |

## Reporting a Vulnerability

If you find a security issue in WhisperWriter, please **do not** open a public
GitHub issue. Instead:

1. Email **verbumeng@gmail.com** with a description of the issue, steps to
   reproduce, and the affected version/commit.
2. You should receive an acknowledgement within 7 days.
3. Once a fix is available, we'll coordinate a disclosure timeline with you.

For non-security bugs, please use the regular
[issue tracker](https://github.com/verbumeng/whisper-writer/issues).

## Scope

WhisperWriter is a local desktop application. The main security-relevant
surfaces are:

- **OpenAI API key handling**: stored in `src/config.yaml` on disk (gitignored).
- **Keystroke injection**: the app types transcribed text into whatever window
  has focus, so a malicious transcription prompt could theoretically inject
  text. This is inherent to the design.
- **Local model files**: downloaded from Hugging Face on first run.

If you find something outside these areas that still looks exploitable, please
report it.
