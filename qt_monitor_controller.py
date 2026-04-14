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
        self.tracker = BlinkFrequencyTracker(close_threshold=0.44, open_threshold=0.62)
        self.last_reminder_at = 0.0

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
            refine_landmarks=True,
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
                    if left_crop is not None and right_crop is not None:
                        left_closed = classifier.predict_closed_probability(left_crop)
                        right_closed = classifier.predict_closed_probability(right_crop)
                        eye_signal = 1.0 - ((left_closed + right_closed) / 2.0)
                        state.status_message = "Eye-state model active"
                    else:
                        state.status_message = "Face found, eye crop unstable"

                metrics = self.tracker.update(eye_signal, now_s)
                if result.multi_face_landmarks and eye_signal is not None:
                    state.status_message = "Blink reminder active" if metrics.needs_blink_reminder else "Blink rate normal"
                show_reminder = metrics.needs_blink_reminder and now_s - self.last_reminder_at >= 18.0
                if show_reminder:
                    self.last_reminder_at = now_s
                self.state_changed.emit(
                    BlinkUiState(
                        metrics=metrics,
                        status_message=state.status_message,
                        show_reminder=show_reminder,
                        left_closed_probability=left_closed,
                        right_closed_probability=right_closed,
                        eye_signal=eye_signal,
                    )
                )
                time.sleep(0.03)
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
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 15)
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
