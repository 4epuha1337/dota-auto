import threading
import cv2
import numpy as np
import pyautogui
import time
import os

# Отключение функции безопасности PyAutoGUI
pyautogui.FAILSAFE = False

# Порог для совпадений изображений
THRESHOLD = 0.7

class AutoBuy(threading.Thread):  # Наследуем от threading.Thread
    def __init__(self, repeat_count, selected_items, on_complete=None):
        super().__init__()  # Вызываем конструктор родительского класса

        self.repeat_count = repeat_count
        self.selected_items = selected_items
        self.on_complete = on_complete  # Колбэк для оповещения о завершении
        self._stop_event = threading.Event()  # Флаг для остановки потока

    def stop(self):
        self._stop_event.set()  # Устанавливаем флаг остановки

    def image_exists(self, image_path, threshold=THRESHOLD):
        # Загрузка изображения предмета
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            print(f"Не удалось загрузить изображение: {image_path}")
            return False, None, None
        
        # Скриншот текущего экрана
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Поиск изображения предмета на экране
        result = cv2.matchTemplate(screenshot_bgr, image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # Найдено изображение с заданным порогом совпадения
            return True, max_loc, image
        else:
            return False, None, None

    def click_image(self, location, image):
        # Получение координат центра изображения
        center_x = location[0] + image.shape[1] // 2
        center_y = location[1] + image.shape[0] // 2
        
        # Наведение курсора на центр изображения и выполнение правого клика
        pyautogui.moveTo(center_x, center_y)
        time.sleep(0.3)  # Задержка перед кликом
        pyautogui.click(button='right')
        time.sleep(0.3)  # Задержка после клика
        pyautogui.moveTo(0, 0)  # Перемещение курсора в точку (0, 0)

    def main(self):
        
        print(f"Будет выполнено {self.repeat_count} циклов")
        
        if not self.selected_items:
            print("Список предметов пуст")
            return
        
        print("Список предметов для закупки:")
        for item_info in self.selected_items:
            print(f"- {item_info['name']}")
        
        # Выполнение циклов
        for cycle in range(1, self.repeat_count + 1):
            if self._stop_event.is_set():
                print("Остановка работы по запросу.")
                return False
            
            print(f"Цикл {cycle}/{self.repeat_count} начат")
            
            # Проход по списку предметов и их поиск на экране
            for item_info in self.selected_items[:]:
                item_name = item_info['name']
                item_path = item_info['icon_path']

                found_item = False
                while not found_item:
                    if self._stop_event.is_set():
                        print("Остановка работы по запросу.")
                        return False
                    
                    found_item, location, image = self.image_exists(item_path)
                    if found_item:
                        self.click_image(location, image)
                        print(f"Нажатие на {item_name} и перемещение курсора в точку (0, 0)")
                        time.sleep(1)  # Задержка после нажатия
                        pyautogui.moveTo(0, 0)  # Перемещение курсора в точку (0, 0)
                        self.selected_items.remove(item_info)  # Удаление найденного элемента из списка
                    else:
                        print(f"Поиск {item_name}...")
                        time.sleep(0.5)  # Проверка раз в 1 секунду
            
            print(f"Цикл {cycle}/{self.repeat_count} завершен")
            
            if cycle < self.repeat_count:
                print(f"Пауза перед следующим циклом ({cycle+1}/{self.repeat_count})...")
                time.sleep(15)  # Пауза 15 секунд между циклами
        
    def run(self):
        self.main()

# Метод чтоб запустить скрипт отдельно для отладки
if __name__ == "__main__":
    repeat_count = 3  # Количество повторений

    selected_items_array = [
        {'name': 'Blight Stone.300', 'icon_path': '.\\icons\\Items\\Blight Stone.300.png'},
        {'name': 'Clarity.50', 'icon_path': '.\\icons\\Items\\Clarity.50.png'},
        {'name': 'Observer Ward.0', 'icon_path': '.\\icons\\Items\\Observer Ward.0.png'}
    ]

    auto_buy = AutoBuy(repeat_count=3, selected_items=selected_items_array)
    auto_buy.start()

    try:
        while auto_buy.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Получен сигнал прерывания, остановка скрипта...")
        auto_buy.stop()
        auto_buy.join()
    print("Скрипт завершен.")