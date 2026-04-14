from __future__ import annotations

import math
import sys
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QPixmap
from PySide6.QtWidgets import QLabel, QWidget


class ReminderOverlay(QWidget):
    def __init__(self) -> None:
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.frames = self._load_frames()
        self.frame_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        self.fade = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade.setDuration(320)
        self.fade.setEasingCurve(QEasingCurve.OutCubic)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._fade_out)

    def _load_frames(self) -> list[QPixmap]:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        folder = base / "assets" / "reminder_frames"
        return [QPixmap(str(path)) for path in sorted(folder.glob("frame_*.png"))]

    def play(self) -> None:
        if not self.frames or self.isVisible():
            return
        screen = QGuiApplication.primaryScreen().availableGeometry()
        pix = self.frames[0]
        w = pix.width()
        h = pix.height()
        self.setGeometry(QRect((screen.width() - w) // 2, int(screen.height() * 0.72), w, h))
        self.label.setGeometry(0, 0, w, h)
        self.frame_index = 0
        self.label.setPixmap(self.frames[0])
        self.setWindowOpacity(0.0)
        self.show()
        self.fade.stop()
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(0.78)
        self.fade.start()
        self.timer.start(78)
        self.hide_timer.start(2000)

    def _next_frame(self) -> None:
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.timer.stop()
            return
        self.label.setPixmap(self.frames[self.frame_index])

    def _fade_out(self) -> None:
        self.fade.stop()
        self.fade.setStartValue(self.windowOpacity())
        self.fade.setEndValue(0.0)
        self.fade.finished.connect(self.hide)
        self.fade.start()
