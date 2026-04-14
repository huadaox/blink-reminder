# Native Model Layout

Put the native OpenVINO pipeline models in this folder before building the WinUI 3 app.

Recommended first-pass model set:

- `openvino/face-detection-retail-0004.onnx`
- `openvino/facial-landmarks-35-adas-0002.onnx`
- `openvino/open-closed-eye-0001.onnx`
- `openvino/head-pose-estimation-adas-0001.onnx`

The native app is being restructured so each stage has a dedicated model:

1. face detection
2. landmarks / eye ROI
3. per-eye open / closed classification
4. head pose gating
