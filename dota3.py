import cv2
import numpy as np
import pyautogui
import time
import os

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
    else:
        print(f"Изображение {image_name} не найдено.")
    
    return False, None, None

# Функция для клика по изображению на экране
def click_image(location, image_shape):
    image_center = (
        int(location[0] + image_shape[1] / 2),
        int(location[1] + image_shape[0] / 2)
    )
    x, y = image_center
    pyautogui.click(x, y, button='right')

def main():
    while True:
        # Проверка на наличие boots.png
        found_boots, location_boots, shape_boots = image_exists('boots.png')
        if found_boots:
            time.sleep(1)  # Задержка перед кликом
            click_image(location_boots, shape_boots)
            time.sleep(1)  # Задержка перед следующим действием
            
            # Проверка на наличие tango.png
            found_tango, location_tango, shape_tango = image_exists('tango.png')
            if found_tango:
                time.sleep(1)  # Задержка перед кликом
                click_image(location_tango, shape_tango)
                break
        
        time.sleep(5)  # Задержка между повторами проверки

    # Создание файла-сигнала о завершении скрипта
    with open("autozakup_complete.txt", "w") as signal_file:
        signal_file.write("Автозакуп завершен.")

if __name__ == "__main__":
    main()
