import pictures as pic
import pyautogui
import cv2
import numpy as np
import time

RandomPick = "./icons/random.png"


def randomHero():
    while not pic.image_exists(RandomPick):
        pass
    randomButton = None
    while randomButton == None:
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # Загружаем изображение кнопки принятия
        randomImage = cv2.imread(RandomPick, cv2.IMREAD_COLOR)
        # Сравниваем скриншот с изображением кнопки
        result = cv2.matchTemplate(screenshot, randomImage, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        # Если совпадение найдено, нажимаем на кнопку
        if max_val > 0.8:
            randomButtonCenter = (
                int(max_loc[0] + randomImage.shape[1] / 2),
                int(max_loc[1] + randomImage.shape[0] / 2)
            )

            x, y = randomButtonCenter

            print("Кнопка рандома найдена, нажимаем...")
            pyautogui.click(x, y)
            return
        else:
            # Если совпадение не найдено, ждем 0.5 секунды и повторяем
            print("Кнопка рандома не найдена. Ждем 0.5 секунды и повторяем...")
            time.sleep(0.5)


randomHero()