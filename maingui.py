import sys
import os
import time
import importlib.util
import inspect
import threading
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
# from PySide6 import uic
from mannager import Manager
from createpictures import ScreenshotWindow

class TaskWorker(QtCore.QThread):
    log_signal = QtCore.Signal(str)
    finished_signal = QtCore.Signal()

    def __init__(self, func, manager, stop_event: threading.Event, mode=None, mode_args=None):
        super().__init__()
        self.func = func
        self.manager = manager
        self.stop_event = stop_event
        # mode: None | 'times' | 'duration'
        self.mode = mode
        self.mode_args = mode_args

    def run(self):
        self.log_signal.emit('Task started')
        try:
            if self.mode == 'times':
                # mode_args expected to be an int
                times = int(self.mode_args or 0)
                self.run_times(times)
            elif self.mode == 'duration':
                # mode_args expected to be a tuple (hours, mins, secs)
                args = self.mode_args or (0, 0, 0)
                self.run_duration(*args)
            else:
                # single run
                self.func(self.manager)
        except Exception as e:
            self.log_signal.emit(f'Task error: {e}')
        finally:
            self.log_signal.emit('Task finished')
            self.finished_signal.emit()
    
    def run_times(self, times):
        self.log_signal.emit(f'Task started for {times} times')
        try:
            for i in range(times):
                if self.stop_event.is_set():
                    self.log_signal.emit('Task stopped by user')
                    break
                self.func(self.manager)
                self.log_signal.emit(f'Task iteration {i+1} finished')
        except Exception as e:
            self.log_signal.emit(f'Task error: {e}')
        finally:
            self.finished_signal.emit()

    def run_duration(self, hours, mins=0, secs=0):
        total_seconds = hours * 3600 + mins * 60 + secs
        end_time = time.time() + total_seconds
        self.log_signal.emit(f'Task started for duration {hours}h {mins}m {secs}s')
        try:
            while time.time() < end_time:
                if self.stop_event.is_set():
                    self.log_signal.emit('Task stopped by user')
                    break
                self.func(self.manager)
        except Exception as e:
            self.log_signal.emit(f'Task error: {e}')
        finally:
            self.finished_signal.emit()

    def stop(self):
        try:
            self.stop_event.set()
        except Exception:
            pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = Manager()
        self.task_worker = None
        self.loaded_task = None

        loader = QUiLoader()
        ui_file = QFile("maingui.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()
        self.band_widgets()


    def band_widgets(self):
        self.lineEdit_connect = self.ui.findChild(QtWidgets.QLineEdit, 'lineEdit_connect')
        self.btn_connect = self.ui.findChild(QtWidgets.QPushButton, 'btn_connect')
        self.btn_loadtask = self.ui.findChild(QtWidgets.QPushButton, 'btn_loadtask')
        self.btn_createtask = self.ui.findChild(QtWidgets.QPushButton, 'btn_createtask')
        self.btn_runonce = self.ui.findChild(QtWidgets.QPushButton, 'btn_runonce')
        self.btn_runduration = self.ui.findChild(QtWidgets.QPushButton, 'btn_runduration')
        self.timeEdit_runduration = self.ui.findChild(QtWidgets.QTimeEdit, 'timeEdit_runduration')
        self.btn_runtimes = self.ui.findChild(QtWidgets.QPushButton, 'btn_runtimes')
        self.spinBox_runtimes = self.ui.findChild(QtWidgets.QSpinBox, 'spinBox_runtimes')
        self.btn_stop = self.ui.findChild(QtWidgets.QPushButton, 'btn_stop')
        self.TextBrowser_log = self.ui.findChild(QtWidgets.QTextBrowser, 'TextBrowser_log')
        self.TextBrowser_log.setReadOnly(True)
        self.btn_screenshot = self.ui.findChild(QtWidgets.QPushButton, 'btn_screenshot')


        self.btn_connect.clicked.connect(self.on_connect)
        self.btn_loadtask.clicked.connect(self.on_load_task)
        self.btn_createtask.clicked.connect(self.on_create_task)
        self.btn_runonce.clicked.connect(self.on_runonce)
        self.btn_runduration.clicked.connect(self.on_runduration)
        self.btn_runtimes.clicked.connect(self.on_runtimes)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_screenshot.clicked.connect(self.on_open_screenshot)


    def check_runable(self):
        if self.manager.has_connected == False or self.loaded_task is None:
            self.log('Please connect and load a task first')
            return False
        return True

    def log(self, msg: str):
        ts = time.strftime('%H:%M:%S')
        self.TextBrowser_log.append(f'[{ts}] {msg}')

    def on_connect(self):
        window_name = self.lineEdit_connect.text().strip()
        ok = self.manager.connect(window_name)
        self.log('Connect ' + ('succeeded' if ok else 'failed'))

     # Task loading / running
    def on_load_task(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select task file', os.path.dirname(__file__), 'Python Files (*.py)')
        if not path:
            return
        try:
            spec = importlib.util.spec_from_file_location('user_task_module', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # find callable task function
            task_func = None
            for name in ('task', 'run', 'main'):
                if hasattr(module, name) and callable(getattr(module, name)):
                    task_func = getattr(module, name)
                    break
            if not task_func:
                # fallback: find first callable at module level
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if callable(obj) and inspect.isfunction(obj):
                        task_func = obj
                        break
            if not task_func:
                self.log('No callable task found in file')
                self.loaded_task = None
                return
            self.loaded_task = task_func
            self.log(f'Task loaded from {os.path.basename(path)} as {task_func.__name__}')
        except Exception as e:
            self.log(f'Load task error: {e}')
            self.loaded_task = None

    def on_create_task(self):
        pass

    def on_runonce(self):
        if self.check_runable() == False:
            return
        if getattr(self, 'task_worker', None) and self.task_worker.isRunning():
            self.log('Task already running')
            return
        self.task_stop_event = threading.Event()
        self.task_worker = TaskWorker(self.loaded_task, self.manager, self.task_stop_event)
        self.task_worker.log_signal.connect(self.log)
        self.task_worker.finished_signal.connect(self.task_finished_callback)
        self.task_worker.start()

    def on_runduration(self):
        if self.check_runable() == False:
            return
        if getattr(self, 'task_worker', None) and self.task_worker.isRunning():
            self.log('Task already running')
            return
        t = self.timeEdit_runduration.time()
        hours = t.hour()
        mins = t.minute()
        secs = t.second()
        self.task_stop_event = threading.Event()
        self.task_worker = TaskWorker(self.loaded_task, self.manager, self.task_stop_event, mode='duration', mode_args=(hours, mins, secs))
        self.task_worker.log_signal.connect(self.log)
        self.task_worker.finished_signal.connect(self.task_finished_callback)
        self.task_worker.start()

    def on_runtimes(self):
        if self.check_runable() == False:
            return
        if getattr(self, 'task_worker', None) and self.task_worker.isRunning():
            self.log('Task already running')
            return
        times = self.spinBox_runtimes.value()
        self.task_stop_event = threading.Event()
        self.task_worker = TaskWorker(self.loaded_task, self.manager, self.task_stop_event, mode='times', mode_args=times)
        self.task_worker.log_signal.connect(self.log)
        self.task_worker.finished_signal.connect(self.task_finished_callback)
        self.task_worker.start()


    def task_finished_callback(self):
        self.task_worker = None

    def on_stop(self):
        if getattr(self, 'task_worker', None):
            try:
                self.task_worker.stop()
                self.task_worker.wait(1)
                self.log('Task stop requested')
            except Exception as e:
                self.log(f'Error stopping task: {e}')

    def on_open_screenshot(self):
        try:
            self.screenshot_window = ScreenshotWindow(fixed_x=self.manager.win_controller.window_left, fixed_y=self.manager.win_controller.window_top)
            #self.screenshot_window.finished.connect(self.on_screenshot_finished)
            self.screenshot_window.show()
        except Exception as e:
            self.log(f'Error opening screenshot window: {e}')


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.ui.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
    #部落冲突 - MuMu安卓设备
