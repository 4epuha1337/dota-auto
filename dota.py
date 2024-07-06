import cv2
import numpy as np
import pyautogui
import time
import pygetwindow as gw
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Путь к папке с изображениями
ICON_DIR = "./icons/"

# Пороги для совпадений изображений
GAMETT_THRESHOLD = 0.8
KNOPKA_THRESHOLD = 0.8

# Глобальные переменные для работы цикла
running = False
repeat_count = 1  # По умолчанию 1 цикл
delay_between_cycles = 15  # По умолчанию 15 секунд

# Функция для проверки, активно ли окно Dota 2 и не свернуто ли оно
def is_window_minimized(window):
    return window.isMinimized

# Функция для активации окна Dota 2
def activate_dota2_window():
    dota2_window_list = gw.getWindowsWithTitle("Dota 2")
    if dota2_window_list:
        dota2_window_list[0].activate()
        return True
    else:
        return False

# Функция для выполнения действий в Dota 2
def perform_dota2_actions():
    global running, repeat_count, delay_between_cycles
    
    dota2_window_list = gw.getWindowsWithTitle("Dota 2")
    if dota2_window_list:
        if not is_window_minimized(dota2_window_list[0]):
            running = True
            
            for current_cycle in range(1, repeat_count + 1):
                print(f"Идет выполнение цикла {current_cycle}/{repeat_count}")
                
                # Ожидание появления изображения game.png
                while not image_exists('game.png', threshold=GAMETT_THRESHOLD):
                    print("Изображение game.png не найдено. Ожидание...")
                    time.sleep(1)
                
                print("Изображение game.png найдено. Продолжаем выполнение...")
                
                # Нажатие на изображение game.png
                click_image('game.png', threshold=GAMETT_THRESHOLD)
                time.sleep(1)
                
                # Нажатие на кнопку "Найти игру" по координатам (1750, 1025)
                pyautogui.click(1750, 1025)
                time.sleep(1)
                
                while running:
                    # Проверка наличия gamett.png
                    if image_exists('gamett.png', threshold=GAMETT_THRESHOLD):
                        print("Игра началась.")
                        break
                    
                    # Если gamett.png не найдено, ищем knopka.png и принимаем игру
                    if image_exists('knopka.png', threshold=KNOPKA_THRESHOLD):
                        print("Кнопка принятия найдена. Принимаем игру...")
                        accept_game()
                
                    # Повторная проверка на gamett.png
                    time.sleep(0.5)
                
                print(f"Цикл {current_cycle}/{repeat_count} завершен.")
                
                if current_cycle < repeat_count:
                    print(f"Ожидание {delay_between_cycles} секунд до следующего цикла...")
                    time.sleep(delay_between_cycles)
            
            running = False
            print("Скрипт завершен.")
        else:
            print("Окно Dota 2 не активно или свернуто.")
    else:
        print("Окно Dota 2 не найдено.")

# Функция для проверки наличия изображения на экране
def image_exists(image_name, threshold=GAMETT_THRESHOLD):
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
        print(f"Найдено изображение с коэффициентом совпадения {max_val}")
        return True
    
    return False

# Функция для клика по изображению на экране
def click_image(image_name, threshold=GAMETT_THRESHOLD):
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

# Объединенная функция для принятия игры
def accept_game():
    accept_button_location = None
    while accept_button_location is None:
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

# Функция для запуска скрипта
def start_script():
    global running

    if activate_dota2_window():
        perform_dota2_actions()
    else:
        print("Не удалось активировать окно Dota 2.")

    print("Скрипт завершен.")

# Класс для обработки событий файловой системы
class Dota2FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Здесь можно добавить обработчик изменений файлов, если потребуется в будущем
        pass

# Основная функция для запуска скрипта
def main():
    global repeat_count, delay_between_cycles
    
    # Проверка аргументов командной строки
    if len(sys.argv) > 1:
        try:
            repeat_count = int(sys.argv[1])
            if len(sys.argv) > 2:
                delay_between_cycles = int(sys.argv[2])
        except ValueError:
            print("Ошибка: Некорректный ввод. Используются значения по умолчанию.")
    
    observer = Observer()
    event_handler = Dota2FileHandler()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        start_script()
    except ValueError:
        print("Некорректный ввод.")

    observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
