import React, { useState, useEffect } from "react";
import Lottie from "lottie-react";
import sunnyAnimation from "./assets/Sunny.json";
import rainAnimation from "./assets/Rain.json";
import snowAnimation from "./assets/Snow.json";
import thunderAnimation from "./assets/ThunderStorm.json";
import nightAnimation from "./assets/Night.json";
import "./WeatherApp.css";

const WeatherApp = () => {
  const [city, setCity] = useState("");
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 });

  // Dynamically detect backend IP
  const API_URL = `${window.location.protocol}//${window.location.hostname}:8000/weather?city=`;

  useEffect(() => {
    const moveCursor = (e) => {
      setCursorPos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", moveCursor);
    return () => window.removeEventListener("mousemove", moveCursor);
  }, []);

  const fetchWeather = async () => {
    if (!city) return;
    setLoading(true);

    try {
      const requestURL = `${API_URL}${encodeURIComponent(city)}`;
      console.log("Fetching:", requestURL);

      const response = await fetch(requestURL);
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

      const data = await response.json();
      console.log("API Response:", data);

      if (data.detail) {
        alert("City not found! Please enter a valid city.");
        setWeatherData(null);
      } else {
        setWeatherData(data);
      }
    } catch (error) {
      console.error("Error fetching weather data:", error);
      alert("Failed to fetch weather data. Please check your backend connection.");
    }

    setLoading(false);
  };

  const getWeatherAnimation = (condition) => {
    if (!condition) return sunnyAnimation;

    const conditionText = condition.toLowerCase();
    if (conditionText.includes("thunder")) return thunderAnimation;
    if (conditionText.includes("rain") || conditionText.includes("drizzle")) return rainAnimation;
    if (conditionText.includes("snow") || conditionText.includes("sleet")) return snowAnimation;

    const currentHour = new Date().getHours();
    return currentHour >= 19 || currentHour < 6 ? nightAnimation : sunnyAnimation;
  };

  return (
    <div className="weather-container">
      <div className="cursor-trail" style={{ left: cursorPos.x, top: cursorPos.y }}></div>

      {weatherData && (
        <Lottie animationData={getWeatherAnimation(weatherData.condition)} className="background-animation" />
      )}

      <div className="content">
        <h1 className="app-title">Weather App</h1>
        <div className="input-container">
          <input
            type="text"
            placeholder="Enter city name"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="city-input"
          />
          <button onClick={fetchWeather} className="weather-button">
            Get Weather
          </button>
        </div>

        {loading && <p className="loading-text">Loading...</p>}

        {weatherData && (
          <div className="weather-info">
            <h2 className="location">
              {weatherData.city}, {weatherData.country}
            </h2>
            <div className="weather-details">
              <p>🌡️ Temperature: {weatherData.temperature}°C</p>
              <p>☁️ Condition: {weatherData.condition}</p>
              <p>💨 Wind Speed: {weatherData.wind_speed} kph</p>
              <p>💧 Humidity: {weatherData.humidity}%</p>
              <p>🌡️ Feels Like: {weatherData.feels_like}°C</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WeatherApp;
