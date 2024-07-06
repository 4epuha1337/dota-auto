import pyautogui
import cv2
import numpy as np
import time
import os

# Путь к папке с изображениями
ICON_DIR = "./icons/"

# Файл для передачи количества повторений
REPEAT_COUNT_FILE = "repeat_count.txt"

def acceptGame():
    try:
        with open(REPEAT_COUNT_FILE, "r") as file:
            repeat_count = int(file.read().strip())
    except FileNotFoundError:
        print(f"Файл {REPEAT_COUNT_FILE} не найден. Завершение программы.")
        return
    except ValueError:
        print("Некорректное значение в файле repeat_count.txt. Завершение программы.")
        return
    
    for i in range(repeat_count):
        print(f"Цикл {i + 1}/{repeat_count}")

        # Поиск кнопки random.png
        while True:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Загружаем изображение кнопки random.png
            randomImagePath = os.path.join(ICON_DIR, 'random.png')
            randomImage = cv2.imread(randomImagePath, cv2.IMREAD_COLOR)
            
            if randomImage is None:
                print(f"Не удалось загрузить изображение: {randomImagePath}")
                break
            
            # Сравниваем скриншот с изображением кнопки random.png
            result = cv2.matchTemplate(screenshot, randomImage, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            # Если совпадение найдено с коэффициентом схожести выше 0.8
            if max_val > 0.8:
                randomButtonCenter = (
                    int(max_loc[0] + randomImage.shape[1] / 2),
                    int(max_loc[1] + randomImage.shape[0] / 2)
                )

                x, y = randomButtonCenter

                print("Изображение random.png найдено, нажимаем...")
                pyautogui.click(x, y)
                break
            else:
                # Если совпадение не найдено, ждем 1 секунду и повторяем
                print("Изображение random.png не найдено. Ждем 1 секунду и повторяем...")
                time.sleep(1)
        
        print(f"Цикл {i + 1}/{repeat_count} завершен.")

        # После каждого цикла, кроме последнего, ждем 15 секунд
        if i < repeat_count - 1:
            print("Ожидание перед следующим циклом...")
            time.sleep(15)

    print("Скрипт завершен.")

if __name__ == "__main__":
    acceptGame()
