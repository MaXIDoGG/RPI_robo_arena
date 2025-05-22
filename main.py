import os
import pygame
from pathlib import Path

FIFO = "/tmp/sound_trigger"  # Именованный канал

# Создаем FIFO, если его нет
if not Path(FIFO).exists():
    os.mkfifo(FIFO)

pygame.mixer.init()

print("Ожидание сигналов...")
while True:
    with open(FIFO, 'r') as f:
        signal = f.read().strip()
        if signal == "play":
            print("Воспроизведение звука")
            sound = pygame.mixer.Sound("Timer_sound.wav")
            sound.play()
            while pygame.mixer.get_busy():
                pygame.time.wait(100)