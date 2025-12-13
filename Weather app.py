import sys
import requests
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel,
    QLineEdit, QPushButton, QVBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        # Widgets
        self.city_label = QLabel("Enter city name:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.icon_label = QLabel(self)
        self.description_label = QLabel(self)

        # Object names for styling
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.description_label.setObjectName("description_label")

        # Alignment
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.initUI()

        # Styling
        self.setStyleSheet("""
            QWidget {
                background-color: lightblue;
            }

            QLabel, QPushButton {
                font-family: Arial;
            }

            QLabel#city_label {
                font-size: 40px;
                font-weight: bold;
            }

            QLineEdit#city_input {
                font-size: 40px;
                padding: 5px;
            }

            QPushButton#get_weather_button {
                font-size: 35px;
                font-weight: bold;
                padding: 10px;
                background-color: white;
                border-radius: 10px;
            }

            QLabel#temperature_label {
                font-size: 60px;
                font-weight: bold;
            }

            QLabel#description_label {
                font-size: 45px;
            }
        """)

        # Buttons
        self.get_weather_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)

    def initUI(self):
        self.setWindowTitle("My Weather App")
        self.resize(400, 600)

        layout = QVBoxLayout()
        layout.addWidget(self.city_label)
        layout.addWidget(self.city_input)
        layout.addWidget(self.get_weather_button)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.description_label)

        self.setLayout(layout)

    def get_weather(self):
        api_key = os.getenv("OPENWEATHER_API_KEY")
        city = self.city_input.text().strip()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)


            if response.status_code == 400:
                self.display_error("❌ 400 Bad Request:\nInvalid Input")
                return
            elif response.status_code == 401:
                self.display_error("❌ 401 Unauthorized:\nInvalid API Key")
                return
            elif response.status_code == 403:
                self.display_error("❌ 403 Forbidden:\nAccess Denied")
                return
            elif response.status_code == 404:
                self.display_error("❌ 404 Not Found:\nCity not found")
                return
            elif response.status_code == 429:
                self.display_error("❌ 429 Too Many Requests:\nAPI limit reached")
                return
            elif 500 <= response.status_code <= 599:
                self.display_error("❌ Server Error:\nTry again later")
                return

            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nServer too slow")
        except requests.exceptions.RequestException as e:
            self.display_error(f"Request Error:\n{e}")

    def display_error(self, message):
        self.temperature_label.setText(message)
        self.icon_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        temp_k = data["main"]["temp"]
        temp_c = temp_k - 273.15

        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.temperature_label.setText(f"{temp_c:.0f}°C")
        self.description_label.setText(weather_description)

        icon_path = self.get_weather_icon(weather_id)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if pixmap.isNull():
                self.icon_label.setText("⚠ Missing icon")
            else:
                self.icon_label.setPixmap(
                    pixmap.scaled(500, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
        else:
            self.icon_label.setText("No icon")

    @staticmethod
    def get_weather_icon(weather_id):
        if 200 <= weather_id <= 232:
            return "weather_icons/thunder.jpg"
        elif 300 <= weather_id <= 321:
            return "weather_icons/drizzle.jpg"
        elif 500 <= weather_id <= 531:
            return "weather_icons/rain.jpg"
        elif 600 <= weather_id <= 622:
            return "weather_icons/snow.jpg"
        elif 700 <= weather_id <= 781:
            return "weather_icons/mist.jpg"
        elif weather_id == 800:
            return "weather_icons/clear.jpg"
        elif 801 <= weather_id <= 804:
            return "weather_icons/cloud.jpg"
        else:
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
