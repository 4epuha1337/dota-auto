import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui

class Communicate(QtCore.QObject):
    autosearch_found = QtCore.pyqtSignal()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.dota_status = "Выключено"
        self.dota2_status = "Выключено"
        self.dota3_status = "Выключено"
        self.selected_heroes = []
        self.communicate = Communicate()
        self.initUI()
        self.initFileWatcher()
        self.dota_process = None
        self.dota2_process = None
        self.dota3_process = None
        self.communicate.autosearch_found.connect(self.check_auto_search_completion)

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Jo4erio&4epuha')

        layout = QtWidgets.QGridLayout()

        # Tabs
        self.tabs = QtWidgets.QTabWidget(self)
        tab_main = self.create_main_tab()
        tab_autosearch = self.create_autosearch_tab()
        tab_autopick = self.create_autopick_tab()
        tab_autobuy = self.create_autobuy_tab()
        
        self.tabs.addTab(tab_main, "Главная")
        self.tabs.addTab(tab_autosearch, "Autosearch")
        self.tabs.addTab(tab_autopick, "Autopick")
        self.tabs.addTab(tab_autobuy, "Autobuy")
        
        layout.addWidget(self.tabs, 0, 0, 1, 1)
        
        self.setLayout(layout)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def create_main_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        # Column 1: Autosearch (dota.py)
        layout.addWidget(QtWidgets.QLabel('Autosearch (dota.py):'), 0, 0)
        self.status_label_dota_status = QtWidgets.QLabel(f'Состояние: {self.dota_status}', self)
        layout.addWidget(self.status_label_dota_status, 1, 0)
        
        self.status_label_dota_cycles = QtWidgets.QLabel('Количество циклов: 1', self)
        layout.addWidget(self.status_label_dota_cycles, 2, 0)

        # Column 2: Autopick (dota2.py)
        layout.addWidget(QtWidgets.QLabel('Autopick (dota2.py):'), 0, 1)
        self.status_label_dota2_status = QtWidgets.QLabel(f'Состояние: {self.dota2_status}', self)
        layout.addWidget(self.status_label_dota2_status, 1, 1)
        
        self.status_label_dota2_cycles = QtWidgets.QLabel('Количество циклов: 1', self)
        layout.addWidget(self.status_label_dota2_cycles, 2, 1)

        # Column 3: Autobuy (dota3.py)
        layout.addWidget(QtWidgets.QLabel('Autobuy (dota3.py):'), 0, 2)
        self.status_label_dota3_status = QtWidgets.QLabel(f'Состояние: {self.dota3_status}', self)
        layout.addWidget(self.status_label_dota3_status, 1, 2)
        
        self.status_label_dota3_cycles = QtWidgets.QLabel('Количество циклов: 1', self)
        layout.addWidget(self.status_label_dota3_cycles, 2, 2)

        # Control buttons for all scripts
        self.start_both_button = QtWidgets.QPushButton('Запустить все процессы', self)
        self.start_both_button.clicked.connect(self.start_both_scripts)
        layout.addWidget(self.start_both_button, 3, 0)

        self.stop_both_button = QtWidgets.QPushButton('Завершить все процессы', self)
        self.stop_both_button.clicked.connect(self.stop_both_scripts)
        layout.addWidget(self.stop_both_button, 3, 1)

        self.start_selected_button = QtWidgets.QPushButton('Включить программу', self)
        self.start_selected_button.clicked.connect(self.start_selected_scripts)
        layout.addWidget(self.start_selected_button, 3, 2)

        self.stop_selected_button = QtWidgets.QPushButton('Выключить программу', self)
        self.stop_selected_button.clicked.connect(self.stop_selected_scripts)
        layout.addWidget(self.stop_selected_button, 3, 3)

        tab.setLayout(layout)
        return tab

    def create_autosearch_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel('Autosearch (dota.py):'))
        
        self.repeat_count_spinbox_dota = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota.setMinimum(1)
        self.repeat_count_spinbox_dota.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota)

        self.toggle_auto_search_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_search_checkbox.setChecked(False)
        self.toggle_auto_search_checkbox.clicked.connect(self.toggle_auto_search)
        layout.addWidget(self.toggle_auto_search_checkbox)

        tab.setLayout(layout)
        return tab

    def create_autopick_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        layout.addWidget(QtWidgets.QLabel('Autopick (dota2.py):'), 0, 0)
        
        self.repeat_count_spinbox_dota2 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota2.setMinimum(1)
        self.repeat_count_spinbox_dota2.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota2, 1, 0)

        self.toggle_auto_pick_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_pick_checkbox.setChecked(False)
        self.toggle_auto_pick_checkbox.clicked.connect(self.toggle_auto_pick)
        layout.addWidget(self.toggle_auto_pick_checkbox, 2, 0)

        # Добавление выбора героев
        heroes_layout = QtWidgets.QGridLayout()
        heroes_dir = "./icons/heroes/"

        # Данные о героях
        heroes_data = [
            ("Anti-Mage", "icons/heroes/anti_mage.png"),
            ("Axe", "icons/heroes/axe.png"),
            ("Bane", "icons/heroes/bane.png"),
            ("Bloodseeker", "icons/heroes/bloodseeker.png"),
            ("Crystal Maiden", "icons/heroes/crystal_maiden.png"),
            ("Drow Ranger", "icons/heroes/drow_ranger.png"),
            ("Earthshaker", "icons/heroes/earthshaker.png"),
            ("Juggernaut", "icons/heroes/juggernaut.png"),
            ("Mirana", "icons/heroes/mirana.png"),
            ("Morphling", "icons/heroes/morphling.png"),
            ("Shadow Fiend", "icons/heroes/shadow_fiend.png"),
            ("Phantom Lancer", "icons/heroes/phantom_lancer.png"),
            ("Puck", "icons/heroes/puck.png"),
            ("Pudge", "icons/heroes/pudge.png"),
            ("Razor", "icons/heroes/razor.png"),
            ("Sand King", "icons/heroes/sand_king.png"),
            ("Storm Spirit", "icons/heroes/storm_spirit.png"),
            ("Sven", "icons/heroes/sven.png"),
            ("Tiny", "icons/heroes/tiny.png"),
            ("Vengeful Spirit", "icons/heroes/vengeful_spirit.png"),
            ("Windranger", "icons/heroes/windranger.png"),
            ("Zeus", "icons/heroes/zeus.png"),
            ("Kunkka", "icons/heroes/kunkka.png"),
            ("Lina", "icons/heroes/lina.png"),
            ("Lion", "icons/heroes/lion.png"),
            ("Shadow Shaman", "icons/heroes/shadow_shaman.png"),
            ("Slardar", "icons/heroes/slardar.png"),
            ("Tidehunter", "icons/heroes/tidehunter.png"),
            ("Witch Doctor", "icons/heroes/witch_doctor.png"),
            ("Lich", "icons/heroes/lich.png"),
            ("Riki", "icons/heroes/riki.png"),
            ("Enigma", "icons/heroes/enigma.png"),
            ("Tinker", "icons/heroes/tinker.png"),
            ("Sniper", "icons/heroes/sniper.png"),
            ("Necrophos", "icons/heroes/necrophos.png"),
            ("Warlock", "icons/heroes/warlock.png"),
            ("Beastmaster", "icons/heroes/beastmaster.png"),
            ("Queen of Pain", "icons/heroes/queen_of_pain.png"),
            ("Venomancer", "icons/heroes/venomancer.png"),
            ("Faceless Void", "icons/heroes/faceless_void.png"),
            ("Wraith King", "icons/heroes/wraith_king.png"),
            ("Death Prophet", "icons/heroes/death_prophet.png"),
            ("Phantom Assassin", "icons/heroes/phantom_assassin.png"),
            ("Pugna", "icons/heroes/pugna.png"),
            ("Templar Assassin", "icons/heroes/templar_assassin.png"),
            ("Viper", "icons/heroes/viper.png"),
            ("Luna", "icons/heroes/luna.png"),
            ("Dragon Knight", "icons/heroes/dragon_knight.png"),
            ("Dazzle", "icons/heroes/dazzle.png"),
            ("Clockwerk", "icons/heroes/clockwerk.png"),
            ("Leshrac", "icons/heroes/leshrac.png"),
            ("Nature's Prophet", "icons/heroes/natures_prophet.png"),
            ("Lifestealer", "icons/heroes/lifestealer.png"),
            ("Dark Seer", "icons/heroes/dark_seer.png"),
            ("Clinkz", "icons/heroes/clinkz.png"),
            ("Omniknight", "icons/heroes/omniknight.png"),
            ("Enchantress", "icons/heroes/enchantress.png"),
            ("Huskar", "icons/heroes/huskar.png"),
            ("Night Stalker", "icons/heroes/night_stalker.png"),
            ("Broodmother", "icons/heroes/broodmother.png"),
            ("Bounty Hunter", "icons/heroes/bounty_hunter.png"),
            ("Weaver", "icons/heroes/weaver.png"),
            ("Jakiro", "icons/heroes/jakiro.png"),
            ("Batrider", "icons/heroes/batrider.png"),
            ("Chen", "icons/heroes/chen.png"),
            ("Spectre", "icons/heroes/spectre.png"),
            ("Ancient Apparition", "icons/heroes/ancient_apparition.png"),
            ("Doom", "icons/heroes/doom.png"),
            ("Ursa", "icons/heroes/ursa.png"),
            ("Spirit Breaker", "icons/heroes/spirit_breaker.png"),
            ("Gyrocopter", "icons/heroes/gyrocopter.png"),
            ("Alchemist", "icons/heroes/alchemist.png"),
            ("Invoker", "icons/heroes/invoker.png"),
            ("Silencer", "icons/heroes/silencer.png"),
            ("Outworld Devourer", "icons/heroes/outworld_devourer.png"),
            ("Lycan", "icons/heroes/lycan.png"),
            ("Brewmaster", "icons/heroes/brewmaster.png"),
            ("Shadow Demon", "icons/heroes/shadow_demon.png"),
            ("Lone Druid", "icons/heroes/lone_druid.png"),
            ("Chaos Knight", "icons/heroes/chaos_knight.png"),
            ("Meepo", "icons/heroes/meepo.png"),
            ("Treant Protector", "icons/heroes/treant_protector.png"),
            ("Ogre Magi", "icons/heroes/ogre_magi.png"),
            ("Undying", "icons/heroes/undying.png"),
            ("Rubick", "icons/heroes/rubick.png"),
            ("Disruptor", "icons/heroes/disruptor.png"),
            ("Nyx Assassin", "icons/heroes/nyx_assassin.png"),
            ("Naga Siren", "icons/heroes/naga_siren.png"),
            ("Keeper of the Light", "icons/heroes/keeper_of_the_light.png"),
            ("Io", "icons/heroes/io.png"),
            ("Visage", "icons/heroes/visage.png"),
            ("Slark", "icons/heroes/slark.png"),
            ("Medusa", "icons/heroes/medusa.png"),
            ("Troll Warlord", "icons/heroes/troll_warlord.png"),
            ("Centaur Warrunner", "icons/heroes/centaur_warrunner.png"),
            ("Magnus", "icons/heroes/magnus.png"),
            ("Timbersaw", "icons/heroes/timbersaw.png"),
            ("Bristleback", "icons/heroes/bristleback.png"),
            ("Tusk", "icons/heroes/tusk.png"),
            ("Skywrath Mage", "icons/heroes/skywrath_mage.png"),
            ("Abaddon", "icons/heroes/abaddon.png"),
            ("Elder Titan", "icons/heroes/elder_titan.png"),
            ("Legion Commander", "icons/heroes/legion_commander.png"),
            ("Ember Spirit", "icons/heroes/ember_spirit.png"),
            ("Earth Spirit", "icons/heroes/earth_spirit.png"),
            ("Underlord", "icons/heroes/underlord.png"),
            ("Terrorblade", "icons/heroes/terrorblade.png"),
            ("Phoenix", "icons/heroes/phoenix.png"),
            ("Oracle", "icons/heroes/oracle.png"),
            ("Techies", "icons/heroes/techies.png"),
            ("Winter Wyvern", "icons/heroes/winter_wyvern.png"),
            ("Arc Warden", "icons/heroes/arc_warden.png"),
            ("Monkey King", "icons/heroes/monkey_king.png"),
            ("Dark Willow", "icons/heroes/dark_willow.png"),
            ("Pangolier", "icons/heroes/pangolier.png"),
            ("Grimstroke", "icons/heroes/grimstroke.png"),
            ("Hoodwink", "icons/heroes/hoodwink.png"),
            ("Void Spirit", "icons/heroes/void_spirit.png"),
            ("Snapfire", "icons/heroes/snapfire.png"),
            ("Mars", "icons/heroes/mars.png"),
            ("Dawnbreaker", "icons/heroes/dawnbreaker.png"),
            ("Marci", "icons/heroes/marci.png"),
            ("Primal Beast", "icons/heroes/primal_beast.png"),
            ("Muerta", "icons/heroes/muerta.png")
        ]

        self.hero_buttons = []

        # Создание кнопок для каждого героя
        row = 0
        col = 0
        for hero_name, hero_icon_path in heroes_data:
            hero_button = QtWidgets.QPushButton(hero_name, self)
            hero_button.setIcon(QtGui.QIcon(hero_icon_path))
            hero_button.setIconSize(QtCore.QSize(64, 64))
            hero_button.clicked.connect(lambda checked, name=hero_name: self.hero_button_clicked(name))
            self.hero_buttons.append(hero_button)
            heroes_layout.addWidget(hero_button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(heroes_layout, 3, 0)

        tab.setLayout(layout)
        return tab

    def create_autobuy_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel('Autobuy (dota3.py):'))
        
        self.repeat_count_spinbox_dota3 = QtWidgets.QSpinBox(self)
        self.repeat_count_spinbox_dota3.setMinimum(1)
        self.repeat_count_spinbox_dota3.setMaximum(100)
        layout.addWidget(self.repeat_count_spinbox_dota3)

        self.toggle_auto_buy_checkbox = QtWidgets.QCheckBox('Выключено', self)
        self.toggle_auto_buy_checkbox.setChecked(False)
        self.toggle_auto_buy_checkbox.clicked.connect(self.toggle_auto_buy)
        layout.addWidget(self.toggle_auto_buy_checkbox)

        tab.setLayout(layout)
        return tab

    def initFileWatcher(self):
        self.file_watcher_dota = QtCore.QFileSystemWatcher()
        self.file_watcher_dota.addPath('dota.py')
        self.file_watcher_dota.fileChanged.connect(self.dota_script_changed)

        self.file_watcher_dota2 = QtCore.QFileSystemWatcher()
        self.file_watcher_dota2.addPath('dota2.py')
        self.file_watcher_dota2.fileChanged.connect(self.dota2_script_changed)

        self.file_watcher_dota3 = QtCore.QFileSystemWatcher()
        self.file_watcher_dota3.addPath('dota3.py')
        self.file_watcher_dota3.fileChanged.connect(self.dota3_script_changed)

    def dota_script_changed(self):
        if self.dota_process:
            self.dota_process.kill()
            self.dota_process = None
            self.dota_status = "Выключено"
            self.status_label_dota_status.setText(f'Состояние: {self.dota_status}')

    def dota2_script_changed(self):
        if self.dota2_process:
            self.dota2_process.kill()
            self.dota2_process = None
            self.dota2_status = "Выключено"
            self.status_label_dota2_status.setText(f'Состояние: {self.dota2_status}')

    def dota3_script_changed(self):
        if self.dota3_process:
            self.dota3_process.kill()
            self.dota3_process = None
            self.dota3_status = "Выключено"
            self.status_label_dota3_status.setText(f'Состояние: {self.dota3_status}')

    def toggle_auto_search(self, state):
        if state:
            self.toggle_auto_search_checkbox.setText('Включено')
            self.dota_status = "Включено"
            self.status_label_dota_status.setText(f'Состояние: {self.dota_status}')
        else:
            self.toggle_auto_search_checkbox.setText('Выключено')
            self.dota_status = "Выключено"
            self.status_label_dota_status.setText(f'Состояние: {self.dota_status}')

    def toggle_auto_pick(self, state):
        if state:
            self.toggle_auto_pick_checkbox.setText('Включено')
            self.dota2_status = "Включено"
            self.status_label_dota2_status.setText(f'Состояние: {self.dota2_status}')
        else:
            self.toggle_auto_pick_checkbox.setText('Выключено')
            self.dota2_status = "Выключено"
            self.status_label_dota2_status.setText(f'Состояние: {self.dota2_status}')

    def toggle_auto_buy(self, state):
        if state:
            self.toggle_auto_buy_checkbox.setText('Включено')
            self.dota3_status = "Включено"
            self.status_label_dota3_status.setText(f'Состояние: {self.dota3_status}')
        else:
            self.toggle_auto_buy_checkbox.setText('Выключено')
            self.dota3_status = "Выключено"
            self.status_label_dota3_status.setText(f'Состояние: {self.dota3_status}')

    def start_both_scripts(self):
        if not self.dota_process:
            self.dota_process = subprocess.Popen(['python', 'dota.py'])
            self.dota_status = "Запущено"
            self.status_label_dota_status.setText(f'Состояние: {self.dota_status}')

        if not self.dota2_process:
            self.dota2_process = subprocess.Popen(['python', 'dota2.py'])
            self.dota2_status = "Запущено"
            self.status_label_dota2_status.setText(f'Состояние: {self.dota2_status}')

        if not self.dota3_process:
            self.dota3_process = subprocess.Popen(['python', 'dota3.py'])
            self.dota3_status = "Запущено"
            self.status_label_dota3_status.setText(f'Состояние: {self.dota3_status}')

    def stop_both_scripts(self):
        if self.dota_process:
            self.dota_process.kill()
            self.dota_process = None
            self.dota_status = "Выключено"
            self.status_label_dota_status.setText(f'Состояние: {self.dota_status}')

        if self.dota2_process:
            self.dota2_process.kill()
            self.dota2_process = None
            self.dota2_status = "Выключено"
            self.status_label_dota2_status.setText(f'Состояние: {self.dota2_status}')

        if self.dota3_process:
            self.dota3_process.kill()
            self.dota3_process = None
            self.dota3_status = "Выключено"
            self.status_label_dota3_status.setText(f'Состояние: {self.dota3_status}')

    def start_selected_scripts(self):
        if self.toggle_auto_search_checkbox.isChecked():
            self.dota_process = subprocess.Popen(['python', 'dota.py'])
            self.dota_status = "Запущено"
            self.status_label_dota_status.setText(f'Состояние: {self.dota_status}')

        if self.toggle_auto_pick_checkbox.isChecked():
            self.dota2_process = subprocess.Popen(['python', 'dota2.py'])
            self.dota2_status = "Запущено"
            self.status_label_dota2_status.setText(f'Состояние: {self.dota2_status}')

        if self.toggle_auto_buy_checkbox.isChecked():
            self.dota3_process = subprocess.Popen(['python', 'dota3.py'])
            self.dota3_status = "Запущено"
            self.status_label_dota3_status.setText(f'Состояние: {self.dota3_status}')

    def stop_selected_scripts(self):
        if self.toggle_auto_search_checkbox.isChecked():
            if self.dota_process:
                self.dota_process.kill()
                self.dota_process = None
                self.dota_status = "Выключено"
                self.status_label_dota_status.setText(f'Состояние: {self.dota_status}')

        if self.toggle_auto_pick_checkbox.isChecked():
            if self.dota2_process:
                self.dota2_process.kill()
                self.dota2_process = None
                self.dota2_status = "Выключено"
                self.status_label_dota2_status.setText(f'Состояние: {self.dota2_status}')

        if self.toggle_auto_buy_checkbox.isChecked():
            if self.dota3_process:
                self.dota3_process.kill()
                self.dota3_process = None
                self.dota3_status = "Выключено"
                self.status_label_dota3_status.setText(f'Состояние: {self.dota3_status}')

    def hero_button_clicked(self, hero_name):
        if hero_name not in self.selected_heroes:
            self.selected_heroes.append(hero_name)
        else:
            self.selected_heroes.remove(hero_name)

        # Обновление визуального состояния кнопок героев
        for button in self.hero_buttons:
            if button.text() in self.selected_heroes:
                button.setStyleSheet("background-color: lightgreen;")
            else:
                button.setStyleSheet("")

        # Вывод списка выбранных героев в консоль (для отладки)
        print("Выбранные герои:", self.selected_heroes)

    def check_auto_search_completion(self):
        # Сюда можно добавить логику, которая будет выполняться при завершении автопоиска
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
