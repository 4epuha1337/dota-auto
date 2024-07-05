import cv2
import numpy as np
import pyautogui
import time
import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
import subprocess

# Порог для совпадения изображений
GAMETT_THRESHOLD = 0.8
GAME_THRESHOLD = 0.85

# Путь к файлу dota2.py
DOTA2_SCRIPT_PATH = "dota2.py"

# Функция для проверки, находится ли окно в свернутом состоянии
def is_window_minimized(window):
    return window.isMinimized

# Функция для активации окна Dota 2
def activate_dota2_window():
    dota2_window_list = gw.getWindowsWithTitle("Dota 2")
    if dota2_window_list:
        dota2_window_list[0].activate()
        return True
    else:
        return False

# Функция для выполнения последовательности действий в Dota 2
def perform_dota2_actions():
    # Нажатие на кнопку "Играть" по координатам (1750, 1025)
    pyautogui.click(1750, 1025)
    time.sleep(1)  # Задержка 1 секунда
    
    # Нажатие на кнопку "Найти игру" по тем же координатам
    pyautogui.click(1750, 1025)
    time.sleep(1)  # Задержка 1 секунда

    while True:
        # Проверяем наличие gamett.png
        if image_exists('gamett.png', threshold=GAMETT_THRESHOLD):
            print("Игра началась.")
            return True
        
        # Если gamett.png не найдено, ищем knopka.png и принимаем игру
        if image_exists('knopka.png'):
            print("Кнопка принятия найдена. Принимаем игру...")
            accept_game()
        
        # Повторная проверка на gamett.png
        time.sleep(0.5)

# Функция для принятия игры
def accept_game():
    accept_button_location = None
    # Снимаем скриншот экрана
    while accept_button_location is None:
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # Загружаем изображение кнопки принятия
        accept_button_image = cv2.imread('knopka.png', cv2.IMREAD_COLOR)
        # Сравниваем скриншот с изображением кнопки
        result = cv2.matchTemplate(screenshot, accept_button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        # Если совпадение найдено, нажимаем на кнопку
        if max_val > 0.8:
            accept_button_center = (
                int(max_loc[0] + accept_button_image.shape[1] / 2),
                int(max_loc[1] + accept_button_image.shape[0] / 2)
            )

            x, y = accept_button_center

            print("Кнопка принятия найдена! Принимаем игру...")
            pyautogui.click(x, y)
            return
        else:
            # Если совпадение не найдено, ждем 0.5 секунды и повторяем
            print("Кнопка принятия не найдена. Ждем 0.5 секунды и повторяем...")
            time.sleep(0.5)

# Функция для проверки наличия изображения на экране
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

# Функция для запуска другого скрипта
def run_dota2_script():
    print("Запуск скрипта dota2.py")
    subprocess.Popen(['python', DOTA2_SCRIPT_PATH])

# Функция для запуска скрипта заданное количество раз
def start_script(repeat_count):
    for i in range(repeat_count):
        print(f"Запуск скрипта: попытка {i + 1} из {repeat_count}")
        
        if activate_dota2_window():
            perform_dota2_actions()
            run_dota2_script()
        else:
            print("Не удалось активировать окно Dota 2.")
            return
        
        if i < repeat_count - 1:
            check_count = 0
            while not image_exists('game.png', threshold=GAME_THRESHOLD):
                if check_count % 600 == 0:  # Печать сообщения каждые 10 минут (600 секунд)
                    print("Ожидание изображения game.png...")
                time.sleep(1)
                check_count += 1
    
    print("Скрипт завершен.")
    root.destroy()  # Закрыть окно root после завершения

# Функция для запуска скрипта по нажатию кнопки
def on_start_button_click():
    repeat_count = repeat_count_var.get()
    start_script(repeat_count)

# Создание основного окна
root = tk.Tk()
root.title("Поиск изображений")

# Метка и выпадающий список для выбора количества повторений
repeat_count_var = tk.IntVar(value=1)
ttk.Label(root, text="Количество повторений:").pack()
ttk.Combobox(root, textvariable=repeat_count_var, values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20]).pack()

# Создание кнопки для запуска скрипта
start_button = tk.Button(root, text="Запустить скрипт", command=on_start_button_click)
start_button.pack()

# Основной цикл работы окна
root.mainloop()
