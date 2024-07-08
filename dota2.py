import pyautogui
import cv2
import numpy as np
import os
import time

# Константы для путей и файлов
SELECTED_HEROES_FILE = "selected_heroes.txt"
HEROES_FILE = "./constants/heroes.txt"
ICONS_FOLDER = "./icons/heroes/"
REPEAT_COUNT_FILE = "repeat_dota2.txt"
AUTO_PICK_FILE = "autopick.txt"

# Функция для чтения выбранных героев из файла
def read_selected_heroes():
    try:
        with open(SELECTED_HEROES_FILE, "r") as file:
            selected_heroes = [line.strip() for line in file.readlines()]
        return selected_heroes
    except FileNotFoundError:
        print(f"Файл {SELECTED_HEROES_FILE} не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла {SELECTED_HEROES_FILE}: {e}")
        return []

# Функция для чтения данных о героях из файла
def read_heroes_info():
    heroes_info = {}
    try:
        with open(HEROES_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    hero_name, img_path = parts
                    heroes_info[hero_name] = img_path.strip()
        return heroes_info
    except FileNotFoundError:
        print(f"Файл {HEROES_FILE} не найден.")
        return {}
    except Exception as e:
        print(f"Ошибка при чтении файла {HEROES_FILE}: {e}")
        return {}

# Функция для выполнения автопика героев
def auto_pick_heroes():
    try:
        # Читаем выбранных героев и данные о героях
        selected_heroes = read_selected_heroes()
        heroes_info = read_heroes_info()

        if not selected_heroes:
            print("Не найдены выбранные герои. Прекращаем выполнение.")
            return

        try:
            with open(REPEAT_COUNT_FILE, "r") as file:
                repeat_count = int(file.read().strip())
        except FileNotFoundError:
            print(f"Файл {REPEAT_COUNT_FILE} не найден.")
            return
        except ValueError:
            print(f"Некорректное значение в файле {REPEAT_COUNT_FILE}.")
            return

        for i in range(repeat_count):
            print(f"Цикл {i + 1}/{repeat_count}")

            for hero_name in selected_heroes:
                if hero_name not in heroes_info:
                    print(f"Для героя {hero_name} нет данных в файле {HEROES_FILE}. Пропускаем.")
                    continue

                img_path = os.path.join(ICONS_FOLDER, heroes_info[hero_name])

                # Поиск героя на экране
                while True:
                    screenshot = pyautogui.screenshot()
                    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    hero_image = cv2.imread(img_path, cv2.IMREAD_COLOR)

                    if hero_image is None:
                        print(f"Не удалось загрузить изображение героя: {img_path}")
                        break

                    result = cv2.matchTemplate(screenshot, hero_image, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)

                    # Если совпадение найдено с коэффициентом схожести выше 0.6
                    if max_val > 0.6:
                        hero_center = (
                            int(max_loc[0] + hero_image.shape[1] / 2),
                            int(max_loc[1] + hero_image.shape[0] / 2)
                        )
                        x, y = hero_center

                        print(f"Герой {hero_name} найден, выбираем...")
                        pyautogui.click(x, y)
                        time.sleep(0.5)

                        # Проверяем, есть ли картинка pick.png на экране
                        pick_image = cv2.imread(os.path.join(ICONS_FOLDER, "pick.png"), cv2.IMREAD_COLOR)
                        if pick_image is not None:
                            result_pick = cv2.matchTemplate(screenshot, pick_image, cv2.TM_CCOEFF_NORMED)
                            _, max_val_pick, _, _ = cv2.minMaxLoc(result_pick)

                            # Если совпадение найдено с коэффициентом схожести выше 0.8
                            if max_val_pick > 0.8:
                                print("Кнопка PICK найдена, выбираем...")
                                pyautogui.click()
                                time.sleep(0.5)
                            else:
                                print("Кнопка PICK не найдена.")
                        break
                    else:
                        print(f"Герой {hero_name} не найден. Ждем 1 секунду и повторяем...")
                        time.sleep(1)

            print(f"Цикл {i + 1}/{repeat_count} завершен.")

            # После каждого цикла, кроме последнего, ждем 15 секунд
            if i < repeat_count - 1:
                print("Ожидание перед следующим циклом...")
                time.sleep(15)

        # После завершения всех циклов создаем файл autopick.txt
        try:
            with open(AUTO_PICK_FILE, "w") as file:
                file.write("autopick.txt created successfully")
            print(f"Файл {AUTO_PICK_FILE} успешно создан.")
        except Exception as e:
            print(f"Ошибка при создании файла {AUTO_PICK_FILE}: {e}")

        print("Скрипт завершен.")
    except Exception as e:
        print(f"Произошла ошибка в скрипте: {e}")

if __name__ == "__main__":
    auto_pick_heroes()
