import cv2
import numpy as np
import pyautogui
import time
import os

# Отключение функции безопасности PyAutoGUI
pyautogui.FAILSAFE = False

# Путь к папке с изображениями
ICON_DIR = "./icons/Items/"

# Порог для совпадений изображений
THRESHOLD = 0.8

# Функция для проверки наличия изображения на экране
def image_exists(image_name, threshold=THRESHOLD):
    image_path = os.path.join(ICON_DIR, image_name)
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"Не удалось загрузить изображение: {image_path}")
        return False, None, None
    
    screenshot = pyautogui.screenshot()
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    result = cv2.matchTemplate(screenshot_np, image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        print(f"Найдено изображение {image_name} с коэффициентом совпадения {max_val}")
        return True, max_loc, image.shape
    
    print(f"Изображение {image_name} не найдено...")
    return False, None, None

# Функция для клика по изображению на экране с задержкой перед нажатием правой кнопки мыши
def click_image(location, image_shape):
    image_center = (
        int(location[0] + image_shape[1] / 2),
        int(location[1] + image_shape[0] / 2)
    )
    x, y = image_center
    
    # Наведение мыши на центр изображения с задержкой 0.2 секунды
    pyautogui.moveTo(x, y)
    time.sleep(0.2)  # Задержка 0.2 секунды, чтобы "залочить" мышь на изображении
    
    # Клик правой кнопкой мыши
    pyautogui.click(button='right')
    time.sleep(0.2)  # Задержка 0.2 секунды после клика
    
    # Возврат мыши в точку (0, 0)
    pyautogui.moveTo(0, 0)

def main():
    # Ожидание появления файла repeat-dota3.txt
    while not os.path.exists("repeat_dota3.txt"):
        time.sleep(3)
    
    # Чтение количества циклов из файла
    with open("repeat_dota3.txt", "r") as file:
        try:
            num_cycles = int(file.read().strip())
        except ValueError:
            print("Ошибка чтения файла repeat-dota3.txt")
            return
    
    print(f"Будет выполнено {num_cycles} циклов")
    
    # Выполнение циклов
    for cycle in range(1, num_cycles + 1):
        print(f"Цикл {cycle}/{num_cycles} начат")
        
        # Проверка на наличие boots.png
        found_boots = False
        while not found_boots:
            found_boots, location_boots, shape_boots = image_exists('boots.png')
            if found_boots:
                click_image(location_boots, shape_boots)
                print(f"Нажатие на boots.png и перемещение курсора в точку (0, 0)")
            else:
                print("Поиск boots.png...")
                time.sleep(1)  # Проверка раз в 3 секунды
        
        # Проверка на наличие tango.png
        found_tango = False
        while not found_tango:
            found_tango, location_tango, shape_tango = image_exists('tango.png')
            if found_tango:
                click_image(location_tango, shape_tango)
                print(f"Нажатие на tango.png и перемещение курсора в точку (0, 0)")
            else:
                print("Поиск tango.png...")
                time.sleep(3)  # Проверка раз в 3 секунды
        
        print(f"Цикл {cycle}/{num_cycles} завершен")
        
        if cycle < num_cycles:
            print(f"Пауза перед следующим циклом ({cycle+1}/{num_cycles})...")
            time.sleep(15)  # Пауза 15 секунд между циклами
    
    # Создание файла-сигнала о завершении скрипта
    with open("autobuy.txt", "w") as signal_file:
        signal_file.write("Автозакуп завершен.")

if __name__ == "__main__":
    main()
