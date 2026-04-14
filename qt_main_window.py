from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from blink_tracker import BlinkMetrics
from qt_monitor_controller import BlinkMonitorController, BlinkUiState
from qt_overlay import ReminderOverlay


class TimelineWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(220)
        self._offsets: list[float] = []
        self._window_seconds = 300.0

    def set_offsets(self, offsets: list[float], window_seconds: float = 300.0) -> None:
        self._offsets = offsets
        self._window_seconds = window_seconds
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(18, 18, -18, -34)
        baseline_y = rect.center().y()

        painter.setPen(QPen(QColor("#24324A"), 1))
        painter.drawRect(rect)

        painter.setPen(QPen(QColor("#2D3B56"), 2))
        painter.drawLine(rect.left(), baseline_y, rect.right(), baseline_y)

        painter.setPen(QPen(QColor("#1D2940"), 1))
        for minute in range(6):
            x = rect.right() - (minute / 5.0) * rect.width()
            painter.drawLine(int(x), rect.top(), int(x), rect.bottom())
            painter.setPen(QColor("#8EA0B6"))
            painter.drawText(int(x) - 16, rect.bottom() + 20, "now" if minute == 0 else f"-{minute}m")
            painter.setPen(QPen(QColor("#1D2940"), 1))

        if not self._offsets:
            painter.setPen(QColor("#73839A"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No recent blinks yet")
            return

        painter.setPen(QPen(QColor("#37D67A"), 2))
        painter.setBrush(QColor("#7DE8B6"))
        for index, offset in enumerate(self._offsets):
            clamped = max(0.0, min(self._window_seconds, offset))
            ratio = clamped / self._window_seconds if self._window_seconds else 0.0
            x = rect.right() - ratio * rect.width()
            spike_top = baseline_y - (42 if index % 2 == 0 else 28)
            painter.drawLine(int(x), baseline_y, int(x), int(spike_top))
            painter.drawEllipse(int(x) - 4, int(spike_top) - 4, 8, 8)


class MetricCard(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background: #162033; border-radius: 18px; }"
            "QLabel[role='title'] { color: #9FB0C4; font-size: 12px; }"
            "QLabel[role='value'] { color: #F7FAFC; font-size: 24px; font-weight: 700; }"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        title_label = QLabel(title)
        title_label.setProperty("role", "title")
        self.value_label = QLabel("0")
        self.value_label.setProperty("role", "value")
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)


class BlinkMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Blink Monitor")
        self.resize(960, 680)
        self.setStyleSheet(
            "QMainWindow, QWidget { background: #09111F; color: #F7FAFC; }"
            "QLabel[secondary='true'] { color: #9FB0C4; }"
            "QFrame[panel='true'] { background: #121A2C; border-radius: 20px; }"
            "QPushButton { background: #22324A; color: #F7FAFC; border: none; border-radius: 10px; padding: 10px 16px; }"
            "QPushButton:hover { background: #304562; }"
            "QListWidget { background: #0C1322; border: none; color: #D8E1EC; }"
        )

        self.controller = BlinkMonitorController()
        self.overlay = ReminderOverlay()

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(24, 22, 24, 22)
        outer.setSpacing(16)

        title = QLabel("Blink Monitor")
        title.setStyleSheet("font-size: 30px; font-weight: 700;")
        subtitle = QLabel(
            "PySide6 desktop UI with timeline, low-intrusion reminder overlay, and eye-state-model recognition pipeline."
        )
        subtitle.setProperty("secondary", "true")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(12)
        self.frequency_card = MetricCard("Current frequency")
        self.total_card = MetricCard("Blink count")
        self.recent_card = MetricCard("Recent summary")
        top_grid.addWidget(self.frequency_card, 0, 0)
        top_grid.addWidget(self.total_card, 0, 1)
        top_grid.addWidget(self.recent_card, 0, 2)
        outer.addLayout(top_grid)

        content = QHBoxLayout()
        content.setSpacing(14)

        left_panel = QFrame()
        left_panel.setProperty("panel", "true")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(18, 18, 18, 18)
        left_layout.addWidget(QLabel("Blink timeline"))
        left_sub = QLabel("Recent 5 minutes. Newer blink events are on the right.")
        left_sub.setProperty("secondary", "true")
        left_layout.addWidget(left_sub)
        self.timeline = TimelineWidget()
        left_layout.addWidget(self.timeline)
        content.addWidget(left_panel, 1)

        right_panel = QFrame()
        right_panel.setProperty("panel", "true")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(18, 18, 18, 18)
        self.status_label = QLabel("Searching for face")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.last_blink_label = QLabel("Last blink: waiting")
        self.last_blink_label.setProperty("secondary", "true")
        self.pipeline_label = QLabel("Pipeline: MediaPipe ROI + ONNX eye-state classifier")
        self.pipeline_label.setProperty("secondary", "true")
        self.left_prob_label = QLabel("Left closed: --")
        self.left_prob_label.setProperty("secondary", "true")
        self.right_prob_label = QLabel("Right closed: --")
        self.right_prob_label.setProperty("secondary", "true")
        self.signal_label = QLabel("Eye signal: --")
        self.signal_label.setProperty("secondary", "true")
        self.ear_label = QLabel("EAR: --")
        self.ear_label.setProperty("secondary", "true")
        self.events = QListWidget()
        stop_button = QPushButton("Stop monitor")
        stop_button.clicked.connect(self.close)
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.last_blink_label)
        right_layout.addWidget(self.pipeline_label)
        right_layout.addSpacing(6)
        right_layout.addWidget(QLabel("Debug signals"))
        right_layout.addWidget(self.left_prob_label)
        right_layout.addWidget(self.right_prob_label)
        right_layout.addWidget(self.signal_label)
        right_layout.addWidget(self.ear_label)
        right_layout.addSpacing(12)
        right_layout.addWidget(QLabel("Recent blink times"))
        right_layout.addWidget(self.events, 1)
        right_layout.addWidget(stop_button)
        content.addWidget(right_panel, 0)
        outer.addLayout(content, 1)

        self.controller.state_changed.connect(self.apply_state)
        self.controller.start()

    def apply_state(self, state: BlinkUiState) -> None:
        metrics = state.metrics
        self.frequency_card.value_label.setText(f"{metrics.blinks_per_minute:.1f} blinks/min")
        self.total_card.value_label.setText(str(metrics.blink_count))
        self.recent_card.value_label.setText(f"{metrics.recent_blink_count} blinks in 5 min")
        self.status_label.setText(state.status_message)
        self.last_blink_label.setText(
            "Last blink: waiting"
            if metrics.last_blink_age_s is None
            else f"Last blink: {format_age(metrics.last_blink_age_s)} ago"
        )
        self.left_prob_label.setText(format_signal("Left closed", state.left_closed_probability))
        self.right_prob_label.setText(format_signal("Right closed", state.right_closed_probability))
        self.signal_label.setText(format_signal("Eye signal", state.eye_signal))
        self.ear_label.setText(format_signal("EAR", state.ear))
        self.timeline.set_offsets(metrics.recent_blink_offsets_s)
        self.events.clear()
        if metrics.recent_blink_offsets_s:
            for offset in metrics.recent_blink_offsets_s[:12]:
                self.events.addItem(f"{format_age(offset)} ago")
        else:
            self.events.addItem("Waiting for blink events...")

        if state.show_reminder:
            self.overlay.play()

    def closeEvent(self, event) -> None:  # noqa: N802
        self.controller.stop()
        self.overlay.close()
        super().closeEvent(event)


def format_age(seconds: float) -> str:
    whole = int(seconds)
    if whole < 1:
        return "<1s"
    if whole < 60:
        return f"{whole}s"
    minutes = whole // 60
    remain = whole % 60
    return f"{minutes}m {remain:02d}s"


def format_signal(label: str, value: float | None) -> str:
    return f"{label}: --" if value is None else f"{label}: {value:.3f}"
