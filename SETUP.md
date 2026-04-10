# WhisperWriter Setup Guide (Windows)

Lessons learned from setting up this fork on Windows 11 with GPU support.

## Prerequisites

- Python 3.12 (not 3.13 — `ctranslate2` and `onnxruntime` don't have 3.13 wheels yet)
- An NVIDIA GPU (optional — CPU works but is slower)
- [uv](https://docs.astral.sh/uv/) for Python/venv management (optional but recommended)

## Quick Start (CPU only, no CUDA needed)

```bash
# Clone the repo
git clone https://github.com/<your-username>/whisper-writer.git
cd whisper-writer

# Create venv with Python 3.12
uv venv .venv --python 3.12

# Activate
# Git Bash:
source .venv/Scripts/activate
# PowerShell:
.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt

# Run
python run.py
```

On first run, the settings window opens. Set `device` to **cpu** and `model` to **base** for fast CPU inference. The **medium** model is more accurate but noticeably slower on CPU.

> **Work machine?** CPU + `base` model is all you need. No CUDA, no admin rights, no GPU required. Skip the GPU section entirely.

## GPU Setup (CUDA)

The original `requirements.txt` pins ancient versions that don't support Python 3.12. Install without version pins:

```bash
uv pip install faster-whisper openai PyQt5 pynput sounddevice soundfile \
    python-dotenv PyYAML coloredlogs webrtcvad-wheels pyperclip audioplayer \
    aiohttp attrs ffmpeg-python numba pillow requests tiktoken \
    pygetwindow pymsgbox pyscreenshot mss
```

Then install CUDA 12 runtime libraries (no need to download the full 3GB CUDA toolkit):

```bash
uv pip install nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cuda-runtime-cu12
```

### Why CUDA 12 specifically?

`ctranslate2` (the inference engine behind `faster-whisper`) is built against CUDA 12. If you have CUDA 13.x installed system-wide, it won't work — it needs `cublas64_12.dll` specifically. The pip packages above provide exactly these DLLs without a system-wide CUDA install.

### PyQt5 + CUDA segfault

Loading PyQt5 and CUDA in the same process can cause a GPU context segfault on Windows. The fix (already applied in this fork): `run.py` adds the pip-installed NVIDIA DLL paths to `PATH`, and `src/main.py` loads the CUDA model *before* importing PyQt5.

## GPU config

In the settings window (or `src/config.yaml`):

```yaml
model_options:
  local:
    device: cuda
    model: medium
    compute_type: default
```

## Taskbar Shortcut (Windows)

To pin WhisperWriter to your taskbar:

1. Create a shortcut (`.lnk`) targeting your venv's `python.exe` with `run.py` as an argument:
   - Target: `C:\path\to\whisper-writer\.venv\Scripts\python.exe`
   - Arguments: `run.py`
   - Start in: `C:\path\to\whisper-writer`
   - Icon: `C:\path\to\whisper-writer\assets\ww-logo.ico`
2. Place the shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\`
3. Search "WhisperWriter" in Start menu, right-click, **Pin to taskbar**

Note: Windows 11 only lets you pin `.exe` targets, not `.bat` files. That's why the shortcut must point to `python.exe` directly.

## Known Bugs Fixed in This Fork

### Hotkey triggers on wrong key combinations

The original code has a bug in `src/key_listener.py` line 794 where unmapped keys default to `KeyCode.SPACE`:

```python
# BEFORE (broken) — any unknown key is treated as SPACE
key_code = self.key_map.get(pynput_key, KeyCode.SPACE)

# AFTER (fixed) — unknown keys are ignored
key_code = self.key_map.get(pynput_key)
if key_code is None:
    return None
```

This caused `ctrl+shift+<any key>` to trigger when the hotkey was set to `ctrl+shift+space`.

### PyQt5 + CUDA segfault on Windows

Loading PyQt5 and CUDA in the same process causes a GPU context segfault. Fixed by preloading the Whisper model in `src/main.py` before any PyQt5 imports.

## Troubleshooting

| Problem | Fix |
|---|---|
| `nvcc: command not found` | Add CUDA's `bin/` dir to PATH, or just use the pip CUDA packages (no `nvcc` needed for inference) |
| `cublas64_12.dll` not found | `uv pip install nvidia-cublas-cu12` — don't need the full CUDA toolkit |
| `ctranslate2` / `onnxruntime` won't install | You're on Python 3.13+. Use Python 3.12 |
| App exits silently after "Creating local model..." | PyQt5+CUDA segfault. Make sure you're using the patched `main.py` that preloads the model |
| Transcription goes to terminal, not text box | `pynput` keystroke simulation can lose focus. Click your target window before the transcription finishes |
| Very slow transcription | Switch model to `base` (CPU) or enable `cuda` device (GPU) |
