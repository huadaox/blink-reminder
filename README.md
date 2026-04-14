# Blink Reminder

Blink Reminder is a Windows desktop app that monitors blink frequency from a webcam and shows a gentle on-screen reminder when your blink rate drops.

The current implementation is designed for local, offline use:

- `PySide6` for the desktop UI and reminder overlay
- `MediaPipe Face Mesh` for face and eye-region tracking
- `ONNX Runtime` for eye-state inference
- adaptive per-eye fallback logic so the app remains usable when eye shape changes or one eye is partially occluded

## What It Does

- Tracks blink frequency in real time
- Shows current blinks per minute, total blink count, and recent blink history
- Displays a 5-minute blink timeline
- Uses a low-intrusion reminder overlay instead of a permanent floating window
- Keeps debug values visible for tuning:
  - left eye closed probability
  - right eye closed probability
  - merged eye signal
  - EAR fallback value

## Current Detection Pipeline

The app uses a hybrid pipeline:

1. `MediaPipe Face Mesh` finds the face and eye regions.
2. An ONNX eye-state classifier estimates whether each eye is open or closed.
3. If model output is unstable, the app falls back to adaptive per-eye `EAR` tracking.
4. A blink tracker converts the eye signal into blink events and rolling blink frequency.

This approach is more robust than using a fixed EAR threshold alone, especially when:

- the user moves slightly closer to or farther from the camera
- one eye is partly covered
- the user looks tired and the default eye opening becomes smaller

## Project Structure

- `main.py`: main entrypoint
- `app_qt.py`: Qt application bootstrap
- `qt_main_window.py`: dashboard window
- `qt_overlay.py`: reminder overlay animation
- `qt_monitor_controller.py`: camera capture, face tracking, inference, blink logic
- `blink_tracker.py`: blink event state machine and rolling metrics
- `models/eye_state_classifier.onnx`: ONNX eye-state model
- `assets/reminder_frames/`: transparent PNG animation frames for the reminder

## Requirements

- Windows 10 or Windows 11
- A working webcam
- Python `3.12`

This project is not currently set up for Python `3.14`, mainly because some computer vision dependencies do not provide matching wheels there.

## Quick Start

Create and activate a Python `3.12` virtual environment:

```powershell
py -m uv python install 3.12
py -m uv venv --python 3.12 .venv
& .\.venv\Scripts\Activate.ps1
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
python .\main.py
```

If `uv` is not available in your shell, you can still use the created `.venv` and install with `pip`.

## Packaging

Use `PyInstaller` in `onedir` mode:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --onedir --name BlinkMonitorQt --add-data "assets\reminder_frames;assets\reminder_frames" --add-data "models\eye_state_classifier.onnx;models" --collect-all PySide6 --collect-all onnxruntime --collect-all cv2 --collect-all mediapipe main.py
```

Output:

```powershell
dist\BlinkMonitorQt\BlinkMonitorQt.exe
```

For distribution, package the whole `dist\BlinkMonitorQt\` directory, not only the `.exe`.

## Notes on Accuracy

This is still a practical desktop beta, not a medical product.

Things that currently affect detection quality:

- large head rotation
- very poor lighting
- strong glasses reflections
- very low camera placement
- heavy motion blur

The app is intentionally biased toward practical desktop reminder behavior rather than strict scientific blink labeling.

## Beta Status

Current release target: `beta0.01`

Known limitations:

- CPU usage is still higher than a fully optimized native implementation
- ONNX eye-state inference can be unstable on some machines, so EAR fallback remains important
- packaging size is large because the app ships with Qt, ONNX Runtime, OpenCV, and MediaPipe

## License

No license has been added yet.

If you plan to open-source this publicly, you should add a license before wider distribution.
