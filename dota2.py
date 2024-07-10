import pyautogui
import cv2
import numpy as np
import os
import time
import random

# Константы для путей и файлов
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SELECTED_HEROES_FILE = os.path.join(CURRENT_DIR, "selected_heroes.txt")
ICONS_FOLDER = os.path.join(CURRENT_DIR, "icons")
HEROES_ICONS_FOLDER = os.path.join(ICONS_FOLDER, "heroes")
AUTO_PICK_FILE = os.path.join(CURRENT_DIR, "autopick.txt")
REPEAT_COUNT_FILE = os.path.join(CURRENT_DIR, "repeat_dota2.txt")

# Функция для чтения выбранных героев из файла
def read_selected_heroes():
    try:
        with open(SELECTED_HEROES_FILE, "r") as file:
            selected_heroes = [line.strip() for line in file.readlines() if line.strip()]
        return selected_heroes
    except FileNotFoundError:
        print(f"Файл {SELECTED_HEROES_FILE} не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла {SELECTED_HEROES_FILE}: {e}")
        return []

# Функция для выполнения клика по изображению с определенной схожестью
def click_image_with_similarity(img_path, similarity_threshold, click_pos=(0, 0), click=True):
    start_time = time.time()
    while True:
        if time.time() - start_time > 7:
            print(f"Изображение {img_path} не найдено в течение 7 секунд. Выбираем другой герой.")
            return False
        
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        hero_image = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if hero_image is None:
            print(f"Не удалось загрузить изображение героя: {img_path}")
            return False
        
        result = cv2.matchTemplate(screenshot, hero_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= similarity_threshold:
            if click:
                pyautogui.click(click_pos)
                time.sleep(0.5)
            return True
        else:
            time.sleep(0.5)

# Функция для выполнения автопика героев
def auto_pick_heroes():
    try:
        # Читаем количество циклов из файла
        try:
            with open(REPEAT_COUNT_FILE, "r") as file:
                repeat_count = int(file.read().strip())
        except FileNotFoundError:
            print(f"Файл {REPEAT_COUNT_FILE} не найден.")
            return
        except ValueError:
            print(f"Некорректное значение в файле {REPEAT_COUNT_FILE}.")
            return
        
        # Читаем выбранных героев из файла
        selected_heroes = read_selected_heroes()
        if not selected_heroes:
            print("Не найдены выбранные герои. Прекращаем выполнение.")
            return
        
        for i in range(1, repeat_count + 1):
            print(f"Цикл {i}/{repeat_count} начался.")
            
            # Поиск изображения gamett.png
            while not click_image_with_similarity(os.path.join(ICONS_FOLDER, "gamett.png"), 0.8):
                continue
            
            # Выбор случайного героя из selected_heroes (по порядку сверху вниз)
            for hero in selected_heroes:
                hero_img_path = os.path.join(HEROES_ICONS_FOLDER, f"{hero}.png")
                start_time_hero = time.time()
                
                while time.time() - start_time_hero < 7:
                    if click_image_with_similarity(hero_img_path, 0.6):
                        pyautogui.moveTo(0, 0)
                        break
                    else:
                        continue
                else:
                    print(f"Персонаж {hero} не был найден в течение 7 секунд.")
                    continue
                
                break  # Выход из цикла выбора героя, если успешно выбран
                
            else:
                print("Выбор случайного героя не удался. Продолжаем снова искать gamett.png.")
                continue
            
            # Поиск изображения pick.png или aallrandom.png и клик по нему
            if hero == "aallrandom":
                if not click_image_with_similarity(os.path.join(ICONS_FOLDER, "aallrandom.png"), 0.7):
                    continue
            else:
                if not click_image_with_similarity(os.path.join(ICONS_FOLDER, "pick.png"), 0.7):
                    continue
            
            pyautogui.moveTo(0, 0)
            print(f"Цикл {i}/{repeat_count} завершен.")
            time.sleep(15)
        
        # Создание файла autopick.txt после завершения всех циклов
        with open(AUTO_PICK_FILE, "w") as file:
            file.write("autopick.txt created successfully")
        print(f"Файл {AUTO_PICK_FILE} успешно создан.")
    
    except Exception as e:
        print(f"Произошла ошибка в скрипте: {e}")

if __name__ == "__main__":
    auto_pick_heroes()
