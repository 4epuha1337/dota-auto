import cv2
import pyautogui
import numpy as np

GAMETT_THRESHOLD = 0.8

def image_exists(image_path, threshold=GAMETT_THRESHOLD):
    # Загружаем изображение gamett.png или knopka.png
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        return False
    
    # Получаем скриншот экрана
    screenshot = pyautogui.screenshot()
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Поиск изображения на скриншоте
    result = cv2.matchTemplate(screenshot_np, image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    
    # Устанавливаем порог совпадения
    if max_val >= threshold:
        print(f"Найдено изображение {image_path} с коэффициентом совпадения {max_val}")
        return True
    
    return False