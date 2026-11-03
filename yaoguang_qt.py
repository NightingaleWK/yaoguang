import json
import logging
import os
from pathlib import Path
import sys
import time

if sys.argv[1:2] == ["--watch-parent"]:
    from yaoguang_watchdog import watchdog_main
    sys.exit(watchdog_main(sys.argv[2], sys.argv[3]))

# Retain the DLL directory handle for the lifetime of the frozen application.
_qt_dll_directory = None
if getattr(sys, "frozen", False):
    _qt_dir = os.path.join(sys._MEIPASS, "PySide6")
    if os.path.isdir(_qt_dir):
        os.environ["PATH"] = _qt_dir + os.pathsep + os.environ.get("PATH", "")
        _qt_dll_directory = os.add_dll_directory(_qt_dir)

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QSpinBox, QVBoxLayout, QWidget,
)

from yaoguang_native import KeyboardWakeGuard, WindowsDesktop


ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent


def load_config(path):
    config = {"autoOffEnabled": True, "idleSeconds": 60}
    try:
        saved = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        enabled = saved.get("autoOffEnabled", saved.get("AutoOffEnabled", saved.get("autoLockEnabled", saved.get("AutoLockEnabled", True))))
        seconds = saved.get("idleSeconds", saved.get("IdleSeconds", 60))
        if isinstance(enabled, bool):
            config["autoOffEnabled"] = enabled
        if isinstance(seconds, int) and not isinstance(seconds, bool):
            config["idleSeconds"] = max(10, min(86400, seconds))
    except FileNotFoundError:
        pass
    except (OSError, ValueError, AttributeError):
        logging.exception("settings read failed; using defaults")
    return config


class Window(QWidget):
    def __init__(self, desktop):
        super().__init__()
        self.desktop = desktop
        self.guard = KeyboardWakeGuard()
        self.settings_path = ROOT / "settings.json"
        self.config = load_config(self.settings_path)
        self.state = "ready"
        self.activity_at = 0
        self.last_activity = 0
        self.setWindowTitle("Yaoguang 下班模式")
        self.setFixedSize(540, 410)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.build_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)
        logging.info("Qt GUI started; keyboard-only wake")

    def build_ui(self):
        self.setFont(QFont("Microsoft YaHei UI", 10))
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        title = QLabel("Yaoguang 下班模式")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.Bold))
        root.addWidget(title)
        self.status = QLabel()
        self.status.setFont(QFont("Microsoft YaHei UI", 11, QFont.Weight.Bold))
        root.addWidget(self.status)
        self.auto = QCheckBox("唤醒后，无操作自动进入下班模式")
        self.auto.setChecked(self.config["autoOffEnabled"])
        root.addWidget(self.auto)
        row = QHBoxLayout()
        row.addWidget(QLabel("无操作时间（秒）："))
        self.seconds = QSpinBox()
        self.seconds.setRange(10, 86400)
        self.seconds.setValue(self.config["idleSeconds"])
        self.seconds.setFixedWidth(110)
        row.addWidget(self.seconds)
        row.addStretch()
        root.addLayout(row)
        hint = QLabel("仅按键盘唤醒屏幕，随后鼠标自动恢复。\n下班期间临时暂停鼠标输入，需管理员权限。")
        hint.setStyleSheet("color:#666;")
        root.addWidget(hint)
        buttons = QHBoxLayout()
        self.mode = QPushButton("进入下班模式")
        self.mode.clicked.connect(self.toggle)
        restore = QPushButton("恢复显示器")
        restore.clicked.connect(self.exit_mode)
        buttons.addWidget(self.mode)
        buttons.addWidget(restore)
        root.addLayout(buttons)
        save = QPushButton("保存设置")
        save.clicked.connect(self.save_clicked)
        root.addWidget(save, alignment=Qt.AlignmentFlag.AlignLeft)
        root.addStretch()
        self.refresh()

    def save(self):
        config = {"autoOffEnabled": self.auto.isChecked(), "idleSeconds": self.seconds.value()}
        temporary = self.settings_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self.settings_path)
        self.config = config

    def save_clicked(self):
        try:
            self.save()
        except OSError as error:
            self.report_error("设置保存失败", error)
        else:
            QMessageBox.information(self, "Yaoguang", "设置已保存。")

    def toggle(self):
        if self.state != "ready":
            self.exit_mode()
            return
        try:
            self.save()
            self.enter_mode()
        except Exception as error:
            self.recover("未能进入下班模式", error)

    def enter_mode(self):
        # Manual entry and idle expiry use exactly the same input protection.
        self.guard.arm()
        self.state = "waiting"
        self.setFocus(Qt.FocusReason.OtherFocusReason)
        self.refresh()
        self.desktop.display(2)
        logging.info("enter waiting; mouse suppressed until keyboard wake")

    def exit_mode(self):
        try:
            self.guard.close()
            self.desktop.display(-1)
        except Exception as error:
            self.report_error("恢复显示器失败", error)
        finally:
            self.state = "ready"
            self.refresh()
        logging.info("restore display; mouse released")

    def tick(self):
        try:
            if self.state == "waiting" and self.guard.take_wake():
                self.guard.close()
                self.desktop.display(-1)
                self.last_activity = self.desktop.last_input()
                self.activity_at = time.monotonic()
                self.state = "counting" if self.auto.isChecked() else "ready"
                self.refresh()
                logging.info("keyboard wake; mouse released")
            elif self.state == "counting":
                if not self.auto.isChecked():
                    self.state = "ready"
                    self.refresh()
                    return
                current = self.desktop.last_input()
                now = time.monotonic()
                if current != self.last_activity:
                    self.last_activity = current
                    self.activity_at = now
                elapsed = now - self.activity_at
                self.refresh(max(0, self.seconds.value() - int(elapsed)))
                if elapsed >= self.seconds.value():
                    self.enter_mode()
                    logging.info("idle timeout; reentered off-duty mode")
        except Exception as error:
            self.recover("下班模式已退出", error)

    def refresh(self, left=None):
        if self.state == "ready":
            self.status.setText("当前状态：正常运行")
        elif self.state == "waiting":
            self.status.setText("当前状态：已熄屏，仅按键盘唤醒")
        elif self.state == "counting":
            if left is None:
                left = self.seconds.value()
            self.status.setText(f"当前状态：已唤醒，{left} 秒后再次熄屏")
        self.mode.setText("进入下班模式" if self.state == "ready" else "退出下班模式")

    def report_error(self, title, error):
        logging.error("%s: %s", title, error, exc_info=True)
        QMessageBox.warning(self, "Yaoguang", f"{title}：\n{error}")

    def recover(self, title, error):
        try:
            self.guard.close()
        except Exception:
            logging.exception("input guard cleanup failed")
        try:
            self.desktop.display(-1)
        except Exception:
            logging.exception("display recovery failed")
        self.state = "ready"
        self.refresh()
        self.report_error(title, error)

    def closeEvent(self, event):
        self.timer.stop()
        try:
            self.guard.close()
        finally:
            if self.state == "waiting":
                try:
                    self.desktop.display(-1)
                except Exception:
                    logging.exception("display restore on close failed")
        logging.info("Qt GUI closed; mouse released")
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Yaoguang")
    app.setStyle("Fusion")
    logging.basicConfig(filename=ROOT / "yaoguang.log", level=logging.INFO, format="%(asctime)s %(message)s")
    desktop = WindowsDesktop()
    instance = desktop.acquire_instance()
    if instance is None:
        QMessageBox.information(None, "Yaoguang", "Yaoguang 已在运行，请使用已打开的窗口。")
        return 0
    try:
        window = Window(desktop=desktop)
        app.aboutToQuit.connect(window.guard.close)
        window.show()
        return app.exec()
    finally:
        try:
            desktop.close()
        finally:
            desktop.release_instance(instance)


if __name__ == "__main__":
    sys.exit(main())
