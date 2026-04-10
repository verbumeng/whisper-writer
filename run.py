import os
import sys
import subprocess
from dotenv import load_dotenv

print('Starting WhisperWriter...')
load_dotenv()

# Add CUDA 12 runtime DLLs (installed via pip) to PATH for the subprocess
nvidia_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'Lib', 'site-packages', 'nvidia')
if os.path.isdir(nvidia_path):
    dll_dirs = []
    for root, dirs, files in os.walk(nvidia_path):
        if 'bin' in dirs:
            dll_dirs.append(os.path.join(root, 'bin'))
    if dll_dirs:
        os.environ['PATH'] = os.pathsep.join(dll_dirs) + os.pathsep + os.environ.get('PATH', '')

subprocess.run([sys.executable, os.path.join('src', 'main.py')])
