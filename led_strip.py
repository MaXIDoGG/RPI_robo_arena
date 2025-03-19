import time
from rpi_ws281x import PixelStrip, Color

# Настройки ленты
LED_COUNT = 30        # Количество светодиодов в ленте
LED_PIN = 18          # GPIO пин, к которому подключен DIN (должен поддерживать ШИМ)
LED_FREQ_HZ = 800000  # Частота сигнала (обычно 800 кГц)
LED_DMA = 10          # DMA-канал (можно оставить 10)
LED_BRIGHTNESS = 255  # Яркость (0-255)
LED_INVERT = False    # Инвертировать сигнал (обычно False)
LED_CHANNEL = 0       # 0 или 1 (GPIO18 использует канал 0)

# Создаем объект для управления лентой
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()  # Инициализация ленты

# Функция для установки цвета всех светодиодов
def color_all(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

# Основной цикл
try:
    while True:
        # Включаем светодиоды поочередно разными цветами
        color_all(strip, Color(255, 0, 0))  # Красный
        time.sleep(1)
        color_all(strip, Color(0, 255, 0))  # Зеленый
        time.sleep(1)
        color_all(strip, Color(0, 0, 255))  # Синий
        time.sleep(1)
        color_all(strip, Color(255, 255, 0))  # Желтый
        time.sleep(1)
        color_all(strip, Color(0, 255, 255))  # Голубой
        time.sleep(1)
        color_all(strip, Color(255, 0, 255))  # Пурпурный
        time.sleep(1)

except KeyboardInterrupt:
    # Выключаем все светодиоды при завершении программы
    color_all(strip, Color(0, 0, 0))
    print("Программа завершена.")