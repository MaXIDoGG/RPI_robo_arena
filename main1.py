import time
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color

# Настройки светодиодной ленты
LED_COUNT = 30        # Количество светодиодов в ленте
LED_PIN = 18          # GPIO пин, к которому подключен DIN (должен поддерживать ШИМ)
LED_FREQ_HZ = 800000  # Частота сигнала (обычно 800 кГц)
LED_DMA = 10          # DMA-канал (можно оставить 10)
LED_BRIGHTNESS = 255  # Яркость (0-255)
LED_INVERT = False    # Инвертировать сигнал (обычно False)
LED_CHANNEL = 0       # 0 или 1 (GPIO18 использует канал 0)

# Настройка пинов для кнопок
buttons = {
    5: Color(255, 0, 0),    # Красный
    6: Color(0, 255, 0),    # Зеленый
    13: Color(0, 0, 255),   # Синий
    16: Color(255, 255, 0), # Желтый
    19: Color(255, 0, 255), # Пурпурный
    26: Color(0, 255, 255)  # Голубой
}

# Инициализация светодиодной ленты
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
for button in buttons:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Функция для установки цвета всех светодиодов
def color_all(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

# Основной цикл
try:
    while True:
        for button, color in buttons.items():
            if GPIO.input(button) == GPIO.HIGH:
                color_all(strip, color)  # Включаем цвет, соответствующий кнопке
                time.sleep(0.2)  # Небольшая задержка для устранения дребезга
        time.sleep(0.1)  # Небольшая задержка для уменьшения нагрузки на процессор

except KeyboardInterrupt:
    # Выключить все светодиоды при завершении программы
    color_all(strip, Color(0, 0, 0))
    GPIO.cleanup()
    print("Программа завершена.")