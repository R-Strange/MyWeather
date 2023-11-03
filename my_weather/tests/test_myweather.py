import sys
import os
sys.path.append(os.path.abspath('../src/'))

import pytest
from unittest.mock import patch
# from my_weather import get_weather_data, print_weather_data
from my_weather.src.my_weather import get_weather_data, print_weather_data



@patch('MyWeather.request.urlopen')
def test_get_weather_data(mock_urlopen):
    mock_response = b'{"name": "London", "weather": [{"description": "overcast"}], "main": {"temp": 10.0, "feels_like": 8.0, "humidity": 70}, "wind": {"speed": 5.0, "deg": 180}, "clouds": {"all": 90}, "sys": {"sunrise": 1630000000, "sunset": 1630000000}}'
    mock_urlopen.return_value.__enter__.return_value.read.return_value = mock_response
    expected_result = {
        "name": "London",
        "weather": [{"description": "overcast"}],
        "main": {"temp": 10.0, "feels_like": 8.0, "humidity": 70},
        "wind": {"speed": 5.0, "deg": 180},
        "clouds": {"all": 90},
        "sys": {"sunrise": 1630000000, "sunset": 1630000000}
    }
    result = get_weather_data("https://api.openweathermap.org/data/2.5/weather?q=London&units=metric&appid=1234567890abcdef1234567890abcdef")
    assert result == expected_result

@patch('builtins.print')
def test_print_weather_data(mock_print):
    weather_data = {
        "name": "London",
        "weather": [{"description": "overcast"}],
        "main": {"temp": 10.0, "feels_like": 8.0, "humidity": 70},
        "wind": {"speed": 5.0, "deg": 180},
        "clouds": {"all": 90},
        "sys": {"sunrise": 1630000000, "sunset": 1630000000}
    }
    print_weather_data(weather_data)
    mock_print.assert_called_with(
        "Current weather in London:",
        "  Conditions: overcast",
        "  Temperature: 10.0 degrees",
        "  Feels like: 8.0 degrees",
        "  Humidity: 70%",
        "  Wind: 5.0 mph",
        "  Wind direction: 180 degrees",
        "  Cloud cover: 90%",
        "  Sunrise: 1630000000",
        "  Sunset: 1630000000"
    )