import sys
from PyQt5 import QtWidgets, QtCore
import subprocess
import os
import time

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.dota_process = None
        self.dota2_process = None
        self.dota3_process = None
        self.initUI()
        self.initFileWatcher()

    def initUI(self):
        self.setGeometry(100, 100, 750, 550)
        self.setWindowTitle('Jo4erio&4epuha')

        layout = QtWidgets.QGridLayout()

        # Столбец "Автопоиск (dota.py)"
        layout.addWidget(QtWidgets.QLabel('Автопоиск (dota.py):'), 0, 0)
        self.repeat_count_spinbox_dota = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota.setMinimum(1)
        self.repeat_count_spinbox_dota.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota, 1, 0)

        self.toggle_auto_search_checkbox = QtWidgets.QCheckBox('Запустить автопоиск', self)
        self.toggle_auto_search_checkbox.clicked.connect(self.on_toggle_auto_search_dota)
        layout.addWidget(self.toggle_auto_search_checkbox, 2, 0)

        self.status_label_dota = QtWidgets.QLabel('Ожидание запуска автопоиска...', self)
        layout.addWidget(self.status_label_dota, 3, 0)

        # Столбец "Автопик (dota2.py)"
        layout.addWidget(QtWidgets.QLabel('Автопик (dota2.py):'), 0, 1)
        self.repeat_count_spinbox_dota2 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota2.setMinimum(1)
        self.repeat_count_spinbox_dota2.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota2, 1, 1)

        self.toggle_auto_pick_checkbox = QtWidgets.QCheckBox('Запустить автопик', self)
        self.toggle_auto_pick_checkbox.clicked.connect(self.on_toggle_auto_pick_dota2)
        layout.addWidget(self.toggle_auto_pick_checkbox, 2, 1)

        self.status_label_dota2 = QtWidgets.QLabel('Ожидание запуска автопика...', self)
        layout.addWidget(self.status_label_dota2, 3, 1)

        # Столбец "Автозакуп (dota3.py)"
        layout.addWidget(QtWidgets.QLabel('Автозакуп (dota3.py):'), 0, 2)
        self.repeat_count_spinbox_dota3 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota3.setMinimum(1)
        self.repeat_count_spinbox_dota3.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota3, 1, 2)

        self.toggle_auto_purchase_checkbox = QtWidgets.QCheckBox('Включить автозакуп', self)
        self.toggle_auto_purchase_checkbox.clicked.connect(self.toggle_auto_purchase_dota3)
        layout.addWidget(self.toggle_auto_purchase_checkbox, 2, 2)

        self.status_label_dota3 = QtWidgets.QLabel('Ожидание запуска автозакупа...', self)
        layout.addWidget(self.status_label_dota3, 3, 2)

        # Кнопки для запуска и остановки всех процессов
        self.start_both_button = QtWidgets.QPushButton('Запустить все процессы', self)
        self.start_both_button.clicked.connect(self.start_both_scripts)
        layout.addWidget(self.start_both_button, 4, 0)

        self.stop_both_button = QtWidgets.QPushButton('Завершить все процессы', self)
        self.stop_both_button.clicked.connect(self.stop_both_scripts)
        self.stop_both_button.setEnabled(False)
        layout.addWidget(self.stop_both_button, 4, 1)

        self.setLayout(layout)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def initFileWatcher(self):
        self.file_watcher = QtCore.QFileSystemWatcher(self)
        self.file_watcher.addPath(os.getcwd())
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)

    def on_directory_changed(self, path):
        self.check_auto_search_completion()
        self.check_auto_pick_completion()
        self.check_auto_buy_status()

        # Проверка на наличие файла autosearch.txt
        if os.path.exists("autosearch.txt"):
            self.stop_dota_script()
            self.toggle_auto_search_checkbox.setChecked(False)
            self.safe_remove_file("autosearch.txt")
            self.safe_remove_file("repeat-dota.txt")
            self.update_status_dota("Автопоиск завершён.")

        # Проверка на наличие файла autobuy.txt
        if os.path.exists("autobuy.txt"):
            self.stop_dota3_script()
            self.toggle_auto_purchase_checkbox.setChecked(False)
            self.safe_remove_file("autobuy.txt")
            self.safe_remove_file("repeat-dota3.txt")
            self.update_status_dota3("Автозакуп завершён.")

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
        if os.path.exists("autobuy.txt"):
            self.safe_remove_file("autobuy.txt")
            self.toggle_auto_purchase_checkbox.setChecked(False)
            self.safe_remove_file("repeat-dota3.txt")

    def on_toggle_auto_search_dota(self):
        if self.toggle_auto_search_checkbox.isChecked():
            self.start_dota_script()
        else:
            self.stop_dota_script()

    def on_toggle_auto_pick_dota2(self):
        if self.toggle_auto_pick_checkbox.isChecked():
            self.start_dota2_script()
        else:
            self.stop_dota2_script()

    def toggle_auto_purchase_dota3(self):
        if self.toggle_auto_purchase_checkbox.isChecked():
            self.start_dota3_script()
        else:
            self.stop_dota3_script()

    def start_dota_script(self):
        if self.dota_process is None:
            self.update_status_dota("Автопоиск запущен...")
            repeat_count = self.repeat_count_spinbox_dota.value()
            with open("repeat-dota.txt", "w") as file:
                file.write(str(repeat_count))
            self.dota_process = subprocess.Popen(["python", "dota.py"])
            self.toggle_auto_search_checkbox.setText('Отключить автопоиск')
            self.toggle_buttons()
        else:
            self.update_status_dota("Автопоиск уже запущен.")

    def stop_dota_script(self):
        if self.dota_process is not None:
            self.dota_process.terminate()
            self.dota_process = None
            self.safe_remove_file("repeat-dota.txt")  # Удаление файла repeat-dota.txt
            self.safe_remove_file("autosearch.txt")  # Удаление файла autosearch.txt
            self.toggle_auto_search_checkbox.setText('Запустить автопоиск')
            self.toggle_buttons()

    def start_dota2_script(self):
        if self.dota2_process is None:
            self.update_status_dota2("Автопик запущен...")
            repeat_count = self.repeat_count_spinbox_dota2.value()
            with open("repeat-dota2.txt", "w") as file:
                file.write(str(repeat_count))
            self.dota2_process = subprocess.Popen(["python", "dota2.py"])
            self.toggle_auto_pick_checkbox.setText('Отключить автопик')
            self.toggle_buttons()
        else:
            self.update_status_dota2("Автопик уже запущен.")

    def stop_dota2_script(self):
        if self.dota2_process is not None:
            self.dota2_process.terminate()
            self.dota2_process = None
            self.safe_remove_file("repeat-dota2.txt")  # Удаление файла repeat-dota2.txt
            self.safe_remove_file("autopick.txt")  # Удаление файла autopick.txt
            self.toggle_auto_pick_checkbox.setText('Запустить автопик')
            self.toggle_buttons()

    def start_dota3_script(self):
        if self.dota3_process is None:
            self.update_status_dota3("Автозакуп запущен...")
            repeat_count = self.repeat_count_spinbox_dota3.value()
            with open("repeat-dota3.txt", "w") as file:
                file.write(str(repeat_count))
            self.dota3_process = subprocess.Popen(["python", "dota3.py"])
            self.toggle_auto_purchase_checkbox.setText('Отключить автозакуп')
            self.toggle_buttons()
        else:
            self.update_status_dota3("Автозакуп уже запущен.")

    def stop_dota3_script(self):
        if self.dota3_process is not None:
            self.dota3_process.terminate()
            self.dota3_process = None
            self.safe_remove_file("repeat-dota3.txt")  # Удаление файла repeat-dota3.txt
            self.toggle_auto_purchase_checkbox.setText('Включить автозакуп')
            self.toggle_buttons()

    def start_both_scripts(self):
        self.start_dota_script()
        self.start_dota2_script()
        self.start_dota3_script()

    def stop_both_scripts(self):
        self.stop_dota_script()
        self.stop_dota2_script()
        self.stop_dota3_script()

    def update_status_dota(self, message):
        self.status_label_dota.setText(message)

    def update_status_dota2(self, message):
        self.status_label_dota2.setText(message)

    def update_status_dota3(self, message):
        self.status_label_dota3.setText(message)

    def toggle_buttons(self):
        dota_running = self.dota_process is not None
        dota2_running = self.dota2_process is not None
        dota3_running = self.dota3_process is not None

        self.toggle_auto_search_checkbox.setEnabled(True)
        self.toggle_auto_pick_checkbox.setEnabled(True)
        self.toggle_auto_purchase_checkbox.setEnabled(True)

        if dota_running:
            self.toggle_auto_search_checkbox.setChecked(True)
        else:
            self.toggle_auto_search_checkbox.setChecked(False)

        if dota2_running:
            self.toggle_auto_pick_checkbox.setChecked(True)
        else:
            self.toggle_auto_pick_checkbox.setChecked(False)

        if dota3_running:
            self.toggle_auto_purchase_checkbox.setChecked(True)
        else:
            self.toggle_auto_purchase_checkbox.setChecked(False)

        self.start_both_button.setEnabled(not (dota_running or dota2_running or dota3_running))
        self.stop_both_button.setEnabled(dota_running or dota2_running or dota3_running)

    def safe_remove_file(self, filename):
        try:
            time.sleep(0.1)  # небольшая задержка перед удалением файла
            if os.path.exists(filename):
                os.remove(filename)
        except PermissionError as e:
            print(f"Не удалось удалить файл {filename}: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
