import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
import subprocess

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.signal_files = {
            'autosearch': 'autosearch.txt',
            'autopick': 'autopick.txt',
            'autobuy': 'autobuy.txt'
        }

        self.setup_timer()

    def setup_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_for_auto_files)
        self.timer.start(5000)  # Проверяем каждые 5 секунд

        self.dota_process = None
        self.dota2_process = None
        self.dota3_process = None

        self.dota_status = "Выключено"
        self.dota2_status = "Выключено"
        self.dota3_status = "Выключено"

        self.dota_cycles = 1
        self.dota2_cycles = 1
        self.dota3_cycles = 1

        self.selected_heroes = []  # список выбранных героев для Autopick

        self.initUI()
        self.check_for_auto_files()  # Проверяем наличие файлов при запуске

    def initUI(self):
        self.setWindowTitle('Dota Automation')
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QtWidgets.QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.main_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.main_tab, "Главная")

        self.autosearch_tab = self.create_autosearch_tab()
        self.tabs.addTab(self.autosearch_tab, "Autosearch")

        self.autopick_tab = self.create_autopick_tab()
        self.tabs.addTab(self.autopick_tab, "Autopick")

        self.autobuy_tab = self.create_autobuy_tab()
        self.tabs.addTab(self.autobuy_tab, "Autobuy")

        self.create_main_tab_buttons()

        self.show()

    def create_main_tab_buttons(self):
        grid_layout = QtWidgets.QGridLayout(self.main_tab)

        self.start_all_button = QtWidgets.QPushButton('Запустить все', self)
        self.start_all_button.clicked.connect(self.start_all_scripts)
        grid_layout.addWidget(self.start_all_button, 0, 0)

        self.stop_all_button = QtWidgets.QPushButton('Остановить все', self)
        self.stop_all_button.clicked.connect(self.stop_all_scripts)
        grid_layout.addWidget(self.stop_all_button, 0, 1)

        self.start_selected_button = QtWidgets.QPushButton('Запустить выбранные', self)
        self.start_selected_button.clicked.connect(self.start_selected_scripts)
        grid_layout.addWidget(self.start_selected_button, 0, 2)

        self.stop_selected_button = QtWidgets.QPushButton('Остановить выбранные', self)
        self.stop_selected_button.clicked.connect(self.stop_selected_scripts)
        grid_layout.addWidget(self.stop_selected_button, 0, 3)

        self.close_button = QtWidgets.QPushButton('Закрыть', self)
        self.close_button.clicked.connect(self.close_application)
        grid_layout.addWidget(self.close_button, 0, 4)

        # Все кнопки на главной вкладке всегда доступны
        self.start_all_button.setEnabled(True)
        self.stop_all_button.setEnabled(True)
        self.start_selected_button.setEnabled(True)
        self.stop_selected_button.setEnabled(True)
        self.close_button.setEnabled(True)

        self.create_status_table(grid_layout)

    def create_status_table(self, grid_layout):
        scripts = [
            ("Autosearch", self.dota_status, f'Количество циклов: {self.dota_cycles}'),
            ("Autopick", self.dota2_status, f'Количество циклов: {self.dota2_cycles}'),
            ("Autobuy", self.dota3_status, f'Количество циклов: {self.dota3_cycles}')
        ]

        self.status_labels = {}
        self.cycle_labels = {}

        row = 1
        for script_name, status, cycles_text in scripts:
            script_label = QtWidgets.QLabel(script_name)
            grid_layout.addWidget(script_label, row, 0)

            status_label = QtWidgets.QLabel(f'Состояние: {status}')
            grid_layout.addWidget(status_label, row, 1)
            self.status_labels[script_name] = status_label

            cycles_label = QtWidgets.QLabel(cycles_text)
            grid_layout.addWidget(cycles_label, row, 2)
            self.cycle_labels[script_name] = cycles_label

            row += 1

    def create_autosearch_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel('Autosearch (dota.py):'))

        self.repeat_count_spinbox_dota = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota.setMinimum(1)
        self.repeat_count_spinbox_dota.setMaximum(100)
        self.repeat_count_spinbox_dota.setValue(self.dota_cycles)
        self.repeat_count_spinbox_dota.valueChanged.connect(self.update_dota_cycles)
        layout.addWidget(self.repeat_count_spinbox_dota)

        self.toggle_auto_search_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_search_checkbox.setChecked(False)
        self.toggle_auto_search_checkbox.stateChanged.connect(self.update_autosearch_checkbox)
        layout.addWidget(self.toggle_auto_search_checkbox)

        tab.setLayout(layout)
        return tab

    def create_autopick_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel('Autopick (dota2.py):'))

        self.repeat_count_spinbox_dota2 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota2.setMinimum(1)
        self.repeat_count_spinbox_dota2.setMaximum(100)
        self.repeat_count_spinbox_dota2.setValue(self.dota2_cycles)
        self.repeat_count_spinbox_dota2.valueChanged.connect(self.update_dota2_cycles)
        layout.addWidget(self.repeat_count_spinbox_dota2)

        self.toggle_auto_pick_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_pick_checkbox.setChecked(False)
        self.toggle_auto_pick_checkbox.stateChanged.connect(self.update_autopick_checkbox)
        layout.addWidget(self.toggle_auto_pick_checkbox)

        self.selected_heroes_scroll_area = QtWidgets.QScrollArea()
        self.selected_heroes_scroll_area.setWidgetResizable(True)
        self.selected_heroes_widget = QtWidgets.QWidget()
        self.selected_heroes_layout = QtWidgets.QGridLayout(self.selected_heroes_widget)
        self.selected_heroes_scroll_area.setWidget(self.selected_heroes_widget)
        layout.addWidget(self.selected_heroes_scroll_area)

        self.heroes_status_label = QtWidgets.QLabel('Название героев: (не выбрано)')
        layout.addWidget(self.heroes_status_label)

        self.heroes_count_label = QtWidgets.QLabel('Количество героев: (0)')
        layout.addWidget(self.heroes_count_label)

        self.populate_hero_icons()  # Call to method for hero icons

        tab.setLayout(layout)
        return tab

    def create_autobuy_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel('Autobuy (dota3.py):'))

        self.repeat_count_spinbox_dota3 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota3.setMinimum(1)
        self.repeat_count_spinbox_dota3.setMaximum(100)
        self.repeat_count_spinbox_dota3.setValue(self.dota3_cycles)
        self.repeat_count_spinbox_dota3.valueChanged.connect(self.update_dota3_cycles)
        layout.addWidget(self.repeat_count_spinbox_dota3)

        self.toggle_auto_buy_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_buy_checkbox.setChecked(False)
        self.toggle_auto_buy_checkbox.stateChanged.connect(self.update_autobuy_checkbox)
        layout.addWidget(self.toggle_auto_buy_checkbox)

        tab.setLayout(layout)
        return tab

    def update_autosearch_checkbox(self):
        if self.toggle_auto_search_checkbox.isChecked():
            self.toggle_auto_search_checkbox.setText("Включено")
            self.dota_status = "Включено"
        else:
            self.toggle_auto_search_checkbox.setText("Выключено")
            self.dota_status = "Выключено"
        self.update_status_table()

    def update_autopick_checkbox(self):
        if self.toggle_auto_pick_checkbox.isChecked():
            self.toggle_auto_pick_checkbox.setText("Включено")
            self.dota2_status = "Включено"
        else:
            self.toggle_auto_pick_checkbox.setText("Выключено")
            self.dota2_status = "Выключено"
        self.update_status_table()

    def update_autobuy_checkbox(self):
        if self.toggle_auto_buy_checkbox.isChecked():
            self.toggle_auto_buy_checkbox.setText("Включено")
            self.dota3_status = "Включено"
        else:
            self.toggle_auto_buy_checkbox.setText("Выключено")
            self.dota3_status = "Выключено"
        self.update_status_table()

    def update_dota_cycles(self, value):
        self.dota_cycles = value
        self.update_status_table()

    def update_dota2_cycles(self, value):
        self.dota2_cycles = value
        self.update_status_table()

    def update_dota3_cycles(self, value):
        self.dota3_cycles = value
        self.update_status_table()

    def update_status_table(self):
        self.status_labels["Autosearch"].setText(f'Состояние: {self.dota_status}')
        self.cycle_labels["Autosearch"].setText(f'Количество циклов: {self.dota_cycles}')

        self.status_labels["Autopick"].setText(f'Состояние: {self.dota2_status}')
        self.cycle_labels["Autopick"].setText(f'Количество циклов: {self.dota2_cycles}')

        self.status_labels["Autobuy"].setText(f'Состояние: {self.dota3_status}')
        self.cycle_labels["Autobuy"].setText(f'Количество циклов: {self.dota3_cycles}')

    def start_all_scripts(self):
        # Устанавливаем все чекбоксы в положение "Включено"
        self.toggle_auto_search_checkbox.setChecked(True)
        self.dota_status = "Включено"

        self.toggle_auto_pick_checkbox.setChecked(True)
        self.dota2_status = "Включено"

        self.toggle_auto_buy_checkbox.setChecked(True)
        self.dota3_status = "Включено"

        # Запускаем все скрипты
        self.start_dota_script()
        self.start_dota2_script()
        self.start_dota3_script()

        # Обновляем таблицу статусов
        self.update_status_table()


    def stop_all_scripts(self):
        # Останавливаем все скрипты
        self.stop_dota_script()
        self.stop_dota2_script()
        self.stop_dota3_script()

        # Устанавливаем все чекбоксы в положение "Выключено"
        self.toggle_auto_search_checkbox.setChecked(False)
        self.dota_status = "Выключено"

        self.toggle_auto_pick_checkbox.setChecked(False)
        self.dota2_status = "Выключено"

        self.toggle_auto_buy_checkbox.setChecked(False)
        self.dota3_status = "Выключено"

        # Обновляем таблицу статусов
        self.update_status_table()


    def start_selected_scripts(self):
        self.start_dota2_script()

    def stop_selected_scripts(self):
        self.stop_dota2_script()

    def start_dota_script(self):
        if self.dota_status == "Включено":
            self.dota_process = subprocess.Popen(['python', 'dota.py'])
            self.update_repeat_dota_file()

    def start_dota2_script(self):
        if self.dota2_status == "Включено":
            self.dota2_process = subprocess.Popen(['python', 'dota2.py'])
            self.update_repeat_dota2_file()
            self.update_selected_heroes_file()

    def start_dota3_script(self):
        if self.dota3_status == "Включено":
            self.dota3_process = subprocess.Popen(['python', 'dota3.py'])
            self.update_repeat_dota3_file()

    def stop_dota_script(self):
        if self.dota_process:
            self.dota_process.terminate()
            self.dota_process = None
            self.delete_repeat_dota_file()

    def stop_dota2_script(self):
        if self.dota2_process:
            self.dota2_process.terminate()
            self.dota2_process = None
            self.delete_repeat_dota2_file()
            self.delete_selected_heroes_file()

    def stop_dota3_script(self):
        if self.dota3_process:
            self.dota3_process.terminate()
            self.dota3_process = None
            self.delete_repeat_dota3_file()

    def close_application(self):
        self.stop_all_scripts()
        QtWidgets.qApp.quit()

    def populate_hero_icons(self):
        icons_folder = 'icons/pretty heroes'
        heroes = os.listdir(icons_folder)
        row, col = 0, 0
        for hero in heroes:
            if col == 4:
                col = 0
                row += 1
            hero_name = hero.split('.')[0].capitalize()
            button = QtWidgets.QPushButton(hero_name)
            button.setIcon(QtGui.QIcon(os.path.join(icons_folder, hero)))
            button.setIconSize(QtCore.QSize(64, 64))
            button.clicked.connect(lambda checked, name=hero_name, button=button: self.toggle_hero_selection(name, button))
            self.selected_heroes_layout.addWidget(button, row, col)
            col += 1

    def toggle_hero_selection(self, hero_name, sender_button):
        if hero_name in self.selected_heroes:
            self.selected_heroes.remove(hero_name)
            sender_button.setStyleSheet("")
        else:
            self.selected_heroes.append(hero_name)
            sender_button.setStyleSheet("border: 2px solid red;")
        self.update_selected_heroes_status()

    def update_selected_heroes_status(self):
        self.heroes_status_label.setText(f'Название героев: ({", ".join(self.selected_heroes)})')
        self.heroes_count_label.setText(f'Количество героев: ({len(self.selected_heroes)})')

    def update_selected_heroes_file(self):
        if self.selected_heroes:
            with open('selected_heroes.txt', 'w', encoding='utf-8') as f:
                for hero in self.selected_heroes:
                    f.write(f"{hero}.png , .\\icons\\heroes\\{hero.lower()}.png\n")

    def update_repeat_dota_file(self):
        if self.dota_process:
            with open('repeat_dota.txt', 'w') as f:
                f.write(str(self.dota_cycles))

    def update_repeat_dota2_file(self):
        if self.dota2_process:
            with open('repeat_dota2.txt', 'w') as f:
                f.write(str(self.dota2_cycles))

    def update_repeat_dota3_file(self):
        if self.dota3_process:
            with open('repeat_dota3.txt', 'w') as f:
                f.write(str(self.dota3_cycles))

    def delete_repeat_dota_file(self):
        if os.path.exists('repeat_dota.txt'):
            os.remove('repeat_dota.txt')

    def delete_repeat_dota2_file(self):
        if os.path.exists('repeat_dota2.txt'):
            os.remove('repeat_dota2.txt')

    def delete_repeat_dota3_file(self):
        if os.path.exists('repeat_dota3.txt'):
            os.remove('repeat_dota3.txt')

    def delete_selected_heroes_file(self):
        if os.path.exists('selected_heroes.txt'):
            os.remove('selected_heroes.txt')
            
    def check_for_auto_files(self):
        for action, file_name in self.signal_files.items():
            if os.path.exists(file_name):
                print(f"Файл {file_name} обнаружен")
                self.handle_signal_file(action, file_name)

    def handle_signal_file(self, action, signal_file):
        if action == 'autosearch':
            self.stop_dota_script()
            self.toggle_auto_search_checkbox.setChecked(False)
            self.dota_status = "Выключено"
            self.delete_repeat_dota_file()
            print(f"Чекбокс на вкладке dota.py сброшен и файлы удалены")
        elif action == 'autopick':
            self.stop_dota2_script()
            self.toggle_auto_pick_checkbox.setChecked(False)
            self.dota2_status = "Выключено"
            self.delete_repeat_dota2_file()
            self.delete_selected_heroes_file()
            print(f"Чекбокс на вкладке dota2.py сброшен и файлы удалены")
        elif action == 'autobuy':
            self.stop_dota3_script()
            self.toggle_auto_buy_checkbox.setChecked(False)
            self.dota3_status = "Выключено"
            self.delete_repeat_dota3_file()
            print(f"Чекбокс на вкладке dota3.py сброшен и файлы удалены")

        self.update_status_table()
        if os.path.exists(signal_file):
            os.remove(signal_file)
            print(f"Файл {signal_file} удален")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
