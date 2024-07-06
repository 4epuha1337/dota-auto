import sys
from PyQt5 import QtWidgets, QtCore
import subprocess
import os

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.dota_process = None
        self.dota2_process = None
        self.dota3_process = None
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 750, 550)
        self.setWindowTitle('Jo4erio&4epuha')

        layout = QtWidgets.QGridLayout()

        # Столбец "Автопоиск"
        layout.addWidget(QtWidgets.QLabel('Автопоиск (dota.py):'), 0, 0)
        self.repeat_count_spinbox_dota = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota.setMinimum(1)
        self.repeat_count_spinbox_dota.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota, 1, 0)

        self.start_dota_button = QtWidgets.QPushButton('Запустить автопоиск', self)
        self.start_dota_button.clicked.connect(self.on_start_dota_click)
        layout.addWidget(self.start_dota_button, 2, 0)

        self.stop_dota_button = QtWidgets.QPushButton('Завершить автопоиск', self)
        self.stop_dota_button.clicked.connect(self.stop_dota_script)
        self.stop_dota_button.setEnabled(False)
        layout.addWidget(self.stop_dota_button, 3, 0)

        # Столбец "Автопик"
        layout.addWidget(QtWidgets.QLabel('Автопик (dota2.py):'), 0, 1)
        self.repeat_count_spinbox_dota2 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota2.setMinimum(1)
        self.repeat_count_spinbox_dota2.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota2, 1, 1)

        self.start_dota2_button = QtWidgets.QPushButton('Запустить автопик', self)
        self.start_dota2_button.clicked.connect(self.on_start_dota2_click)
        layout.addWidget(self.start_dota2_button, 2, 1)

        self.stop_dota2_button = QtWidgets.QPushButton('Завершить автопик', self)
        self.stop_dota2_button.clicked.connect(self.stop_dota2_script)
        self.stop_dota2_button.setEnabled(False)
        layout.addWidget(self.stop_dota2_button, 3, 1)

        # Столбец "Автозакуп"
        layout.addWidget(QtWidgets.QLabel('Автозакуп (dota3.py):'), 0, 2)
        self.auto_purchase_checkbox = QtWidgets.QCheckBox('Включение автозакупа', self)
        self.auto_purchase_checkbox.stateChanged.connect(self.on_auto_purchase_toggle)
        layout.addWidget(self.auto_purchase_checkbox, 1, 2)

        # Общие кнопки для запуска и остановки обоих скриптов
        self.start_both_button = QtWidgets.QPushButton('Запустить все процессы', self)
        self.start_both_button.clicked.connect(self.start_both_scripts)
        layout.addWidget(self.start_both_button, 4, 0)

        self.stop_both_button = QtWidgets.QPushButton('Завершить все процессы', self)
        self.stop_both_button.clicked.connect(self.stop_both_scripts)
        self.stop_both_button.setEnabled(False)
        layout.addWidget(self.stop_both_button, 4, 1)

        self.status_label_dota = QtWidgets.QLabel('Ожидание запуска автопоиска...', self)
        layout.addWidget(self.status_label_dota, 5, 0)

        self.status_label_dota2 = QtWidgets.QLabel('Ожидание запуска автопика...', self)
        layout.addWidget(self.status_label_dota2, 5, 1)

        self.status_label_dota3 = QtWidgets.QLabel('Ожидание запуска автозакупа...', self)
        layout.addWidget(self.status_label_dota3, 5, 2)

        self.setLayout(layout)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def stop_dota_script(self):
        if self.dota_process is not None:
            self.dota_process.terminate()
            self.dota_process = None
            self.update_status_dota("Автопоиск остановлен.")
            self.toggle_buttons()

    def stop_dota2_script(self):
        if self.dota2_process is not None:
            self.dota2_process.terminate()
            self.dota2_process = None
            self.update_status_dota2("Автопик остановлен.")
            self.toggle_buttons()

    def stop_dota3_script(self):
        if self.dota3_process is not None:
            self.dota3_process.terminate()
            self.dota3_process = None
            self.update_status_dota3("Автозакуп остановлен.")
            self.auto_purchase_checkbox.setText('Включение автозакупа')
            self.auto_purchase_checkbox.setCheckState(QtCore.Qt.Unchecked)

    def start_both_scripts(self):
        self.on_start_dota_click()
        self.on_start_dota2_click()

    def stop_both_scripts(self):
        self.stop_dota_script()
        self.stop_dota2_script()
        self.stop_dota3_script()

    def on_start_dota_click(self):
        if self.dota_process is None:
            self.update_status_dota("Автопоиск запущен...")
            repeat_count = self.repeat_count_spinbox_dota.value()
            self.dota_process = subprocess.Popen(["python", "dota.py", str(repeat_count)])
            self.toggle_buttons()
        else:
            self.update_status_dota("Автопоиск уже запущен.")

    def on_start_dota2_click(self):
        if self.dota2_process is None:
            self.update_status_dota2("Автопик запущен...")
            repeat_count = self.repeat_count_spinbox_dota2.value()
            with open("repeat_count.txt", "w") as file:
                file.write(str(repeat_count))
            self.dota2_process = subprocess.Popen(["python", "dota2.py"])
            self.toggle_buttons()
        else:
            self.update_status_dota2("Автопик уже запущен.")

    def on_auto_purchase_toggle(self, state):
        if state == QtCore.Qt.Checked:
            self.start_dota3_script()
        else:
            self.stop_dota3_script()

    def start_dota3_script(self):
        if self.dota3_process is None:
            self.update_status_dota3("Автозакуп запущен...")
            self.dota3_process = subprocess.Popen(["python", "dota3.py"])
            self.auto_purchase_checkbox.setText('Выключить автозакуп')
        else:
            self.update_status_dota3("Автозакуп уже запущен.")

    def update_status_dota(self, message):
        self.status_label_dota.setText(message)

    def update_status_dota2(self, message):
        self.status_label_dota2.setText(message)

    def update_status_dota3(self, message):
        self.status_label_dota3.setText(message)

    def toggle_buttons(self):
        dota_running = self.dota_process is not None
        dota2_running = self.dota2_process is not None

        self.start_dota_button.setEnabled(not dota_running)
        self.stop_dota_button.setEnabled(dota_running)
        self.start_dota2_button.setEnabled(not dota2_running)
        self.stop_dota2_button.setEnabled(dota2_running)

        self.start_both_button.setEnabled(not (dota_running or dota2_running))
        self.stop_both_button.setEnabled(dota_running or dota2_running)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
