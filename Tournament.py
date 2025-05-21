import requests
import json
import socketio

class Tournament:
    def __init__(self, id, login, password, api_url):
        self.api_url = api_url
        self.id = id
        self.login = login
        self.password = password
        self.sio = socketio.Client()
        
        # Регистрация обработчиков событий
        self.register_handlers()
        
        # Подключение к серверу и авторизация
        self.connect()
        

    def register_handlers(self):
        """Регистрирует все обработчики событий."""
        @self.sio.event
        def connect():
            print("✅ Подключено к серверу.")

        @self.sio.event
        def disconnect():
            print("❌ Отключено от сервера.")
            
        #ID поединка
        @self.sio.on("BACK-END: Fight ID sent.")
        def get_fight_id(data):
            self.id = data
            
        # Обработчики для событий от сервера
        @self.sio.on("BACK-END: Team 1 ready sent.")
        def on_team1_ready(data):
            print(f"Команда 1 готова: {data}")

        @self.sio.on("BACK-END: Team 2 ready sent.")
        def on_team2_ready(data):
            print(f"Команда 2 готова: {data}")

        @self.sio.on("BACK-END: Fight start sent.")
        def on_fight_start(data):
            print(f"Бой начался: {data}")

        @self.sio.on("BACK-END: Fight end sent.")
        def on_fight_end(data):
            print(f"Бой завершен: {data}")

    def connect(self):
        """Подключается к серверу."""
        self.sio.connect(self.api_url, wait_timeout = 10)

    def send_team1_ready(self):
        """Отправляет готовность команды 1."""
        self.sio.emit("BUTTONS: Team 1 ready.", self.id)

    def send_team2_ready(self):
        """Отправляет готовность команды 2."""
        self.sio.emit("BUTTONS: Team 2 ready.", self.id)

    def send_fight_start(self):
        """Отправляет запрос на начало боя."""
        self.sio.emit("BUTTONS: Fight start.", self.id)

    def send_fight_end(self):
        """Отправляет запрос на завершение боя."""
        self.sio.emit("BUTTONS: Fight end.", self.id)

    def disconnect(self):
        """Отключается от сервера."""
        self.sio.disconnect()


# Пример использования
if __name__ == "__main__":
    tournament = Tournament(
        id=123,
        login="admin",
        password="secret",
        api_url="https://grmvzdlx-3008.euw.devtunnels.ms"  # Укажите ваш URL сервера
    )