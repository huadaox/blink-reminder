from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class BlinkMetrics:
    blink_count: int = 0
    elapsed_seconds: float = 0.0
    blinks_per_minute: float = 0.0
    needs_blink_reminder: bool = False
    recent_blink_count: int = 0
    last_blink_age_s: float | None = None
    recent_blink_offsets_s: list[float] = field(default_factory=list)


class BlinkFrequencyTracker:
    def __init__(
        self,
        close_threshold: float = 0.21,
        open_threshold: float = 0.27,
        min_blink_duration_s: float = 0.06,
        max_blink_duration_s: float = 0.80,
        rolling_window_s: float = 60.0,
        recent_window_s: float = 300.0,
        reminder_threshold_bpm: float = 12.0,
        warmup_s: float = 20.0,
    ) -> None:
        self.close_threshold = close_threshold
        self.open_threshold = open_threshold
        self.min_blink_duration_s = min_blink_duration_s
        self.max_blink_duration_s = max_blink_duration_s
        self.rolling_window_s = rolling_window_s
        self.recent_window_s = recent_window_s
        self.reminder_threshold_bpm = reminder_threshold_bpm
        self.warmup_s = warmup_s

        self._blink_count = 0
        self._tracking_started_at = 0.0
        self._eyes_closed_at: float | None = None
        self._is_closed = False
        self._blink_timestamps: deque[float] = deque()

    def reset(self, now_s: float) -> None:
        self._blink_count = 0
        self._tracking_started_at = now_s
        self._eyes_closed_at = None
        self._is_closed = False
        self._blink_timestamps.clear()

    def update(self, ear: float | None, now_s: float) -> BlinkMetrics:
        if self._tracking_started_at == 0.0:
            self._tracking_started_at = now_s

        if ear is not None:
            if not self._is_closed and ear <= self.close_threshold:
                self._is_closed = True
                self._eyes_closed_at = now_s
            elif self._is_closed and ear >= self.open_threshold:
                closed_duration = now_s - self._eyes_closed_at if self._eyes_closed_at else 0.0
                if self.min_blink_duration_s <= closed_duration <= self.max_blink_duration_s:
                    self._blink_count += 1
                    self._blink_timestamps.append(now_s)
                self._is_closed = False
                self._eyes_closed_at = None

        return self._metrics(now_s)

    def _metrics(self, now_s: float) -> BlinkMetrics:
        while self._blink_timestamps and now_s - self._blink_timestamps[0] > self.recent_window_s:
            self._blink_timestamps.popleft()

        elapsed_s = max(now_s - self._tracking_started_at, 0.001)
        rolling_count = sum(1 for ts in self._blink_timestamps if now_s - ts <= self.rolling_window_s)
        effective_window_s = max(min(elapsed_s, self.rolling_window_s), 0.001)
        bpm = rolling_count * 60.0 / effective_window_s
        needs_reminder = elapsed_s >= self.warmup_s and bpm < self.reminder_threshold_bpm
        last_blink_age_s = None if not self._blink_timestamps else now_s - self._blink_timestamps[-1]
        recent_offsets = [now_s - ts for ts in reversed(self._blink_timestamps)]
        return BlinkMetrics(
            blink_count=self._blink_count,
            elapsed_seconds=elapsed_s,
            blinks_per_minute=round(bpm, 1),
            needs_blink_reminder=needs_reminder,
            recent_blink_count=len(self._blink_timestamps),
            last_blink_age_s=last_blink_age_s,
            recent_blink_offsets_s=recent_offsets,
        )
