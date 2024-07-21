import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
import subprocess
import re
import dota2

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
        self.selected_items = []  # список выбранных предметов для Autobuy
        self.remaining_gold = 600  # начальное значение золота

        self.initUI()
        self.check_for_auto_files()  # Проверяем наличие файлов при запуске
        
                # Таймер для задержки между нажатиями
        self.click_timer = QtCore.QTimer()
        self.click_timer.setInterval(100)  # 0.25 секунды
        self.click_timer.setSingleShot(True)

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

        self.selected_items_scroll_area = QtWidgets.QScrollArea()
        self.selected_items_scroll_area.setWidgetResizable(True)
        self.selected_items_widget = QtWidgets.QWidget()
        self.selected_items_layout = QtWidgets.QGridLayout(self.selected_items_widget)
        self.selected_items_scroll_area.setWidget(self.selected_items_widget)
        layout.addWidget(self.selected_items_scroll_area)

        self.gold_status_label = QtWidgets.QLabel(f'Остаток золота: {self.remaining_gold} gold')
        layout.addWidget(self.gold_status_label)

        self.items_count_label = QtWidgets.QLabel('Выбрано предметов: (0)')
        layout.addWidget(self.items_count_label)

        self.items_status_label = QtWidgets.QLabel('Предметы: (не выбрано)')
        layout.addWidget(self.items_status_label)

        self.populate_item_icons()  # Call to method for item icons

        tab.setLayout(layout)
        return tab

    def populate_hero_icons(self):
        hero_icons_folder = 'icons/pretty heroes'
        hero_icon_size = 50
        col_count = 8
        row = 0
        col = 0

        for filename in os.listdir(hero_icons_folder):
            if filename.endswith('.png'):
                hero_name = filename.replace('.png', '')
                hero_icon_path = os.path.join(hero_icons_folder, filename)
                hero_icon = QtGui.QPixmap(hero_icon_path).scaled(hero_icon_size, hero_icon_size)

                hero_button = QtWidgets.QPushButton()
                hero_button.setIcon(QtGui.QIcon(hero_icon))
                hero_button.setIconSize(QtCore.QSize(hero_icon_size, hero_icon_size))
                hero_button.setToolTip(hero_name)
                hero_button.setCheckable(True)
                hero_button.clicked.connect(self.select_hero)
                self.selected_heroes_layout.addWidget(hero_button, row, col)

                col += 1
                if col >= col_count:
                    col = 0
                    row += 1

        self.update_selected_heroes_status()

    def populate_item_icons(self):
        item_icons_folder = 'icons/items'
        item_icon_size = 50
        col_count = 8
        row = 0
        col = 0

        for filename in os.listdir(item_icons_folder):
            if filename.endswith('.png'):
                item_name = filename.replace('.png', '')
                item_icon_path = os.path.join(item_icons_folder, filename)
                item_icon = QtGui.QPixmap(item_icon_path).scaled(item_icon_size, item_icon_size)

                item_button = QtWidgets.QPushButton()
                item_button.setIcon(QtGui.QIcon(item_icon))
                item_button.setIconSize(QtCore.QSize(item_icon_size, item_icon_size))
                item_button.setToolTip(item_name)
                item_button.setCheckable(True)
                item_button.clicked.connect(self.select_item)
                item_button.setStyleSheet("")  # Инициализируем без рамки
                self.selected_items_layout.addWidget(item_button, row, col)

                # Получаем стоимость предмета из названия файла (если есть число)
                item_cost = self.get_item_cost(item_name)
                if item_cost is not None:
                    item_button.setProperty('cost', item_cost)

                col += 1
                if col >= col_count:
                    col = 0
                    row += 1

        self.update_selected_items_status()


    def get_item_cost(self, item_name):
        # Ищем число в названии предмета (первое число, если таковое есть)
        import re
        match = re.search(r'\d+', item_name)
        if match:
            return int(match.group())
        return None

    def update_dota_cycles(self, value):
        self.dota_cycles = value
        self.cycle_labels['Autosearch'].setText(f'Количество циклов: {self.dota_cycles}')

    def update_dota2_cycles(self, value):
        self.dota2_cycles = value
        self.cycle_labels['Autopick'].setText(f'Количество циклов: {self.dota2_cycles}')

    def update_dota3_cycles(self, value):
        self.dota3_cycles = value
        self.cycle_labels['Autobuy'].setText(f'Количество циклов: {self.dota3_cycles}')

    def update_autosearch_checkbox(self, state):
        if state == QtCore.Qt.Checked:
            self.dota_status = "Включено"
            self.toggle_auto_search_checkbox.setText("Включено")
        else:
            self.dota_status = "Выключено"
            self.toggle_auto_search_checkbox.setText("Выключено")
        self.status_labels['Autosearch'].setText(f'Состояние: {self.dota_status}')

    def update_autopick_checkbox(self, state):
        if state == QtCore.Qt.Checked:
            self.dota2_status = "Включено"
            self.toggle_auto_pick_checkbox.setText("Включено")
        else:
            self.dota2_status = "Выключено"
            self.toggle_auto_pick_checkbox.setText("Выключено")
        self.status_labels['Autopick'].setText(f'Состояние: {self.dota2_status}')

    def update_autobuy_checkbox(self, state):
        if state == QtCore.Qt.Checked:
            self.dota3_status = "Включено"
            self.toggle_auto_buy_checkbox.setText("Включено")
        else:
            self.dota3_status = "Выключено"
            self.toggle_auto_buy_checkbox.setText("Выключено")
        self.status_labels['Autobuy'].setText(f'Состояние: {self.dota3_status}')


    def start_all_scripts(self):
        if self.dota_status == "Включено" and self.dota_process is None:
            self.start_dota_script()
        if self.dota2_status == "Включено" and self.dota2_process is None:
            self.start_dota2_script()
        if self.dota3_status == "Включено" and self.dota3_process is None:
            self.start_dota3_script()

    def stop_all_scripts(self):
        if self.dota_process is not None:
            self.stop_dota_script()
        if self.dota2_process is not None:
            self.stop_dota2_script()
        if self.dota3_process is not None:
            self.stop_dota3_script()

    def start_selected_scripts(self):
        if self.dota_status == "Включено" and self.dota_process is None:
            self.start_dota_script()
        if self.dota2_status == "Включено" and self.dota2_process is None:
            self.start_dota2_script()
        if self.dota3_status == "Включено" and self.dota3_process is None:
            self.start_dota3_script()

    def stop_selected_scripts(self):
        if self.dota_process is not None:
            self.stop_dota_script()
        if self.dota2_process is not None:
            self.stop_dota2_script()
        if self.dota3_process is not None:
            self.stop_dota3_script()

    def close_application(self):
        self.close()

    def start_dota_script(self):
        self.dota_process = subprocess.Popen(['python', 'dota.py'])
        self.dota_status = "Запущено"
        self.status_labels['Autosearch'].setText(f'Состояние: {self.dota_status}')

        # Создаем файл repeat_dota.txt с текущим количеством циклов
        with open('repeat_dota.txt', 'w') as f:
            f.write(str(self.dota_cycles))

    def stop_dota_script(self):
        if self.dota_process is not None:
            self.dota_process.terminate()
            self.dota_process = None
            self.dota_status = "Остановлено"
            self.status_labels['Autosearch'].setText(f'Состояние: {self.dota_status}')
        
            # Удаляем файл repeat_dota.txt при остановке
            if os.path.exists('repeat_dota.txt'):
                os.remove('repeat_dota.txt')

    def start_dota2_script(self):
        # Создаем пустой массив для хранения объектов
        selected_heroes_array = []

        # Итерируем по выбранным героям и добавляем их в массив в нужном формате
        for hero in self.selected_heroes:
            hero_object = {
                'name': hero,
                'icon_path': f'.\\icons\\heroes\\{hero}.png'
            }
            selected_heroes_array.append(hero_object)

        # Создаем и запускаем поток
        self.dota2_process = dota2.HeroesAutoPicker(selected_heroes=selected_heroes_array, repeat_count=self.dota2_cycles, on_complete=self.on_autopick_complete)
        self.dota2_process.start()
        self.dota2_status = "Запущено"
        self.status_labels['Autopick'].setText(f'Состояние: {self.dota2_status}')

    # Метод, который вызывается после выхода из AutoPick
    def on_autopick_complete(self):
        self.toggle_auto_pick_checkbox.setChecked(False)
        self.toggle_auto_pick_checkbox.setText("Выключено")
        self.status_labels['Autopick'].setText(f'Состояние: Выключено')
        
        print("Скрипт Dota 2 остановлен.")

    def stop_dota2_script(self):
        if self.dota2_process is not None:
            self.dota2_process.stop()
            self.dota2_process.join()
            self.dota2_process = None
            self.dota2_status = "Остановлено"
            self.status_labels['Autopick'].setText(f'Состояние: {self.dota2_status}')


    def start_dota3_script(self):
        self.dota3_process = subprocess.Popen(['python', 'dota3.py'])
        self.dota3_status = "Запущено"
        self.status_labels['Autobuy'].setText(f'Состояние: {self.dota3_status}')

        # Создаем файл repeat_dota3.txt с текущим количеством циклов
        with open('repeat_dota3.txt', 'w') as f:
            f.write(str(self.dota3_cycles))

        # Создаем файл selected_items.txt с выбранными предметами
        with open('selected_items.txt', 'w') as f:
            for item in self.selected_items:
                f.write(f'{item}.png , .\\icons\\Items\\{item}.png\n')



    def stop_dota3_script(self):
        if self.dota3_process is not None:
            self.dota3_process.terminate()
            self.dota3_process = None
            self.dota3_status = "Остановлено"
            self.status_labels['Autobuy'].setText(f'Состояние: {self.dota3_status}')
        
            # Удаляем файлы repeat_dota3.txt и selected_items.txt при остановке
            if os.path.exists('repeat_dota3.txt'):
                os.remove('repeat_dota3.txt')
            if os.path.exists('selected_items.txt'):
                os.remove('selected_items.txt')


    def check_for_auto_files(self):
        for key, filename in self.signal_files.items():
            if os.path.exists(filename):
                # Удаляем файл сигнала
                os.remove(filename)
            
                # Останавливаем соответствующий скрипт и обновляем интерфейс
                if key == 'autosearch' and self.dota_process is not None:
                    self.stop_dota_script()
                    self.toggle_auto_search_checkbox.setChecked(False)
                    self.toggle_auto_search_checkbox.setText("Выключено")
                    self.status_labels['Autosearch'].setText(f'Состояние: Выключено')
                    if os.path.exists('repeat_dota.txt'):
                        os.remove('repeat_dota.txt')
                        print("Файл repeat_dota.txt удален")
                    print("Сигнальный файл autosearch.txt обнаружен. Скрипт Dota остановлен, все файлы удалены.")
                
                elif key == 'autobuy' and self.dota3_process is not None:
                    self.stop_dota3_script()
                    self.toggle_auto_buy_checkbox.setChecked(False)
                    self.toggle_auto_buy_checkbox.setText("Выключено")
                    self.status_labels['Autobuy'].setText(f'Состояние: Выключено')
                    if os.path.exists('repeat_dota3.txt'):
                        os.remove('repeat_dota3.txt')
                        print("Файл repeat_dota3.txt удален")
                    if os.path.exists('selected_items.txt'):
                        os.remove('selected_items.txt')
                        print("Файл selected_items.txt удален")
                    print("Сигнальный файл autobuy.txt обнаружен. Скрипт Dota 3 остановлен, все файлы удалены.")



    def select_hero(self):
        sender = self.sender()
        hero_name = sender.toolTip()

        if sender.isChecked():
            self.selected_heroes.append(hero_name)
        else:
            self.selected_heroes.remove(hero_name)

        self.update_selected_heroes_status()

    def update_selected_heroes_status(self):
        selected_heroes_text = ', '.join(self.selected_heroes) if self.selected_heroes else '(не выбрано)'
        self.heroes_status_label.setText(f'Название героев: {selected_heroes_text}')
        self.heroes_count_label.setText(f'Количество героев: ({len(self.selected_heroes)})')

    def select_item(self, item_button):
        
        if not isinstance(item_button, QtWidgets.QPushButton):
            return  # Защита от вызова с неправильным типом аргумента

        
        
        item_name = item_button.toolTip()
        item_cost = item_button.property('cost')
    
        initial_remaining_gold = self.remaining_gold  # Сохраняем исходное количество золота
        initial_selected_items = list(self.selected_items)  # Сохраняем исходные выбранные предметы
    
        if QtWidgets.QApplication.mouseButtons() == QtCore.Qt.LeftButton:
            # Левая кнопка мыши: добавляем предмет
            if item_name in self.selected_items:
                item_count = self.selected_items.count(item_name)
                if item_count < 9:
                    if self.remaining_gold >= item_cost:
                        self.selected_items.append(item_name)
                        self.remaining_gold -= item_cost
                        self.update_item_button_color(item_button, item_count + 1)
                    else:
                        QtWidgets.QMessageBox.warning(self, 'Недостаточно золота', 'У вас недостаточно золота для покупки этого предмета.')
                        self.reset_to_initial_state(item_button, initial_remaining_gold, initial_selected_items)
                else:
                    QtWidgets.QMessageBox.warning(self, 'Максимальное количество предметов', 'Вы уже выбрали максимальное количество предметов (9).')
                    self.reset_to_initial_state(item_button, initial_remaining_gold, initial_selected_items)
            else:
                if item_cost is not None and self.remaining_gold >= item_cost:
                    self.selected_items.append(item_name)
                    self.remaining_gold -= item_cost
                    self.update_item_button_color(item_button, 1)
                else:
                    QtWidgets.QMessageBox.warning(self, 'Недостаточно золота', 'У вас недостаточно золота для покупки этого предмета.')
                    self.reset_to_initial_state(item_button, initial_remaining_gold, initial_selected_items)
    
        elif QtWidgets.QApplication.mouseButtons() == QtCore.Qt.RightButton:
            # Правая кнопка мыши: уменьшаем предмет
            if item_name in self.selected_items:
                self.selected_items.remove(item_name)
                self.remaining_gold += item_cost  # Возвращаем золото
                self.update_item_button_color(item_button, self.selected_items.count(item_name))
            else:
                # Если предмета нет, просто игнорируем
                return
    
        self.update_selected_items_status()
        self.update_gold_status()  # Обновляем статус золота




    def update_item_button_color(self, button, count):
        color_map = {
            1: "green",
            2: "blue",
            3: "red",
            4: "yellow",
            5: "purple",
            6: "black",
            7: "brown",
            8: "cyan",
            9: "orange"
        }
        if count == 0:
            button.setStyleSheet("")  # Сброс цвета
        else:
            color = color_map.get(count, "")
            button.setStyleSheet(f"border: 2px solid {color};")

    def populate_item_icons(self):
        item_icons_folder = 'icons/items'
        item_icon_size = 50
        col_count = 8
        row = 0
        col = 0

        for filename in os.listdir(item_icons_folder):
            if filename.endswith('.png'):
                item_name = filename.replace('.png', '')
                item_icon_path = os.path.join(item_icons_folder, filename)
                item_icon = QtGui.QPixmap(item_icon_path).scaled(item_icon_size, item_icon_size)

                item_button = QtWidgets.QPushButton()
                item_button.setIcon(QtGui.QIcon(item_icon))
                item_button.setIconSize(QtCore.QSize(item_icon_size, item_icon_size))
                item_button.setToolTip(item_name)
                item_button.setCheckable(True)
                item_button.setStyleSheet("")  # Инициализируем без рамки
                item_button.clicked.connect(lambda _, b=item_button: self.select_item(b))
                item_button.installEventFilter(self)  # Устанавливаем фильтр событий для кнопки

                self.selected_items_layout.addWidget(item_button, row, col)

                # Получаем стоимость предмета из названия файла (если есть число)
                item_cost = self.get_item_cost(item_name)
                if item_cost is not None:
                    item_button.setProperty('cost', item_cost)

                col += 1
                if col >= col_count:
                    col = 0
                    row += 1

        self.update_selected_items_status()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if isinstance(obj, QtWidgets.QPushButton) and obj.toolTip():
                if self.click_timer.isActive():
                    return True  # Если таймер активен, игнорируем событие
                else:
                    self.click_timer.start()
                    self.process_click(obj)
                    return True  # Возвращаем True, чтобы сообщить, что событие было обработано
    
        return super().eventFilter(obj, event)
    

    def update_gold_status(self):
        self.gold_status_label.setText(f'Остаток золота: {self.remaining_gold} gold')
        

    def reset_to_initial_state(self, sender, initial_remaining_gold, initial_selected_items):
        self.selected_items = initial_selected_items.copy()
        self.remaining_gold = initial_remaining_gold
        
        for button in self.selected_items_layout.findChildren(QtWidgets.QPushButton):
            if button.toolTip() == sender.toolTip():  # Сравниваем по всплывающей подсказке, предполагая, что подсказка уникальна
                button.setChecked(False)
                self.update_item_button_color(button, 0)
        
        self.update_selected_items_status()
        self.update_gold_status()

    def update_selected_items_status(self):
        # Убираем расширение .png и цифры из названий предметов
        cleaned_items = [item.split('.')[0] for item in self.selected_items]
        selected_items_text = ', '.join(cleaned_items) if cleaned_items else '(не выбрано)'
        self.items_status_label.setText(f'Предметы: {selected_items_text}')
        self.items_count_label.setText(f'Выбрано предметов: ({len(self.selected_items)})')
        self.gold_status_label.setText(f'Остаток золота: {self.remaining_gold} gold')

    def handle_right_click_item(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.select_item()
        else:
            super().mousePressEvent(event)
            
            
    def process_click(self, button):
        self.select_item(button)
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
