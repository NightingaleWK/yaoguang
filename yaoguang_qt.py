import ctypes, json, logging, os, sys, time
from ctypes import wintypes
# PyInstaller stores Qt's native DLLs below _MEIPASS/PySide6. Add that
# directory before importing any PySide6 module so Windows can resolve QtCore.
if getattr(sys, 'frozen', False):
    _qt_dir = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), 'PySide6')
    if os.path.isdir(_qt_dir):
        os.environ['PATH'] = _qt_dir + os.pathsep + os.environ.get('PATH', '')
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(_qt_dir)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox

ROOT = os.path.dirname(os.path.abspath(sys.argv[0])); SETTINGS = os.path.join(ROOT, 'settings.json')
logging.basicConfig(filename=os.path.join(ROOT, 'yaoguang.log'), level=logging.INFO, format='%(asctime)s %(message)s')
user32 = ctypes.windll.user32
class LASTINPUTINFO(ctypes.Structure): _fields_ = [('cbSize', wintypes.UINT), ('dwTime', wintypes.DWORD)]
def last_input():
    info = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
    return int(info.dwTime) if user32.GetLastInputInfo(ctypes.byref(info)) else 0
def display(level): user32.SendMessageW(0xFFFF, 0x0112, 0xF170, level)

class Window(QWidget):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Yaoguang 下班模式'); self.setFixedSize(480, 360)
        self.state='ready'; self.baseline=0; self.wake=0; self.load_config(); self.build_ui()
        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(250)
        logging.info('Qt GUI started')
    def load_config(self):
        self.config={'autoLockEnabled':True,'idleSeconds':60}
        try:
            with open(SETTINGS,encoding='utf-8') as f: self.config.update(json.load(f))
        except Exception as e: logging.info('settings read: %s',e)
    def save(self):
        self.config={'autoLockEnabled':self.auto.isChecked(),'idleSeconds':self.seconds.value()}
        with open(SETTINGS,'w',encoding='utf-8') as f: json.dump(self.config,f,ensure_ascii=False,indent=2)
    def build_ui(self):
        self.setFont(QFont('Microsoft YaHei UI', 10)); root=QVBoxLayout(self); root.setContentsMargins(28,24,28,24); root.setSpacing(16)
        title=QLabel('Yaoguang 下班模式'); title.setFont(QFont('Microsoft YaHei UI',18,QFont.Weight.Bold)); root.addWidget(title)
        self.status=QLabel('当前状态：正常运行'); self.status.setFont(QFont('Microsoft YaHei UI',12,QFont.Weight.Bold)); root.addWidget(self.status)
        self.auto=QCheckBox('启用无操作自动锁屏'); self.auto.setChecked(bool(self.config.get('autoLockEnabled',True))); root.addWidget(self.auto)
        row=QHBoxLayout(); row.addWidget(QLabel('无操作时间（秒）：')); self.seconds=QSpinBox(); self.seconds.setRange(10,86400); self.seconds.setValue(int(self.config.get('idleSeconds',60))); self.seconds.setFixedWidth(110); row.addWidget(self.seconds); row.addStretch(); root.addLayout(row)
        hint=QLabel('关闭显示器后，移动鼠标或按键盘会唤醒屏幕。'); hint.setStyleSheet('color:#777;'); root.addWidget(hint)
        buttons=QHBoxLayout(); self.mode=QPushButton('进入下班模式'); self.mode.clicked.connect(self.toggle); restore=QPushButton('恢复显示器'); restore.clicked.connect(self.exit_mode); buttons.addWidget(self.mode); buttons.addWidget(restore); root.addLayout(buttons)
        save=QPushButton('保存设置'); save.clicked.connect(lambda: (self.save(), QMessageBox.information(self,'Yaoguang','设置已保存。'))); root.addWidget(save,alignment=Qt.AlignmentFlag.AlignLeft); root.addStretch(); self.refresh()
    def toggle(self):
        if self.state=='ready': self.save(); self.baseline=last_input(); display(2); self.state='waiting'; logging.info('enter waiting')
        else: self.exit_mode()
        self.refresh()
    def exit_mode(self): display(-1); self.state='ready'; self.timer.start(); self.refresh(); logging.info('restore display')
    def tick(self):
        if self.state=='waiting':
            current=last_input()
            if current and current != self.baseline: self.wake=current; self.state='counting' if self.auto.isChecked() else 'ready'; self.refresh()
        elif self.state=='counting':
            current=last_input()
            if current != self.wake: self.wake=current; self.refresh(); return
            elapsed=(int(time.monotonic()*1000) - int(self.wake)) & 0xFFFFFFFF
            left=max(0,self.seconds.value()-elapsed//1000); self.status.setText(f'当前状态：已唤醒，{left} 秒后自动锁屏')
            if elapsed >= self.seconds.value()*1000 and user32.LockWorkStation(): self.state='locked'; logging.info('auto lock')
    def refresh(self):
        if self.state=='ready': self.status.setText('当前状态：正常运行'); self.mode.setText('进入下班模式')
        elif self.state=='waiting': self.status.setText('当前状态：显示器已关闭，等待输入'); self.mode.setText('退出下班模式')
        elif self.state=='locked': self.status.setText('当前状态：已锁屏'); self.mode.setText('退出下班模式')
        self.update()
    def closeEvent(self,e):
        if self.state != 'ready': display(-1)
        logging.info('Qt GUI closed'); e.accept()

app=QApplication(sys.argv); app.setApplicationName('Yaoguang'); app.setStyle('Fusion'); win=Window(); win.show(); sys.exit(app.exec())
