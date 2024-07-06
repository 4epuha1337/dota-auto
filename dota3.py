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
        return False
    
    screenshot = pyautogui.screenshot()
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    result = cv2.matchTemplate(screenshot_np, image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        print(f"Найдено изображение {image_name} с коэффициентом совпадения {max_val}")
        return True, max_loc, image.shape
    
    return False, None, None

# Функция для клика по изображению на экране с задержкой перед нажатием правой кнопки мыши
def click_image(location, image_shape):
    image_center = (
        int(location[0] + image_shape[1] / 2),
        int(location[1] + image_shape[0] / 2)
    )
    x, y = image_center
    
    # Наведение мыши на центр изображения с задержкой 0.5 секунды
    pyautogui.moveTo(x, y)
    time.sleep(0.2)  # Задержка 0.5 секунды, чтобы "залочить" мышь на изображении
    
    # Клик правой кнопкой мыши
    pyautogui.click(button='right')
    time.sleep(0.2)  # Задержка 1 секунда после клика
    
    # Возврат мыши в точку (0, 0)
    pyautogui.moveTo(0, 0)

def main():
    while True:
        # Проверка на наличие boots.png
        found_boots, location_boots, shape_boots = image_exists('boots.png')
        if found_boots:
            click_image(location_boots, shape_boots)
            
            # Проверка на наличие tango.png
            found_tango, location_tango, shape_tango = image_exists('tango.png')
            if found_tango:
                click_image(location_tango, shape_tango)
                break
        
        time.sleep(0.3)  # Задержка между повторами проверки

    # Создание файла-сигнала о завершении скрипта
    with open("autozakup_complete.txt", "w") as signal_file:
        signal_file.write("Автозакуп завершен.")

if __name__ == "__main__":
    main()
