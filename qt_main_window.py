from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from qt_monitor_controller import BlinkMonitorController, BlinkUiState
from qt_overlay import ReminderOverlay


class TimelineWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(240)
        self._offsets: list[float] = []
        self._window_seconds = 300.0

    def set_offsets(self, offsets: list[float], window_seconds: float = 300.0) -> None:
        self._offsets = offsets
        self._window_seconds = window_seconds
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(18, 20, -18, -36)
        baseline_y = rect.center().y()

        painter.setPen(QPen(QColor("#203148"), 1))
        painter.setBrush(QColor("#0F1928"))
        painter.drawRoundedRect(rect, 18, 18)

        painter.setPen(QPen(QColor("#2A3E5D"), 2))
        painter.drawLine(rect.left() + 16, baseline_y, rect.right() - 16, baseline_y)

        for minute in range(6):
            x = rect.right() - (minute / 5.0) * rect.width()
            painter.setPen(QPen(QColor("#172537"), 1))
            painter.drawLine(int(x), rect.top() + 14, int(x), rect.bottom() - 14)
            painter.setPen(QColor("#7890A8"))
            painter.drawText(int(x) - 16, rect.bottom() + 22, "现在" if minute == 0 else f"-{minute} 分")

        if not self._offsets:
            painter.setPen(QColor("#657A90"))
            painter.drawText(self.rect(), Qt.AlignCenter, "还没有记录到近期眨眼")
            return

        painter.setPen(QPen(QColor("#89E0A9"), 2))
        painter.setBrush(QColor("#A4F0C1"))
        for index, offset in enumerate(self._offsets):
            clamped = max(0.0, min(self._window_seconds, offset))
            ratio = clamped / self._window_seconds if self._window_seconds else 0.0
            x = rect.right() - ratio * rect.width()
            spike_top = baseline_y - (44 if index % 2 == 0 else 30)
            painter.drawLine(int(x), baseline_y, int(x), int(spike_top))
            painter.drawEllipse(int(x) - 4, int(spike_top) - 4, 8, 8)


class MetricCard(QFrame):
    def __init__(self, title: str, accent: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background: #101B2C; border: 1px solid #1C3048; border-radius: 20px; }"
            "QLabel[role='title'] { color: #91A7BE; font-size: 12px; }"
            "QLabel[role='value'] { color: #F4F8FC; font-size: 30px; font-weight: 700; }"
            f"QFrame[accent='true'] {{ border-top: 3px solid {accent}; }}"
        )
        self.setProperty("accent", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        title_label = QLabel(title)
        title_label.setProperty("role", "title")
        self.value_label = QLabel("--")
        self.value_label.setProperty("role", "value")
        self.note_label = QLabel("")
        self.note_label.setProperty("secondary", "true")
        self.note_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.note_label)


class StatusBadge(QLabel):
    def __init__(self) -> None:
        super().__init__("等待中")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(34)
        self.setStyleSheet(
            "QLabel { background: #18314A; color: #D8E8F7; border-radius: 17px; padding: 0 14px; font-weight: 600; }"
        )

    def apply_status(self, text: str, paused: bool, reminder: bool) -> None:
        bg = "#18314A"
        fg = "#D8E8F7"
        if paused:
            bg = "#3B2C17"
            fg = "#F6D7A5"
        elif reminder:
            bg = "#472326"
            fg = "#FFCDD2"
        elif "fallback" in text.lower():
            bg = "#17333A"
            fg = "#AAE7EF"
        elif "normal" in text.lower():
            bg = "#173822"
            fg = "#B9F4C8"
        self.setText(text)
        self.setStyleSheet(
            f"QLabel {{ background: {bg}; color: {fg}; border-radius: 17px; padding: 0 14px; font-weight: 600; }}"
        )


class BlinkMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("眨眼提醒 Blink Reminder")
        self.resize(1180, 760)
        self.setStyleSheet(
            "QMainWindow, QWidget { background: #08111D; color: #F4F8FC; }"
            "QLabel[secondary='true'] { color: #8EA5BC; }"
            "QFrame[panel='true'] { background: #0C1523; border: 1px solid #18293F; border-radius: 24px; }"
            "QPushButton { background: #1C3048; color: #F4F8FC; border: 1px solid #294666; border-radius: 12px; padding: 10px 16px; font-weight: 600; }"
            "QPushButton:hover { background: #25405F; }"
            "QPushButton[primary='true'] { background: #2B7256; border-color: #42966F; }"
            "QPushButton[primary='true']:hover { background: #358767; }"
            "QListWidget { background: #0A1320; border: 1px solid #162639; border-radius: 18px; color: #DDE8F2; padding: 6px; }"
        )

        self.controller = BlinkMonitorController()
        self.overlay = ReminderOverlay()
        self._paused = False
        self._debug_visible = False

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(26, 24, 26, 24)
        outer.setSpacing(16)

        hero = QFrame()
        hero.setProperty("panel", "true")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 22, 24, 22)
        hero_layout.setSpacing(12)

        title_row = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("眨眼提醒")
        title.setStyleSheet("font-size: 34px; font-weight: 700;")
        subtitle = QLabel("盯着屏幕时，眨眼次数会下降。这个工具会在你眨眼频率过低时，做一个温和提醒。")
        subtitle.setWordWrap(True)
        subtitle.setProperty("secondary", "true")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        title_row.addLayout(title_block, 1)

        self.status_badge = StatusBadge()
        title_row.addWidget(self.status_badge, 0, Qt.AlignTop)
        hero_layout.addLayout(title_row)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self.pause_button = QPushButton("暂停监测")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.test_button = QPushButton("测试提醒")
        self.test_button.setProperty("primary", True)
        self.test_button.clicked.connect(self.overlay.play)
        self.debug_button = QPushButton("显示调试")
        self.debug_button.clicked.connect(self.toggle_debug)
        action_row.addWidget(self.pause_button)
        action_row.addWidget(self.test_button)
        action_row.addWidget(self.debug_button)
        action_row.addStretch(1)
        hero_layout.addLayout(action_row)
        outer.addWidget(hero)

        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(12)
        top_grid.setVerticalSpacing(12)
        self.frequency_card = MetricCard("当前频率", "#5ECF92")
        self.total_card = MetricCard("累计眨眼", "#5EA5CF")
        self.recent_card = MetricCard("最近 5 分钟", "#E5B95C")
        self.recovery_card = MetricCard("最近一次眨眼", "#D17D67")
        top_grid.addWidget(self.frequency_card, 0, 0)
        top_grid.addWidget(self.total_card, 0, 1)
        top_grid.addWidget(self.recent_card, 0, 2)
        top_grid.addWidget(self.recovery_card, 0, 3)
        outer.addLayout(top_grid)

        content = QHBoxLayout()
        content.setSpacing(14)

        left_panel = QFrame()
        left_panel.setProperty("panel", "true")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(14)
        section_title = QLabel("眨眼时间线")
        section_title.setStyleSheet("font-size: 18px; font-weight: 650;")
        section_subtitle = QLabel("显示最近 5 分钟内的眨眼时间点，越靠右越接近当前时刻。")
        section_subtitle.setProperty("secondary", "true")
        section_subtitle.setWordWrap(True)
        self.timeline = TimelineWidget()
        left_layout.addWidget(section_title)
        left_layout.addWidget(section_subtitle)
        left_layout.addWidget(self.timeline, 1)
        content.addWidget(left_panel, 1)

        right_panel = QFrame()
        right_panel.setProperty("panel", "true")
        right_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(14)

        summary_title = QLabel("监测状态")
        summary_title.setStyleSheet("font-size: 18px; font-weight: 650;")
        self.status_label = QLabel("正在等待人脸")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: 700;")
        self.helper_label = QLabel("建议把摄像头放在屏幕上方附近，保持脸部基本朝向屏幕。")
        self.helper_label.setProperty("secondary", "true")
        self.helper_label.setWordWrap(True)
        right_layout.addWidget(summary_title)
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.helper_label)

        right_layout.addWidget(QLabel("近期眨眼记录"))
        self.events = QListWidget()
        right_layout.addWidget(self.events, 1)

        self.debug_panel = QFrame()
        self.debug_panel.setStyleSheet("QFrame { background: #0A1320; border: 1px solid #162639; border-radius: 18px; }")
        debug_layout = QVBoxLayout(self.debug_panel)
        debug_layout.setContentsMargins(14, 14, 14, 14)
        debug_layout.setSpacing(6)
        debug_title = QLabel("调试信号")
        debug_title.setStyleSheet("font-weight: 650;")
        self.left_prob_label = QLabel("Left closed: --")
        self.left_prob_label.setProperty("secondary", "true")
        self.right_prob_label = QLabel("Right closed: --")
        self.right_prob_label.setProperty("secondary", "true")
        self.signal_label = QLabel("Eye signal: --")
        self.signal_label.setProperty("secondary", "true")
        self.ear_label = QLabel("EAR: --")
        self.ear_label.setProperty("secondary", "true")
        debug_layout.addWidget(debug_title)
        debug_layout.addWidget(self.left_prob_label)
        debug_layout.addWidget(self.right_prob_label)
        debug_layout.addWidget(self.signal_label)
        debug_layout.addWidget(self.ear_label)
        self.debug_panel.setVisible(False)
        right_layout.addWidget(self.debug_panel)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        stop_button = QPushButton("退出")
        stop_button.clicked.connect(self.close)
        bottom_row.addWidget(stop_button)
        right_layout.addLayout(bottom_row)
        content.addWidget(right_panel, 0)
        outer.addLayout(content, 1)

        self.controller.state_changed.connect(self.apply_state)
        self.controller.start()

    def toggle_pause(self) -> None:
        self._paused = not self._paused
        self.controller.set_paused(self._paused)
        self.pause_button.setText("继续监测" if self._paused else "暂停监测")

    def toggle_debug(self) -> None:
        self._debug_visible = not self._debug_visible
        self.debug_panel.setVisible(self._debug_visible)
        self.debug_button.setText("隐藏调试" if self._debug_visible else "显示调试")

    def apply_state(self, state: BlinkUiState) -> None:
        metrics = state.metrics
        self.frequency_card.value_label.setText(f"{metrics.blinks_per_minute:.1f}")
        self.frequency_card.note_label.setText("次 / 分钟")
        self.total_card.value_label.setText(str(metrics.blink_count))
        self.total_card.note_label.setText("从本次启动开始累计")
        self.recent_card.value_label.setText(str(metrics.recent_blink_count))
        self.recent_card.note_label.setText("最近 5 分钟内记录到的眨眼次数")
        self.recovery_card.value_label.setText(
            "等待中" if metrics.last_blink_age_s is None else format_age(metrics.last_blink_age_s)
        )
        self.recovery_card.note_label.setText("距离最近一次眨眼的时间")

        self.status_badge.apply_status(state.status_message, state.is_paused, state.show_reminder)
        self.status_label.setText(state.status_message)
        self.helper_label.setText(build_helper_text(state, metrics))
        self.left_prob_label.setText(format_signal("左眼闭合概率", state.left_closed_probability))
        self.right_prob_label.setText(format_signal("右眼闭合概率", state.right_closed_probability))
        self.signal_label.setText(format_signal("融合眼部信号", state.eye_signal))
        self.ear_label.setText(format_signal("EAR", state.ear))
        self.timeline.set_offsets(metrics.recent_blink_offsets_s)

        self.events.clear()
        if metrics.recent_blink_offsets_s:
            for offset in metrics.recent_blink_offsets_s[:12]:
                self.events.addItem(f"{format_age(offset)} 前")
        else:
            self.events.addItem("暂时还没有记录到眨眼事件")

        if state.show_reminder:
            self.overlay.play()

    def closeEvent(self, event) -> None:  # noqa: N802
        self.controller.stop()
        self.overlay.close()
        super().closeEvent(event)


def build_helper_text(state: BlinkUiState, metrics) -> str:
    if state.is_paused:
        return "监测已暂停。你可以继续保留窗口，也可以点击“继续监测”恢复。"
    if metrics.needs_blink_reminder:
        return "最近一分钟眨眼频率偏低，建议主动做几次完整眨眼，放松眼周。"
    if "Single-eye" in state.status_message:
        return "当前主要依赖单眼信号。另一只眼睛被遮挡或偏离镜头时，仍可继续工作。"
    if "fallback" in state.status_message.lower():
        return "当前主要依赖 EAR 自适应兜底，说明模型分数不够稳定，但监测仍在继续。"
    if "Searching" in state.status_message:
        return "请让脸部进入镜头范围，尽量保持正对屏幕。"
    return "状态稳定。正常使用电脑即可，只有眨眼频率明显下降时才会弹出提醒。"


def format_age(seconds: float) -> str:
    whole = int(seconds)
    if whole < 1:
        return "<1 秒"
    if whole < 60:
        return f"{whole} 秒"
    minutes = whole // 60
    remain = whole % 60
    return f"{minutes} 分 {remain:02d} 秒"


def format_signal(label: str, value: float | None) -> str:
    return f"{label}: --" if value is None else f"{label}: {value:.3f}"
