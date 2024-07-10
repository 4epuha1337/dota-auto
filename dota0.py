import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
import subprocess

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

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

        self.populate_hero_icons()

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
        self.toggle_auto_search_checkbox.setChecked(True)
        self.toggle_auto_pick_checkbox.setChecked(True)
        self.toggle_auto_buy_checkbox.setChecked(True)

        self.dota_status = "Включено"
        self.dota2_status = "Включено"
        self.dota3_status = "Включено"

        self.delete_repeat_files()
        self.start_all_button.setEnabled(False)
        self.stop_all_button.setEnabled(True)
        self.start_selected_button.setEnabled(False)
        self.stop_selected_button.setEnabled(True)
        self.close_button.setEnabled(False)

        self.start_both_scripts()

    def stop_all_scripts(self):
        self.toggle_auto_search_checkbox.setChecked(False)
        self.toggle_auto_pick_checkbox.setChecked(False)
        self.toggle_auto_buy_checkbox.setChecked(False)

        self.dota_status = "Выключено"
        self.dota2_status = "Выключено"
        self.dota3_status = "Выключено"

        self.dota_cycles = 1
        self.dota2_cycles = 1
        self.dota3_cycles = 1

        self.delete_repeat_files()
        self.stop_both_scripts()
        self.start_all_button.setEnabled(True)
        self.stop_all_button.setEnabled(False)
        self.start_selected_button.setEnabled(True)
        self.stop_selected_button.setEnabled(False)
        self.close_button.setEnabled(True)

    def start_selected_scripts(self):
        if self.dota_status == "Включено":
            self.create_repeat_file('repeat_dota.txt', self.dota_cycles)
            self.start_dota_script()

        if self.dota2_status == "Включено":
            self.create_repeat_file('repeat_dota2.txt', self.dota2_cycles)
            self.start_dota2_script()
            self.create_selected_heroes_file(self.selected_heroes)

        if self.dota3_status == "Включено":
            self.create_repeat_file('repeat_dota3.txt', self.dota3_cycles)
            self.start_dota3_script()

        self.start_selected_button.setEnabled(False)
        self.stop_selected_button.setEnabled(True)

    def stop_selected_scripts(self):
        if self.dota_status == "В работе":
            self.stop_dota_script()

        if self.dota2_status == "В работе":
            self.stop_dota2_script()

        if self.dota3_status == "В работе":
            self.stop_dota3_script()

        self.start_selected_button.setEnabled(True)
        self.stop_selected_button.setEnabled(False)

    def close_application(self):
        self.stop_all_scripts()
        QtWidgets.qApp.quit()

    def create_repeat_files(self):
        if self.dota_status == "Включено":
            self.create_repeat_file('repeat_dota.txt', self.dota_cycles)

        if self.dota2_status == "Включено":
            self.create_repeat_file('repeat_dota2.txt', self.dota2_cycles)

        if self.dota3_status == "Включено":
            self.create_repeat_file('repeat_dota3.txt', self.dota3_cycles)

    def delete_repeat_files(self):
        if os.path.exists('repeat_dota.txt'):
            os.remove('repeat_dota.txt')

        if os.path.exists('repeat_dota2.txt'):
            os.remove('repeat_dota2.txt')

        if os.path.exists('repeat_dota3.txt'):
            os.remove('repeat_dota3.txt')
            
        if os.path.exists('selected_heroes.txt'):
            os.remove('selected_heroes.txt')
        

    def create_repeat_file(self, filename, cycles):
        with open(filename, 'w') as file:
            file.write(str(cycles))

    def start_both_scripts(self):
        if self.dota_status == "Включено":
            self.dota_process = subprocess.Popen([sys.executable, 'dota.py'])

        if self.dota2_status == "Включено":
            self.dota2_process = subprocess.Popen([sys.executable, 'dota2.py'])

        if self.dota3_status == "Включено":
            self.dota3_process = subprocess.Popen([sys.executable, 'dota3.py'])

    def stop_both_scripts(self):
        if self.dota_process:
            self.dota_process.terminate()
            self.dota_process = None

        if self.dota2_process:
            self.dota2_process.terminate()
            self.dota2_process = None

        if self.dota3_process:
            self.dota3_process.terminate()
            self.dota3_process = None

    def start_dota_script(self):
        self.dota_process = subprocess.Popen([sys.executable, 'dota.py'])

    def stop_dota_script(self):
        if self.dota_process:
            self.dota_process.terminate()
            self.dota_process = None

    def start_dota2_script(self):
        self.dota2_process = subprocess.Popen([sys.executable, 'dota2.py'])

    def stop_dota2_script(self):
        if self.dota2_process:
            self.dota2_process.terminate()
            self.dota2_process = None

    def start_dota3_script(self):
        self.dota3_process = subprocess.Popen([sys.executable, 'dota3.py'])

    def stop_dota3_script(self):
        if self.dota3_process:
            self.dota3_process.terminate()
            self.dota3_process = None

    def check_signal_flags(self):
        if os.path.exists('autosearch.txt'):
            self.stop_dota_script()
            self.dota_cycles = 1
            self.dota_status = "Выключено"
            self.toggle_auto_search_checkbox.setChecked(False)
            self.delete_repeat_files()
            os.remove('autosearch.txt')

        if os.path.exists('autopick.txt'):
            self.stop_dota2_script()
            self.dota2_cycles = 1
            self.dota2_status = "Выключено"
            self.toggle_auto_pick_checkbox.setChecked(False)
            self.delete_repeat_files()
            os.remove('autopick.txt')
            self.delete_selected_heroes_file()

        if os.path.exists('autobuy.txt'):
            self.stop_dota3_script()
            self.dota3_cycles = 1
            self.dota3_status = "Выключено"
            self.toggle_auto_buy_checkbox.setChecked(False)
            self.delete_repeat_files()
            os.remove('autobuy.txt')
            
    def delete_selected_heroes_file(self):
        if os.path.exists('selected_heroes.txt'):
            os.remove('selected_heroes.txt')

    def run(self):
        self.check_signal_flags()
        self.update_status_table()
        QtWidgets.qApp.exec_()

    def populate_hero_icons(self):
        icons_folder = 'icons/pretty heroes'
        heroes = os.listdir(icons_folder)
        row = 0
        col = 0
        for hero in heroes:
            hero_button = QtWidgets.QPushButton()
            hero_icon = QtGui.QPixmap(os.path.join(icons_folder, hero)).scaled(80, 80, QtCore.Qt.KeepAspectRatio)
            hero_button.setIcon(QtGui.QIcon(hero_icon))
            hero_button.setIconSize(QtCore.QSize(80, 80))
            hero_button.setToolTip(hero.split('.')[0])  # Устанавливаем название героя без расширения
            hero_button.clicked.connect(self.select_hero)
            self.selected_heroes_layout.addWidget(hero_button, row, col)
            col += 1
            if col >= 5:
                col = 0
                row += 1

    def select_hero(self):
        sender_button = self.sender()
        hero_name = sender_button.toolTip()
        if hero_name in self.selected_heroes:
            self.selected_heroes.remove(hero_name)
            sender_button.setStyleSheet("")
        else:
            self.selected_heroes.append(hero_name)
            sender_button.setStyleSheet("border: 2px solid red;")

        # Обновляем информацию о выбранных героях
        self.update_heroes_information()

    def update_heroes_information(self):
        if len(self.selected_heroes) > 0:
            self.heroes_status_label.setText(f'Название героев: {", ".join(self.selected_heroes)}')
            self.heroes_count_label.setText(f'Количество героев: {len(self.selected_heroes)}')
        else:
            self.heroes_status_label.setText('Название героев: (не выбрано)')
            self.heroes_count_label.setText('Количество героев: (0)')

    def create_selected_heroes_file(self, selected_heroes):
        with open('selected_heroes.txt', 'w') as file:
            for hero in selected_heroes:
                file.write(hero + '\n')

    def delete_selected_heroes_file(self):
        if os.path.exists('selected_heroes.txt'):
            os.remove('selected_heroes.txt')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.run()
