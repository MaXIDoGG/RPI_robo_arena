import os
import pygame
from pathlib import Path
import time

# Настройки
FIFO_PATH = "/tmp/sound_pipe"
SOUND_FILE = "Timer_sound.wav"

# Создаем FIFO (если не существует)
if not Path(FIFO_PATH).exists():
    os.mkfifo(FIFO_PATH, mode=0o666)  # Права на чтение/запись для всех

# Инициализация звука
pygame.mixer.init()
print(f"Сервер звука запущен. Ожидание команд в {FIFO_PATH}...")

while True:
    try:
        with open(FIFO_PATH, 'r') as pipe:
            while True:
                message = pipe.read().strip()
                if message == "play":
                    print("Воспроизведение звука")
                    sound = pygame.mixer.Sound(SOUND_FILE)
                    sound.play()
                    while pygame.mixer.get_busy():  # Ждем окончания
                        pygame.time.wait(100)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(1)  # Пауза при ошибках