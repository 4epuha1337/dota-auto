import cv2
import numpy as np
import pyautogui
import time
import os

# Отключение функции безопасности PyAutoGUI
pyautogui.FAILSAFE = False

# Порог для совпадений изображений
THRESHOLD = 0.7

# Путь к папке с изображениями предметов
ICON_DIR = ".\\icons\\Items"

def image_exists(image_path, threshold=THRESHOLD):
    # Загрузка изображения предмета
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"Не удалось загрузить изображение: {image_path}")
        return False, None, None
    
    # Скриншот текущего экрана
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Поиск изображения предмета на экране
    result = cv2.matchTemplate(screenshot_bgr, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        # Найдено изображение с заданным порогом совпадения
        return True, max_loc, image
    else:
        return False, None, None

def click_image(location, image):
    # Получение координат центра изображения
    center_x = location[0] + image.shape[1] // 2
    center_y = location[1] + image.shape[0] // 2
    
    # Наведение курсора на центр изображения и выполнение правого клика
    pyautogui.moveTo(center_x, center_y)
    time.sleep(0.3)  # Задержка перед кликом
    pyautogui.click(button='right')
    time.sleep(0.3)  # Задержка после клика
    pyautogui.moveTo(0, 0)  # Перемещение курсора в точку (0, 0)

def main():
    # Ожидание появления файла repeat_dota3.txt
    while not os.path.exists("repeat_dota3.txt"):
        time.sleep(3)
    
    # Чтение количества циклов из файла
    with open("repeat_dota3.txt", "r") as file:
        try:
            num_cycles = int(file.read().strip())
        except ValueError:
            print("Ошибка чтения файла repeat_dota3.txt")
            return
    
    print(f"Будет выполнено {num_cycles} циклов")
    
    # Чтение списка предметов и их путей из файла selected_items.txt
    items_list = []
    with open("selected_items.txt", "r") as items_file:
        for line in items_file:
            parts = line.strip().split(",")
            if len(parts) == 2:
                item_name = parts[0].strip()
                item_path = parts[1].strip()
                items_list.append((item_name, item_path))
    
    if not items_list:
        print("Список предметов пуст или не удалось прочитать из файла selected_items.txt")
        return
    
    print("Список предметов для закупки:")
    for item_name, _ in items_list:
        print(f"- {item_name}")
    
    # Выполнение циклов
    for cycle in range(1, num_cycles + 1):
        print(f"Цикл {cycle}/{num_cycles} начат")
        
        # Проход по списку предметов и их поиск на экране
        remaining_items = items_list[:]
        while remaining_items:
            for item_name, item_path in remaining_items[:]:
                found_item = False
                while not found_item:
                    found_item, location, image = image_exists(item_path)
                    if found_item:
                        click_image(location, image)
                        print(f"Нажатие на {item_name} и перемещение курсора в точку (0, 0)")
                        time.sleep(1)  # Задержка после нажатия
                        pyautogui.moveTo(0, 0)  # Перемещение курсора в точку (0, 0)
                        remaining_items.remove((item_name, item_path))
                    else:
                        print(f"Поиск {item_name}...")
                        time.sleep(0.5)  # Проверка раз в 1 секунду
        
        print(f"Цикл {cycle}/{num_cycles} завершен")
        
        if cycle < num_cycles:
            print(f"Пауза перед следующим циклом ({cycle+1}/{num_cycles})...")
            time.sleep(15)  # Пауза 15 секунд между циклами
    
    # Создание файла-сигнала о завершении скрипта
    with open("autobuy.txt", "w") as signal_file:
        signal_file.write("Автозакуп завершен.")

if __name__ == "__main__":
    main()
