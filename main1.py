import time
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color
from playsound import playsound
# import pyglet
# sound = pyglet.media.load("//home//admin//project//buttons//start.mp3")
# sound.play()


# Настройки светодиодной ленты
LED_COUNT = 180
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# Состояния системы
STATE_WAITING = 0
STATE_READY = 1
STATE_FIGHT = 2
current_state = STATE_WAITING

# Настройка пинов для кнопок
TEAM1_READY = 6
TEAM1_STOP = 5
TEAM2_READY = 13
TEAM2_STOP = 16
REFEREE_START = 19
REFEREE_STOP = 26

# Флаги готовности команд
team1_ready = False
team2_ready = False

# Инициализация светодиодной ленты
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
buttons = [TEAM1_READY, TEAM1_STOP, TEAM2_READY, TEAM2_STOP, REFEREE_START, REFEREE_STOP]
for button in buttons:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def set_color(color, duration=0):
    """Установка цвета всей ленты"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    if duration > 0:
        time.sleep(duration)

def fade_to_color(target_color, duration=1.0):
    """Плавный переход к указанному цвету"""
    steps = 100
    delay = duration / steps
    
    current_color = strip.getPixelColor(0)
    current_r = (current_color >> 16) & 0xff
    current_g = (current_color >> 8) & 0xff
    current_b = current_color & 0xff
    
    target_r = (target_color >> 16) & 0xff
    target_g = (target_color >> 8) & 0xff
    target_b = target_color & 0xff
    
    for step in range(steps):
        r = int(current_r + (target_r - current_r) * (step / steps))
        g = int(current_g + (target_g - current_g) * (step / steps))
        b = int(current_b + (target_b - current_b) * (step / steps))
        
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(r, g, b))
        strip.show()
        time.sleep(delay)

def reset_to_waiting():
    """Сброс в состояние ожидания"""
    global current_state, team1_ready, team2_ready
    current_state = STATE_WAITING
    team1_ready = False
    team2_ready = False
    fade_to_color(Color(0, 0, 255))  # Синий

def handle_button_press(button):
    """Обработка нажатия кнопок"""
    global current_state, team1_ready, team2_ready
    
    if button == TEAM1_READY and current_state == STATE_WAITING:
        team1_ready = True
        set_color(Color(0, 255, 0), 0)  # Зеленый на 2 секунды
        if team2_ready:
            current_state = STATE_READY
    
    elif button == TEAM2_READY and current_state == STATE_WAITING:
        team2_ready = True
        set_color(Color(0, 255, 0), 0)  # Зеленый на 2 секунды
        if team1_ready:
            current_state = STATE_READY
    
    elif button == REFEREE_START and current_state == STATE_READY:
        current_state = STATE_FIGHT
        playsound('//home//admin//project//buttons//start.mp3', block=False)
        fade_to_color(Color(255, 0, 0))  # Красный
    
    elif (button in [TEAM1_STOP, TEAM2_STOP, REFEREE_STOP]) and current_state != STATE_WAITING:
        reset_to_waiting()
        playsound('//home//admin//project//buttons//stop.mp3', block=False)

# Основной цикл
try:
    # Инициализация - синий цвет
    set_color(Color(0, 0, 255))
    
    while True:
        # Проверка всех кнопок
        for button in buttons:
            if GPIO.input(button) == GPIO.HIGH:
                handle_button_press(button)
                time.sleep(0.1)  # Задержка для антидребезга
                print(current_state, team1_ready, team2_ready, button)
        
        time.sleep(0.05)

except KeyboardInterrupt:
    set_color(Color(0, 0, 0))  # Выключить все светодиоды
    GPIO.cleanup()
    print("Программа завершена.")