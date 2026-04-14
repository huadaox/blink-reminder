from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from qt_main_window import BlinkMainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Blink Monitor")
    window = BlinkMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
