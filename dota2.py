import pyautogui
import cv2
import numpy as np
import os
import time

# Отключаем fail-safe
pyautogui.FAILSAFE = False

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
        if time.time() - start_time > 0.1:
            print(f"Изображение {img_path} не найдено")
            return False
        
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        hero_image = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if hero_image is None:
            print(f"Не удалось загрузить изображение: {img_path}")
            return False
        
        result = cv2.matchTemplate(screenshot, hero_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= similarity_threshold:
            if click:
                # Находим координаты центра изображения
                center_x = max_loc[0] + hero_image.shape[1] // 2
                center_y = max_loc[1] + hero_image.shape[0] // 2
                # Наводим курсор на центр изображения + смещение на 5 пикселей вправо
                pyautogui.moveTo(center_x + 5, center_y)
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(0.5)
            return True
        else:
            time.sleep(1)

# Функция для поиска изображения gamett.png с заданным интервалом времени
def find_gamett():
    while True:
        if click_image_with_similarity(os.path.join(ICONS_FOLDER, "gamett.png"), 0.8):
            print("Изображение с игрой найдено")
            return True
        print("Изображение gamett.png не найдено")
        time.sleep(0.5)

def auto_pick_heroes():
    try:
        # Ищем изображение gamett.png перед началом выбора героев
        print("Ищем изображение gamett.png...")
        if not find_gamett():
            print("Изображение gamett.png не найдено. Прекращаем выполнение.")
            return
        
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
            
            # Поиск изображения gamett.png перед каждым выбором героя
            if not find_gamett():
                print("Изображение gamett.png не найдено. Прекращаем выполнение.")
                return
            
            time.sleep(0.5)  # Пауза перед началом поиска героев
            
            # Попытка выбрать случайного героя из списка с учетом приоритетности
            hero_found = False
            for hero_entry in selected_heroes:
                hero_name, hero_path = hero_entry.split(', ')
                hero_img_path = os.path.join(CURRENT_DIR, hero_path)
                
                if click_image_with_similarity(hero_img_path, 0.4):
                    print(f"Герой {hero_name} выбран.")
                    time.sleep(0.5)  # Пауза перед нажатием pick.png
                    if click_image_with_similarity(os.path.join(ICONS_FOLDER, "pick.png"), 0.7, click_pos=(5, 0)):
                        print("Найдено изображение pick.png. Выбираем его.")
                        pyautogui.moveTo(0, 0)
                        hero_found = True
                        break
                    else:
                        print("Изображение pick.png не найдено.")
            
            if not hero_found:
                print("Не удалось найти ни одного героя из списка.")
                continue
            
            print(f"Цикл {i}/{repeat_count} завершен.")
            time.sleep(5)
        
        # Создание файла autopick.txt после завершения всех циклов
        with open(AUTO_PICK_FILE, "w") as file:
            pass
        print(f"Файл {AUTO_PICK_FILE} успешно создан.")
    
    except Exception as e:
        print(f"Произошла ошибка в скрипте: {e}")

if __name__ == "__main__":
    auto_pick_heroes()

