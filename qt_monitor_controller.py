from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import onnxruntime as ort
from PySide6.QtCore import QObject, QThread, Signal

from blink_tracker import BlinkFrequencyTracker, BlinkMetrics


LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


@dataclass
class BlinkUiState:
    metrics: BlinkMetrics = field(default_factory=BlinkMetrics)
    status_message: str = "Searching for face"
    show_reminder: bool = False
    left_closed_probability: float | None = None
    right_closed_probability: float | None = None
    eye_signal: float | None = None
    ear: float | None = None


class EyeStateClassifier:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def predict_closed_probability(self, eye_crop_bgr: np.ndarray) -> float:
        eye = cv2.resize(eye_crop_bgr, (32, 32), interpolation=cv2.INTER_AREA)
        eye = eye.astype(np.float32)
        eye = np.transpose(eye, (2, 0, 1))[None, ...]
        logits = self.session.run([self.output_name], {self.input_name: eye})[0]
        logits = np.asarray(logits, dtype=np.float32).reshape(-1)
        exp = np.exp(logits - logits.max())
        probs = exp / exp.sum()
        return float(probs[-1])


class CaptureWorker(QObject):
    state_changed = Signal(object)
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._running = True
        self.tracker = BlinkFrequencyTracker(close_threshold=0.50, open_threshold=0.68)
        self.last_reminder_at = 0.0
        self._smoothed_signal: float | None = None
        self._last_emit_at = 0.0

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        model_path = Path(__file__).resolve().parent / "models" / "eye_state_classifier.onnx"
        if not model_path.exists():
            self.state_changed.emit(
                BlinkUiState(status_message="Missing model: models/eye_state_classifier.onnx")
            )
            self.finished.emit()
            return

        classifier = EyeStateClassifier(model_path)
        mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        camera = open_camera()
        self.tracker.reset(time.monotonic())

        try:
            if not camera.isOpened():
                self.state_changed.emit(BlinkUiState(status_message="Camera unavailable"))
                return

            while self._running:
                ok, frame = camera.read()
                now_s = time.monotonic()
                if not ok:
                    self.state_changed.emit(BlinkUiState(status_message="Camera read failed"))
                    time.sleep(0.2)
                    continue

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = mesh.process(rgb)
                state = BlinkUiState(status_message="Searching for face")
                eye_signal = None
                left_closed = None
                right_closed = None

                if result.multi_face_landmarks:
                    landmarks = result.multi_face_landmarks[0].landmark
                    left_crop = crop_eye(frame, landmarks, LEFT_EYE)
                    right_crop = crop_eye(frame, landmarks, RIGHT_EYE)
                    ear_value = compute_eye_aspect_ratio(landmarks)
                    if left_crop is not None and right_crop is not None:
                        left_closed = classifier.predict_closed_probability(left_crop)
                        right_closed = classifier.predict_closed_probability(right_crop)
                        model_open_signal = 1.0 - ((left_closed + right_closed) / 2.0)
                        ear_open_signal = normalize_ear_signal(ear_value)
                        combined_signal = blend_signals(model_open_signal, ear_open_signal)
                        eye_signal = smooth_signal(self._smoothed_signal, combined_signal)
                        self._smoothed_signal = eye_signal
                        state.status_message = "Eye-state model active"
                    else:
                        state.status_message = "Face found, eye crop unstable"
                        eye_signal = smooth_signal(self._smoothed_signal, normalize_ear_signal(ear_value))
                        self._smoothed_signal = eye_signal
                else:
                    self._smoothed_signal = None

                metrics = self.tracker.update(eye_signal, now_s)
                if result.multi_face_landmarks and eye_signal is not None:
                    state.status_message = "Blink reminder active" if metrics.needs_blink_reminder else "Blink rate normal"
                show_reminder = metrics.needs_blink_reminder and now_s - self.last_reminder_at >= 18.0
                if show_reminder:
                    self.last_reminder_at = now_s
                emit_due = now_s - self._last_emit_at >= 0.12
                if emit_due or show_reminder:
                    self._last_emit_at = now_s
                    self.state_changed.emit(
                        BlinkUiState(
                            metrics=metrics,
                            status_message=state.status_message,
                            show_reminder=show_reminder,
                            left_closed_probability=left_closed,
                            right_closed_probability=right_closed,
                            eye_signal=eye_signal,
                            ear=ear_value if result.multi_face_landmarks else None,
                        )
                    )
                time.sleep(0.06)
        finally:
            camera.release()
            mesh.close()
            self.finished.emit()


class BlinkMonitorController(QObject):
    state_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.thread = QThread()
        self.worker = CaptureWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.state_changed.connect(self.state_changed.emit)
        self.worker.finished.connect(self.thread.quit)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.worker.stop()
        self.thread.quit()
        self.thread.wait(1500)


def open_camera() -> cv2.VideoCapture:
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, None]
    for backend in backends:
        camera = cv2.VideoCapture(0) if backend is None else cv2.VideoCapture(0, backend)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        camera.set(cv2.CAP_PROP_FPS, 10)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if camera.isOpened():
            return camera
        camera.release()
    return cv2.VideoCapture()


def crop_eye(frame: np.ndarray, landmarks, indexes: list[int]) -> np.ndarray | None:
    h, w = frame.shape[:2]
    points = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in indexes], dtype=np.float32)
    x, y, eye_w, eye_h = cv2.boundingRect(points.astype(np.int32))
    pad_x = int(eye_w * 0.5)
    pad_y = int(eye_h * 0.8)
    x0 = max(0, x - pad_x)
    y0 = max(0, y - pad_y)
    x1 = min(w, x + eye_w + pad_x)
    y1 = min(h, y + eye_h + pad_y)
    if x1 <= x0 or y1 <= y0:
        return None
    crop = frame[y0:y1, x0:x1]
    if crop.size == 0:
        return None
    return crop


def compute_eye_aspect_ratio(landmarks) -> float | None:
    left = eye_aspect_ratio(landmarks, LEFT_EYE)
    right = eye_aspect_ratio(landmarks, RIGHT_EYE)
    if left is None and right is None:
        return None
    valid = [value for value in (left, right) if value is not None]
    return float(sum(valid) / len(valid))


def eye_aspect_ratio(landmarks, indexes: list[int]) -> float | None:
    points = [landmarks[i] for i in indexes]
    horizontal = point_distance(points[0], points[3])
    if horizontal <= 1e-6:
        return None
    vertical = (point_distance(points[1], points[5]) + point_distance(points[2], points[4])) / 2.0
    return float(vertical / horizontal)


def point_distance(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def normalize_ear_signal(ear_value: float | None) -> float | None:
    if ear_value is None:
        return None
    # Typical open-eye EAR is roughly 0.26-0.32 on Face Mesh; closed blinks dip near 0.15.
    return float(np.clip((ear_value - 0.15) / 0.17, 0.0, 1.0))


def blend_signals(model_open_signal: float | None, ear_open_signal: float | None) -> float | None:
    if model_open_signal is None:
        return ear_open_signal
    if ear_open_signal is None:
        return model_open_signal
    # Keep the model as primary input but let EAR rescue obvious blinks.
    return float((model_open_signal * 0.65) + (ear_open_signal * 0.35))


def smooth_signal(previous: float | None, current: float | None, alpha: float = 0.55) -> float | None:
    if current is None:
        return previous
    if previous is None:
        return current
    return float((alpha * current) + ((1.0 - alpha) * previous))
