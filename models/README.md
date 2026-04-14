Place the ONNX eye-state classifier here as:

`eye_state_classifier.onnx`

Expected contract for the current code:
- input tensor: `float32`, shape `[1, 3, 32, 32]`
- output tensor: logits or probabilities for two classes
- the last class is treated as `closed`

This project keeps MediaPipe only for face/eye ROI extraction.
Blink detection is expected to come from the eye-state model output, not pure EAR thresholds.
