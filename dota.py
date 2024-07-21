import threading
import cv2
import numpy as np
import pyautogui
import time
import pygetwindow as gw
import sys
import os

# Путь к папке с изображениями
ICON_DIR = "./icons/"

# Пороги для совпадений изображений
GAMETT_THRESHOLD = 0.8
KNOPKA_THRESHOLD = 0.8

# Глобальные переменные для работы цикла
delay_between_cycles = 15  # По умолчанию 15 секунд

class AutoSearch(threading.Thread):  # Наследуем от threading.Thread
    def __init__(self, repeat_count = 1, on_complete=None):
        super().__init__()  # Вызываем конструктор родительского класса

        self.repeat_count = repeat_count
        self.on_complete = on_complete  # Колбэк для оповещения о завершении
        self._stop_event = threading.Event()  # Флаг для остановки потока

    def stop(self):
        self._stop_event.set()  # Устанавливаем флаг остановки

    # Функция для проверки, активно ли окно Dota 2 и не свернуто ли оно
    def is_window_minimized(self, window):
        return window.isMinimized

    # Функция для активации окна Dota 2
    def activate_dota2_window(self):
        dota2_window_list = gw.getWindowsWithTitle("Dota 2")
        if dota2_window_list:
            dota2_window_list[0].activate()
            return True
        else:
            return False

    # Функция для выполнения действий в Dota 2
    def perform_dota2_actions(self):
        
        dota2_window_list = gw.getWindowsWithTitle("Dota 2")
        if dota2_window_list:
            if not self.is_window_minimized(dota2_window_list[0]):
                for current_cycle in range(1, self.repeat_count + 1):
                    print(f"Цикл {current_cycle}/{self.repeat_count} начат")
                    
                    # Ожидание появления изображения game.png
                    while not self.image_exists('game.png', GAMETT_THRESHOLD):
                        if self._stop_event.is_set():
                            print("Остановка работы скрипта dota.py по запросу.")
                            return False
                        
                        print("Изображение game.png не найдено. Ожидание...")
                        time.sleep(1)
                    
                    print("Изображение game.png найдено. Продолжаем выполнение...")
                    
                    # Нажатие на изображение game.png
                    self.click_image('game.png', GAMETT_THRESHOLD)
                    time.sleep(1)
                    
                    # Нажатие на кнопку "Найти игру" по координатам (1750, 1025)
                    pyautogui.click(1750, 1025)
                    time.sleep(1)
                    
                    # Проверка наличия изображения gamett.png
                    while not self.image_exists('gamett.png', GAMETT_THRESHOLD):
                        if self._stop_event.is_set():
                            print("Остановка работы скрипта dota.py по запросу.")
                            return False
                        # Если gamett.png не найдено, ищем knopka.png и принимаем игру
                        if self.image_exists('knopka.png', KNOPKA_THRESHOLD):
                            print("Кнопка принятия найдена. Принимаем игру...")
                            self.accept_game()
                            time.sleep(1)  # Небольшая задержка после принятия игры
                        else:
                            print("Кнопка принятия не найдена. Ждем 1 секунду и повторяем...")
                            time.sleep(1)
                    
                    print(f"Цикл {current_cycle}/{self.repeat_count} завершен.")
                    
                    if current_cycle < self.repeat_count:
                        print(f"Ожидание {delay_between_cycles} секунд до следующего цикла...")
                        time.sleep(delay_between_cycles)
            
            else:
                print("Окно Dota 2 не активно или свернуто.")
        else:
            print("Окно Dota 2 не найдено.")

    # Функция для проверки наличия изображения на экране
    def image_exists(self, image_name, threshold):
        image_path = os.path.join(ICON_DIR, image_name)
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            print(f"Не удалось загрузить изображение: {image_path}")
            return False
        
        screenshot = pyautogui.screenshot()
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        result = cv2.matchTemplate(screenshot_np, image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            print(f"Найдено изображение {image_name} с коэффициентом совпадения {max_val}")
            return True
        
        return False

    # Функция для клика по изображению на экране
    def click_image(self, image_name, threshold):
        image_path = os.path.join(ICON_DIR, image_name)
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            print(f"Не удалось загрузить изображение: {image_path}")
            return False
        
        screenshot = pyautogui.screenshot()
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        result = cv2.matchTemplate(screenshot_np, image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            image_center = (
                int(max_loc[0] + image.shape[1] / 2),
                int(max_loc[1] + image.shape[0] / 2)
            )
            x, y = image_center

            pyautogui.click(x, y)
            return True
        
        return False

    # Функция для принятия игры
    def accept_game(self):
        accept_button_location = None
        while accept_button_location is None:
            if self._stop_event.is_set():
                print("Остановка работы скрипта dota.py по запросу.")
                return False
            
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            accept_button_image_path = os.path.join(ICON_DIR, 'knopka.png')
            accept_button_image = cv2.imread(accept_button_image_path, cv2.IMREAD_COLOR)
            
            if accept_button_image is None:
                print(f"Не удалось загрузить изображение: {accept_button_image_path}")
                break
            
            result = cv2.matchTemplate(screenshot, accept_button_image, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= KNOPKA_THRESHOLD:
                accept_button_center = (
                    int(max_loc[0] + accept_button_image.shape[1] / 2),
                    int(max_loc[1] + accept_button_image.shape[0] / 2)
                )
                x, y = accept_button_center

                print("Кнопка принятия найдена! Принимаем игру...")
                pyautogui.click(x, y)
            else:
                print("Кнопка принятия не найдена. Ждем 1 секунду и повторяем...")
                time.sleep(1)

    # Основная функция для запуска скрипта
    def main(self):

        if self.activate_dota2_window():
            self.perform_dota2_actions()
        else:
            print("Не удалось активировать окно Dota 2.")

        print("Скрипт завершен.")

    def run(self):
        self.main()

# Метод чтоб запустить скрипт отдельно для отладки
if __name__ == "__main__":
    repeat_count = 3  # Количество повторений


    auto_search = AutoSearch(repeat_count=3)
    auto_search.start()

    try:
        while auto_search.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Получен сигнал прерывания, остановка скрипта...")
        auto_search.stop()
        auto_search.join()
    print("Скрипт завершен.")
