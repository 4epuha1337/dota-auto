import sys
from PyQt5 import QtWidgets, QtCore
import subprocess
import os
import time

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initFileWatcher()
        self.dota_process = None
        self.dota2_process = None
        self.dota3_process = None

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Jo4erio&4epuha')

        layout = QtWidgets.QGridLayout()

        # Column 1: Autosearch (dota.py)
        layout.addWidget(QtWidgets.QLabel('Autosearch (dota.py):'), 0, 0)
        self.repeat_count_spinbox_dota = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota.setMinimum(1)
        self.repeat_count_spinbox_dota.setMaximum(100)
        self.repeat_count_spinbox_dota.valueChanged.connect(self.update_status_dota_status)
        layout.addWidget(self.repeat_count_spinbox_dota, 1, 0)

        self.toggle_auto_search_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_search_checkbox.stateChanged.connect(self.on_toggle_auto_search_dota)
        layout.addWidget(self.toggle_auto_search_checkbox, 2, 0)

        # Column 2: Autopick (dota2.py)
        layout.addWidget(QtWidgets.QLabel('Autopick (dota2.py):'), 0, 1)
        self.repeat_count_spinbox_dota2 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota2.setMinimum(1)
        self.repeat_count_spinbox_dota2.setMaximum(100)
        self.repeat_count_spinbox_dota2.valueChanged.connect(self.update_status_dota2_status)
        layout.addWidget(self.repeat_count_spinbox_dota2, 1, 1)

        self.toggle_auto_pick_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_pick_checkbox.stateChanged.connect(self.on_toggle_auto_pick_dota2)
        layout.addWidget(self.toggle_auto_pick_checkbox, 2, 1)

        # Column 3: Autobuy (dota3.py)
        layout.addWidget(QtWidgets.QLabel('Autobuy (dota3.py):'), 0, 2)
        self.repeat_count_spinbox_dota3 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota3.setMinimum(1)
        self.repeat_count_spinbox_dota3.setMaximum(100)
        self.repeat_count_spinbox_dota3.valueChanged.connect(self.update_status_dota3_status)
        layout.addWidget(self.repeat_count_spinbox_dota3, 1, 2)

        self.toggle_auto_purchase_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_purchase_checkbox.stateChanged.connect(self.toggle_auto_purchase_dota3)
        layout.addWidget(self.toggle_auto_purchase_checkbox, 2, 2)

        # Status tab with tabs for each script
        self.status_tabs = QtWidgets.QTabWidget(self)
        tab_dota, self.status_label_dota_status, self.status_label_dota_cycles = self.create_status_tab('Autosearch')
        self.status_tabs.addTab(tab_dota, 'Autosearch')
        tab_dota2, self.status_label_dota2_status, self.status_label_dota2_cycles = self.create_status_tab('Autopick')
        self.status_tabs.addTab(tab_dota2, 'Autopick')
        tab_dota3, self.status_label_dota3_status, self.status_label_dota3_cycles = self.create_status_tab('Autobuy')
        self.status_tabs.addTab(tab_dota3, 'Autobuy')
        layout.addWidget(self.status_tabs, 0, 3, 3, 1)

        self.setLayout(layout)

        # Start and Stop buttons for all scripts
        self.start_both_button = QtWidgets.QPushButton('Запустить все процессы', self)
        self.start_both_button.clicked.connect(self.start_both_scripts)
        layout.addWidget(self.start_both_button, 4, 0)

        self.stop_both_button = QtWidgets.QPushButton('Завершить все процессы', self)
        self.stop_both_button.clicked.connect(self.stop_both_scripts)
        layout.addWidget(self.stop_both_button, 4, 1)

        self.start_selected_button = QtWidgets.QPushButton('Включить программу', self)
        self.start_selected_button.clicked.connect(self.start_selected_scripts)
        layout.addWidget(self.start_selected_button, 4, 2)

        self.stop_selected_button = QtWidgets.QPushButton('Выключить программу', self)
        self.stop_selected_button.clicked.connect(self.stop_selected_scripts)
        layout.addWidget(self.stop_selected_button, 4, 3)

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def create_status_tab(self, script_name):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        groupbox_status = QtWidgets.QGroupBox('Status', self)
        groupbox_layout = QtWidgets.QVBoxLayout(groupbox_status)
        status_label_status = QtWidgets.QLabel(f'Состояние: Выключено', self)
        groupbox_layout.addWidget(status_label_status)
        status_label_cycles = QtWidgets.QLabel('Количество циклов: 1', self)  # Нумерация циклов с 1
        groupbox_layout.addWidget(status_label_cycles)

        layout.addWidget(groupbox_status)
        tab.setLayout(layout)

        return tab, status_label_status, status_label_cycles

    def initFileWatcher(self):
        self.file_watcher = QtCore.QFileSystemWatcher(self)
        self.file_watcher.addPath(os.getcwd())
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)

    def on_directory_changed(self, path):
        self.check_auto_search_completion()
        self.check_auto_pick_completion()
        self.check_auto_buy_status()

    def check_auto_search_completion(self):
        if os.path.exists("autosearch.txt") and self.dota_process is not None:
            self.stop_dota_script()
            self.toggle_auto_search_checkbox.setChecked(False)
            self.safe_remove_file("autosearch.txt")
            self.safe_remove_file("repeat-dota.txt")
            self.update_status_dota("Автопоиск завершён.")

    def check_auto_pick_completion(self):
        if os.path.exists("autopick.txt") and self.dota2_process is not None:
            self.stop_dota2_script()
            self.toggle_auto_pick_checkbox.setChecked(False)
            self.safe_remove_file("autopick.txt")
            self.safe_remove_file("repeat-dota2.txt")
            self.update_status_dota2("Автопик завершён.")

    def check_auto_buy_status(self):
        if os.path.exists("autobuy.txt") and self.dota3_process is not None:
            self.stop_dota3_script()
            self.toggle_auto_purchase_checkbox.setChecked(False)
            self.safe_remove_file("autobuy.txt")
            self.safe_remove_file("repeat-dota3.txt")
            self.update_status_dota3("Автозакуп завершён.")

    def start_selected_scripts(self):
        if self.toggle_auto_search_checkbox.isChecked():
            self.start_dota_script()
            self.create_repeat_file("repeat-dota.txt", self.repeat_count_spinbox_dota.value())
        if self.toggle_auto_pick_checkbox.isChecked():
            self.start_dota2_script()
            self.create_repeat_file("repeat-dota2.txt", self.repeat_count_spinbox_dota2.value())
        if self.toggle_auto_purchase_checkbox.isChecked():
            self.start_dota3_script()
            self.create_repeat_file("repeat-dota3.txt", self.repeat_count_spinbox_dota3.value())

    def stop_selected_scripts(self):
        if self.dota_process is not None:
            self.stop_dota_script()
        if self.dota2_process is not None:
            self.stop_dota2_script()
        if self.dota3_process is not None:
            self.stop_dota3_script()

    def on_toggle_auto_search_dota(self):
        if self.toggle_auto_search_checkbox.isChecked():
            self.toggle_auto_search_checkbox.setText('Включено')
            self.update_status_dota("В ожидании")
        else:
            self.toggle_auto_search_checkbox.setText('Выключено')
            self.update_status_dota("Выключено")

    def on_toggle_auto_pick_dota2(self):
        if self.toggle_auto_pick_checkbox.isChecked():
            self.toggle_auto_pick_checkbox.setText('Включено')
            self.update_status_dota2("В ожидании")
        else:
            self.toggle_auto_pick_checkbox.setText('Выключено')
            self.update_status_dota2("Выключено")

    def toggle_auto_purchase_dota3(self):
        if self.toggle_auto_purchase_checkbox.isChecked():
            self.toggle_auto_purchase_checkbox.setText('Включено')
            self.update_status_dota3("В ожидании")
        else:
            self.toggle_auto_purchase_checkbox.setText('Выключено')
            self.update_status_dota3("Выключено")

    def start_both_scripts(self):
        if not self.toggle_auto_search_checkbox.isChecked():
            self.start_dota_script()
            self.create_repeat_file("repeat-dota.txt", self.repeat_count_spinbox_dota.value())
        if not self.toggle_auto_pick_checkbox.isChecked():
            self.start_dota2_script()
            self.create_repeat_file("repeat-dota2.txt", self.repeat_count_spinbox_dota2.value())
        if not self.toggle_auto_purchase_checkbox.isChecked():
            self.start_dota3_script()
            self.create_repeat_file("repeat-dota3.txt", self.repeat_count_spinbox_dota3.value())

        self.toggle_auto_search_checkbox.setChecked(True)
        self.toggle_auto_pick_checkbox.setChecked(True)
        self.toggle_auto_purchase_checkbox.setChecked(True)

    def stop_both_scripts(self):
        if self.dota_process is not None:
            self.stop_dota_script()
        if self.dota2_process is not None:
            self.stop_dota2_script()
        if self.dota3_process is not None:
            self.stop_dota3_script()

        self.toggle_auto_search_checkbox.setChecked(False)
        self.toggle_auto_pick_checkbox.setChecked(False)
        self.toggle_auto_purchase_checkbox.setChecked(False)

    def start_dota_script(self):
        self.dota_process = subprocess.Popen(['python', 'dota.py'])
        self.create_repeat_file("repeat-dota.txt", self.repeat_count_spinbox_dota.value())

    def stop_dota_script(self):
        if self.dota_process is not None:
            self.dota_process.terminate()
            self.dota_process = None

    def start_dota2_script(self):
        self.dota2_process = subprocess.Popen(['python', 'dota2.py'])
        self.create_repeat_file("repeat-dota2.txt", self.repeat_count_spinbox_dota2.value())

    def stop_dota2_script(self):
        if self.dota2_process is not None:
            self.dota2_process.terminate()
            self.dota2_process = None

    def start_dota3_script(self):
        self.dota3_process = subprocess.Popen(['python', 'dota3.py'])
        self.create_repeat_file("repeat-dota3.txt", self.repeat_count_spinbox_dota3.value())

    def stop_dota3_script(self):
        if self.dota3_process is not None:
            self.dota3_process.terminate()
            self.dota3_process = None

    def create_repeat_file(self, filename, cycles):
        with open(filename, 'w') as file:
            file.write(str(cycles))

    def safe_remove_file(self, filename):
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        except PermissionError:
            time.sleep(0.1)  # Ждем 100 мс и пытаемся снова
            self.safe_remove_file(filename)

    def update_status_dota_status(self):
        cycles = self.repeat_count_spinbox_dota.value()
        self.status_label_dota_cycles.setText(f'Количество циклов: {cycles}')
        if self.toggle_auto_search_checkbox.isChecked():
            self.update_status_dota("В ожидании")

    def update_status_dota2_status(self):
        cycles = self.repeat_count_spinbox_dota2.value()
        self.status_label_dota2_cycles.setText(f'Количество циклов: {cycles}')
        if self.toggle_auto_pick_checkbox.isChecked():
            self.update_status_dota2("В ожидании")

    def update_status_dota3_status(self):
        cycles = self.repeat_count_spinbox_dota3.value()
        self.status_label_dota3_cycles.setText(f'Количество циклов: {cycles}')
        if self.toggle_auto_purchase_checkbox.isChecked():
            self.update_status_dota3("В ожидании")

    def update_status_dota(self, status):
        self.status_label_dota_status.setText(f'Состояние: {status}')

    def update_status_dota2(self, status):
        self.status_label_dota2_status.setText(f'Состояние: {status}')

    def update_status_dota3(self, status):
        self.status_label_dota3_status.setText(f'Состояние: {status}')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
