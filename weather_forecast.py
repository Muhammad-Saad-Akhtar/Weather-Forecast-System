import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weather Search App")
        self.setGeometry(100, 100, 400, 400)

        # Central Widget and Layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Input field for city name
        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Enter city name...")
        layout.addWidget(self.city_input)

        # Search button
        self.search_button = QPushButton("Get Weather", self)
        self.search_button.clicked.connect(self.display_weather)
        layout.addWidget(self.search_button)

        # Weather display label
        self.weather_label = QLabel("Enter a city to get weather info.", self)
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.weather_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.weather_label)

    def get_coordinates(self, city_name):
        """Fetch latitude and longitude for a city using Open-Meteo Geocoding API."""
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "results" in data and len(data["results"]) > 0:
                    return data["results"][0]["latitude"], data["results"][0]["longitude"]
        except Exception as e:
            return None
        return None

    def get_weather(self, lat, lon):
        """Fetch current, hourly, and weekly weather data for given coordinates."""
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
               f"&hourly=temperature_2m,precipitation_probability,windspeed_10m"
               f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return None
        return None

    def display_weather(self):
        """Fetch and display weather data for the entered city."""
        city = self.city_input.text().strip()
        if not city:
            self.weather_label.setText("Please enter a city name.")
            return

        # Get coordinates of the city
        coordinates = self.get_coordinates(city)
        if not coordinates:
            self.weather_label.setText("City not found. Try again.")
            return

        lat, lon = coordinates
        weather_data = self.get_weather(lat, lon)

        if not weather_data:
            self.weather_label.setText("Weather data not available.")
        else:
            current_temp = weather_data["current_weather"]["temperature"]
            windspeed = weather_data["current_weather"]["windspeed"]
            daily_temp_max = weather_data["daily"]["temperature_2m_max"][0]
            daily_temp_min = weather_data["daily"]["temperature_2m_min"][0]
            sunrise = weather_data["daily"]["sunrise"][0].split("T")[1]
            sunset = weather_data["daily"]["sunset"][0].split("T")[1]

            self.weather_label.setText(
                f"Weather in {city}:\n"
                f"Temperature: {current_temp}°C\n"
                f"Wind Speed: {windspeed} km/h\n"
                f"Max Temp: {daily_temp_max}°C, Min Temp: {daily_temp_min}°C\n"
                f"Sunrise: {sunrise}, Sunset: {sunset}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
