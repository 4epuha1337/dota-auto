import threading
import pyautogui
import cv2
import numpy as np
import os
import time

# Отключаем fail-safe
pyautogui.FAILSAFE = False

# Константы для путей и файлов
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_FOLDER = os.path.join(CURRENT_DIR, "icons")

class HeroesAutoPicker(threading.Thread):  # Наследуем от threading.Thread
    def __init__(self, selected_heroes, repeat_count, on_complete=None):
        super().__init__()  # Вызываем конструктор родительского класса

        self.selected_heroes = selected_heroes
        self.repeat_count = repeat_count
        self.on_complete = on_complete  # Колбэк для оповещения о завершении
        self._stop_event = threading.Event()  # Флаг для остановки потока

    def stop(self):
        self._stop_event.set()  # Устанавливаем флаг остановки

    def click_image_with_similarity(self, img_path, similarity_threshold, click_pos=(0, 0), click=True, timeout=7):
        start_time = time.time()
        while time.time() - start_time < timeout:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            hero_image = cv2.imread(img_path, cv2.IMREAD_COLOR)
            if hero_image is None:
                print(f"Не удалось загрузить изображение: {img_path}")
                return False
            
            result = cv2.matchTemplate(screenshot, hero_image, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= similarity_threshold:
                if click:
                    center_x = max_loc[0] + hero_image.shape[1] // 2
                    center_y = max_loc[1] + hero_image.shape[0] // 2
                    pyautogui.moveTo(center_x + click_pos[0], center_y + click_pos[1])
                    time.sleep(0.5)
                    pyautogui.click()
                    time.sleep(0.5)
                return True
            
            time.sleep(0.5)
        
        print(f"Изображение {img_path} не найдено в течение {timeout} секунд.")
        return False

    # Функция для поиска изображения gamett.png
    def find_gamett(self):
        while True:
            if self._stop_event.is_set():
                print("Остановка работы по запросу.")
                return False
            if self.click_image_with_similarity(os.path.join(ICONS_FOLDER, "gamett.png"), 0.8, timeout=0.5):
                print("Изображение с игрой найдено")
                return True
            print("Изображение gamett.png не найдено")
            time.sleep(0.5)

    # Функция для автоматического выбора героев
    def auto_pick_heroes(self):
        try:
            print(f"Запускаем скрипт с {self.repeat_count} циклами.")
            
            if not self.selected_heroes:
                print("Не найдены выбранные герои. Прекращаем выполнение.")
                return
            
            # Ищем изображение gamett.png перед началом выбора героев
            print("Ищем изображение gamett.png...")
            if not self.find_gamett():
                print("Изображение gamett.png не найдено. Прекращаем выполнение.")
                return
            
            # Интервал между попытками поиска
            search_interval = 0.5
            
            # Приоритетный герой на первой строке списка
            current_cycle = 1
            while current_cycle <= self.repeat_count:
                if self._stop_event.is_set():
                    print("Остановка работы по запросу.")
                    return False

                print(f"Цикл {current_cycle}/{self.repeat_count} начат.")
                for hero_info in self.selected_heroes:
                    hero_name = hero_info['name']
                    hero_path = hero_info['icon_path']

                    hero_img_path = os.path.join(CURRENT_DIR, hero_path)
                    
                    # Если первый герой - aallrandom, выбираем его сразу
                    if hero_name == 'aallrandom':
                        if self.click_image_with_similarity(hero_img_path, 0.8, timeout=7):
                            print(f"Герой {hero_name} выбран.")
                            time.sleep(0.5)
                            self.click_image_with_similarity(os.path.join(ICONS_FOLDER, "pick.png"), 0.7, click_pos=(10, 0))
                            pyautogui.moveTo(0, 0)
                            print("Выбор героя завершен.")
                    else:
                        # Иначе, выбираем героя с учетом схожести и времени ожидания
                        if self.click_image_with_similarity(hero_img_path, 0.5, timeout=7):
                            print(f"Герой {hero_name} выбран.")
                            time.sleep(0.5)
                            self.click_image_with_similarity(os.path.join(ICONS_FOLDER, "pick.png"), 0.7, click_pos=(10, 0))
                            pyautogui.moveTo(0, 0)
                            print("Выбор героя завершен.")
                        else:
                            print(f"Не удалось выбрать героя {hero_name}. Пробуем следующего.")
                    
                    time.sleep(search_interval)
                
                print(f"Цикл {current_cycle}/{self.repeat_count} завершен.")
                current_cycle += 1
                if current_cycle <= self.repeat_count:
                    print(f"Ожидаем 15 секунд перед началом следующего цикла.")
                    time.sleep(15)

        except Exception as e:
            print(f"Произошла ошибка в скрипте: {e}")

        finally:
            # Вызов колбэка при завершении выполнения
            if self.on_complete:
                self.on_complete()

    def run(self):
        self.auto_pick_heroes()

# Метод чтоб запустить скрипт отдельно для отладки
if __name__ == "__main__":
    repeat_count = 3  # Количество повторений

    selected_heroes_array = [
        {'name': 'abaddon', 'icon_path': '.\\icons\\heroes\\abaddon.png'},
        {'name': 'windranger', 'icon_path': '.\\icons\\heroes\\windranger.png'},
        {'name': 'ursa', 'icon_path': '.\\icons\\heroes\\ursa.png'}
    ]

    auto_picker = HeroesAutoPicker(selected_heroes_array, repeat_count)
    auto_picker.start()

    try:
        while auto_picker.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Получен сигнал прерывания, остановка скрипта...")
        auto_picker.stop()
        auto_picker.join()
    print("Скрипт завершен.")