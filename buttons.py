import RPi.GPIO as GPIO
import time

# Настройка режима нумерации пинов
GPIO.setmode(GPIO.BCM)

# Настройка пинов для кнопок
buttons = [5, 6, 13, 19, 26, 16]

# Настройка пинов кнопок как входы с подтяжкой вниз
for button in buttons:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        # Проверяем состояние каждой кнопки
        for button in buttons:
            if GPIO.input(button) == GPIO.HIGH:
                print(f"Кнопка GPIO{button} нажата")
        
        # Небольшая задержка для уменьшения нагрузки на процессор
        time.sleep(0.1)

except KeyboardInterrupt:
    # Очистка GPIO при завершении программы
    GPIO.cleanup()
