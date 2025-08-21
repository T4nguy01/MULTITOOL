from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
import platform

class PingWorker(QThread):
    finished = pyqtSignal(str, bool)
    progress = pyqtSignal(int)

    def __init__(self, target, count=4):
        super().__init__()
        self.target = target
        self.count = count

    def run(self):
        self.progress.emit(0)
        param = "-n" if platform.system() == "Windows" else "-c"
        try:
            result = subprocess.run(["ping", param, str(self.count), self.target], capture_output=True, text=True)
            success = result.returncode == 0
            self.finished.emit(result.stdout.strip(), success)
        except Exception as e:
            self.finished.emit(str(e), False)
        self.progress.emit(100)
