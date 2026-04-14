# Windows Blink Monitor

New stack direction:

- `Python + PySide6` for the desktop UI and reminder overlay
- `MediaPipe Face Mesh` only for face/eye ROI extraction
- `ONNX Runtime` for a dedicated eye-state classifier
- blink detection driven by eye open/closed classification, not pure EAR

## Files

- `app_qt.py`: Qt application entrypoint
- `qt_main_window.py`: dashboard UI
- `qt_overlay.py`: low-intrusion reminder overlay
- `qt_monitor_controller.py`: capture loop and ONNX inference orchestration
- `models/README.md`: expected ONNX model contract

## Current status

The Qt/ONNX path is wired to the official `open-closed-eye-0001` ONNX model.

Model path:

`models/eye_state_classifier.onnx`

Run:

```powershell
python main.py
```
