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
REPEAT_FILE = os.path.join(CURRENT_DIR, "repeat_dota2.txt")

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

# Функция для чтения количества циклов из файла repeat_dota2.txt
def read_repeat_count():
    try:
        with open(REPEAT_FILE, "r") as file:
            repeat_count = int(file.read().strip())
        return repeat_count
    except FileNotFoundError:
        print(f"Файл {REPEAT_FILE} не найден. Используется значение по умолчанию: 1 цикл.")
        return 1
    except ValueError:
        print(f"Ошибка при чтении файла {REPEAT_FILE}. Некорректные данные. Используется значение по умолчанию: 1 цикл.")
        return 1
    except Exception as e:
        print(f"Произошла ошибка при чтении файла {REPEAT_FILE}: {e}")
        return 1

# Функция для выполнения клика по изображению с определенной схожестью
def click_image_with_similarity(img_path, similarity_threshold, click_pos=(0, 0), click=True, timeout=7):
    start_time = time.time()
    while time.time() - start_time < timeout:
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
                center_x = max_loc[0] + hero_image.shape[1] // 2
                center_y = max_loc[1] + hero_image.shape[0] // 2
                pyautogui.moveTo(center_x + click_pos[0], center_y + click_pos[1])
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(0.5)
            return True
        
        time.sleep(0.5)
    
    print(f"Изображение {img_path} не найдено в течение {timeout} секунд.")
    return False

# Функция для поиска изображения gamett.png
def find_gamett():
    while True:
        if click_image_with_similarity(os.path.join(ICONS_FOLDER, "gamett.png"), 0.8, timeout=0.5):
            print("Изображение с игрой найдено")
            return True
        print("Изображение gamett.png не найдено")
        time.sleep(0.5)

# Функция для автоматического выбора героев
def auto_pick_heroes():
    try:
        # Читаем количество циклов из файла
        repeat_count = read_repeat_count()
        print(f"Запускаем скрипт с {repeat_count} циклами.")
        
        # Читаем выбранных героев из файла
        selected_heroes = read_selected_heroes()
        if not selected_heroes:
            print("Не найдены выбранные герои. Прекращаем выполнение.")
            return
        
        # Ищем изображение gamett.png перед началом выбора героев
        print("Ищем изображение gamett.png...")
        if not find_gamett():
            print("Изображение gamett.png не найдено. Прекращаем выполнение.")
            return
        
        # Интервал между попытками поиска
        search_interval = 0.5
        
        # Приоритетный герой на первой строке списка
        current_cycle = 1
        while current_cycle <= repeat_count:
            print(f"Цикл {current_cycle}/{repeat_count} начат.")
            for hero_info in selected_heroes:
                hero_name, hero_path = hero_info.split(', ')
                hero_img_path = os.path.join(CURRENT_DIR, hero_path)
                
                # Если первый герой - aallrandom.png, выбираем его сразу
                if hero_name == 'aallrandom.png':
                    if click_image_with_similarity(hero_img_path, 0.8, timeout=7):
                        print(f"Герой {hero_name} выбран.")
                        time.sleep(0.5)
                        click_image_with_similarity(os.path.join(ICONS_FOLDER, "pick.png"), 0.7, click_pos=(10, 0))
                        pyautogui.moveTo(0, 0)
                        print("Выбор героя завершен.")
                else:
                    # Иначе, выбираем героя с учетом схожести и времени ожидания
                    if click_image_with_similarity(hero_img_path, 0.5, timeout=7):
                        print(f"Герой {hero_name} выбран.")
                        time.sleep(0.5)
                        click_image_with_similarity(os.path.join(ICONS_FOLDER, "pick.png"), 0.7, click_pos=(10, 0))
                        pyautogui.moveTo(0, 0)
                        print("Выбор героя завершен.")
                    else:
                        print(f"Не удалось выбрать героя {hero_name}. Пробуем следующего.")
                
                time.sleep(search_interval)
            
            print(f"Цикл {current_cycle}/{repeat_count} завершен.")
            current_cycle += 1
            if current_cycle <= repeat_count:
                print(f"Ожидаем 15 секунд перед началом следующего цикла.")
                time.sleep(15)
        
        # Создание файла-сигнала о завершении скрипта
        with open(AUTO_PICK_FILE, "w") as signal_file:
            signal_file.write("Автовыбор завершен.")
        
        print(f"Все циклы завершены. Файл {AUTO_PICK_FILE} создан.")
    
    except Exception as e:
        print(f"Произошла ошибка в скрипте: {e}")

if __name__ == "__main__":
    auto_pick_heroes()
