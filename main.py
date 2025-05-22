import spidev
from PyQt5.QtCore import QObject, pyqtSignal
import RPi.GPIO as GPIO
import threading
import time
from dotenv import load_dotenv
import os
from Tournament import Tournament

load_dotenv()
api_url = os.getenv("API_URL")


def color_to_spi(r, g, b):
    """Форматирование цвета для передачи в APA102 (start-bit, B, G, R)"""
    return [0b11100000 | 31, b, g, r]  # Яркость = 31 (максимум)


class GPIOHandler(QObject):
    fight_started = pyqtSignal()
    fight_stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tournament = Tournament(api_url=api_url)
        self.lock = threading.Lock()
        self.threads = []

        self.LED_COUNT = 180
        self.LED_BRIGHTNESS = 31  # от 0 до 31

        self.STATE_WAITING = 0
        self.STATE_READY = 1
        self.STATE_FIGHT = 2
        self.PREPARING = 3

        self.current_state = self.STATE_WAITING
        self.team1_ready = False
        self.team2_ready = False

        # Настройка SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Bus 0, Device 0
        self.spi.max_speed_hz = 8000000  # 8 MHz

        # Кнопки
        self.TEAM1_READY = 5
        self.TEAM1_STOP = 6
        self.TEAM2_READY = 19
        self.TEAM2_STOP = 13
        self.REFEREE_START = 26
        self.REFEREE_STOP = 16

        GPIO.setmode(GPIO.BCM)
        self.buttons = [
            self.TEAM1_READY, self.TEAM1_STOP,
            self.TEAM2_READY, self.TEAM2_STOP,
            self.REFEREE_START, self.REFEREE_STOP
        ]
        for button in self.buttons:
            GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self._running = True
        self.pixels = [[0, 0, 0]] * self.LED_COUNT
        self.show_strip()

    def show_strip(self):
        """Отправка текущих пикселей в SPI"""
        start_frame = [0x00] * 4
        end_frame = [0xFF] * ((self.LED_COUNT + 15) // 16)
        led_data = [byte for r, g, b in self.pixels for byte in color_to_spi(r, g, b)]
        self.spi.xfer2(start_frame + led_data + end_frame)

    def set_color(self, color, team=0):
        """Установка цвета всей ленты или половины"""
        r = (color >> 16) & 0xff
        g = (color >> 8) & 0xff
        b = color & 0xff

        with self.lock:
            if team == 1:
                for i in range(90, self.LED_COUNT):
                    self.pixels[i] = [r, g, b]
            elif team == 2:
                for i in range(90):
                    self.pixels[i] = [r, g, b]
            else:
                self.pixels = [[r, g, b]] * self.LED_COUNT
            self.show_strip()

    def fade_to_color(self, target_color, team=0, duration=0.5):
        steps = 100
        delay = duration / steps

        if team == 2:
            current = self.pixels[0]
        else:
            current = self.pixels[91]

        r0, g0, b0 = current
        r1 = (target_color >> 16) & 0xff
        g1 = (target_color >> 8) & 0xff
        b1 = target_color & 0xff

        for step in range(steps):
            r = int(r0 + (r1 - r0) * step / steps)
            g = int(g0 + (g1 - g0) * step / steps)
            b = int(b0 + (b1 - b0) * step / steps)
            self.set_color((r << 16) + (g << 8) + b, team=team)
            time.sleep(delay)

    def circle_color(self, first_color, second_color, frequency=100):
        delay = 1 / frequency
        line_id = 0
        while self.current_state == self.STATE_WAITING and self._running:
            for i in range(self.LED_COUNT):
                pos = (i - line_id) % self.LED_COUNT
                if pos <= self.LED_COUNT // 2:
                    self.pixels[i] = [
                        (second_color >> 16) & 0xff,
                        (second_color >> 8) & 0xff,
                        second_color & 0xff
                    ]
                else:
                    self.pixels[i] = [
                        (first_color >> 16) & 0xff,
                        (first_color >> 8) & 0xff,
                        first_color & 0xff
                    ]
            self.show_strip()
            line_id += 1
            time.sleep(delay)

    def run_loop(self):
        print("Starting!")
        try:
            self.set_color(0x000000)
            threading.Thread(target=self.circle_color, args=(0x0000FF, 0xFF0000)).start()
            while self._running:
                for button in self.buttons:
                    if GPIO.input(button) == GPIO.HIGH:
                        print(button)
                        t = threading.Thread(target=self.handle_button_press, args=(button,))
                        t.start()
                        self.threads.append(t)
                        time.sleep(0.1)
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.stop()
            print("Программа завершена.")

    def handle_button_press(self, button):
        if button == self.TEAM1_READY and self.current_state == self.PREPARING and not self.team1_ready:
            self.team1_ready = True
            self.fade_to_color(0x00FF00, team=1)
            if self.team2_ready:
                self.current_state = self.STATE_READY
            self.tournament.send_team1_ready()
        elif button == self.TEAM2_READY and self.current_state == self.PREPARING and not self.team2_ready:
            self.team2_ready = True
            self.fade_to_color(0x00FF00, team=2)
            if self.team1_ready:
                self.current_state = self.STATE_READY
            self.tournament.send_team2_ready()
        elif button == self.REFEREE_START and self.current_state != self.STATE_FIGHT:
            self.fight_started.emit()
            if self.current_state == self.STATE_WAITING:
                self.current_state = self.PREPARING
                self.tournament.send_preparing()
            else:
                self.current_state = self.STATE_FIGHT
                self.fade_to_color(0xFF0000)
                self.tournament.send_fight_start()
        elif (button in [self.TEAM1_STOP, self.TEAM2_STOP, self.REFEREE_STOP]) and self.current_state != self.STATE_WAITING:
            self.fight_stopped.emit()
            self.reset_to_waiting()
            self.tournament.send_fight_end()

    def reset_to_waiting(self):
        self.current_state = self.STATE_WAITING
        self.team1_ready = False
        self.team2_ready = False
        self.fade_to_color(0x0000FF)

    def stop(self):
        print("Stopping")
        for t in self.threads:
            t.join(timeout=0.1)
        self.set_color(0x000000)
        self.spi.close()
        self._running = False
        GPIO.cleanup()
        
def main():
	gpio_handler = GPIOHandler()
	gpio_handler.run_loop()

if __name__ == "__main__":
  main()
