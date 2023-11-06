import yaml
from typing import Dict, List
import argparse
import json
from urllib import parse, request
import os
from datetime import datetime

CREDENTIALS_PATH: str = "./creds.yaml"
abs_credentials_path: str = os.path.abspath(CREDENTIALS_PATH)


def read_creds(path: str = abs_credentials_path) -> str:
    """Reads the API key from creds.yaml"""
    try:
        with open(path, "r") as f:
            creds: Dict = yaml.safe_load(f)
            open_weather_api_key: str = creds["open_weather_api_key"]
        return open_weather_api_key
    except FileNotFoundError:
        print("creds.yaml file not found")
        raise FileNotFoundError
    except IOError:
        print("Error opening creds.yaml file")
        raise IOError
    except:
        raise
    with open(path, "r") as f:
        creds: Dict = yaml.safe_load(f)
        open_weather_api_key: str = creds["open_weather_api_key"]
    return open_weather_api_key


def define_units(imperial: bool = False, kelvin: bool = False) -> str:
    """
    Defines the units for the OpenWeather API query string.

    Args:
        imperial (bool, optional): A flag indicating whether to use imperial units. Default is False.
        kelvin (bool, optional): A flag indicating whether to use kelvin units. Default is False.

    Returns:
        str: The units for the OpenWeather API query string. Possible values are "imperial", "kelvin", or "metric".
    """
    if imperial:
        units: str = "imperial"
    elif kelvin:
        units: str = "kelvin"
    else:
        units: str = "metric"
    return units


def parse_user_cli_args() -> argparse.Namespace:
    """
    Parses the user's command-line arguments to determine the city name and the units of measurement for displaying weather data.
    the imperial and kelvin flags are mutually exclusive. metric/celcius is the default unit of measurement, inferred by no kelvin or imperial (farenheit) flag.

    Args:
        None

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
            The object has the following attributes:
            - city: A list of strings representing the city/cities for which weather data is requested.
            - imperial: A boolean indicating whether to display data in imperial units.
            - kelvin: A boolean indicating whether to display data in kelvin units.
    """
    parser = argparse.ArgumentParser(
        description="Weather CLI tool returning current weather conditions for a given city."
    )

    parser.add_argument(
        "city",
        nargs="+",
        type=str,
        help="enter a city name (spaces allowed, e.g. 'New York')",
    )

    temperature_args_group = parser.add_mutually_exclusive_group()
    temperature_args_group.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="display data in imperial units (metric by default)",
    )
    temperature_args_group.add_argument(
        "-k",
        "--kelvin",
        action="store_true",
        help="display data in kelvin units (metric by default)",
    )

    return parser.parse_args()


def api_url_query_string_builder(
    open_weather_api_key: str, city: List[str], imperial: bool = False
) -> str:
    """
    Builds the URL query string for the OpenWeather API based on the provided parameters.

    Args:
        open_weather_api_key (str): The API key for the OpenWeather API.
        city (List[str]): A list of city names.
        imperial (bool, optional): A flag indicating whether to use imperial units (default is False).

    Returns:
        str: The URL query string for the OpenWeather API.

    Raises:
        TypeError: If city is not a list of strings.

    Example Usage:
        open_weather_api_key = "1234567890abcdef1234567890abcdef"
        city = ["London"]
        imperial = False

        query_string = api_url_query_string_builder(open_weather_api_key, city, imperial)
        print(query_string)

    Output:
        https://api.openweathermap.org/data/2.5/weather?q=London&units=metric&appid=1234567890abcdef1234567890abcdef
    """
    root_url: str = "https://api.openweathermap.org/data/2.5/weather"
    if imperial:
        units: str = "imperial"
    else:
        units: str = "metric"
    if not isinstance(city, list):
        raise TypeError("city must be a list of strings")
    city_string: str = " ".join(
        city
    )  # joins  multiple word cities (e.g. New York) into a single string.
    if open_weather_api_key is None:
        query_string: str = f"{root_url}?q={city_string}&units={units}"
    else:
        query_string: (
            str
        ) = f"{root_url}?q={city_string}&units={units}&appid={open_weather_api_key}"

    return query_string


def get_weather_data(query_url: str) -> Dict:
    """Gets the weather data from the OpenWeather API."""
    print(query_url)
    with request.urlopen(query_url) as response:
        return json.loads(response.read())


def print_weather_data(weather_data: Dict, metrics: str) -> None:
    """
    Prints the weather data to the console.

    Args:
        weather_data (Dict): A dictionary containing the weather data, including the city name, weather conditions, temperature, humidity, wind speed, cloud cover, and sunrise/sunset times.
        metrics (str): A string indicating the units of measurement for temperature. Possible values are "metric" (Celsius), "imperial" (Fahrenheit), or "kelvin" (Kelvin).

    Returns:
        None

    Example Usage:
        weather_data = {
            "name": "New York",
            "weather": [{"description": "Cloudy"}],
            "main": {"temp": 20, "feels_like": 18, "humidity": 70},
            "wind": {"speed": 10, "deg": 180},
            "clouds": {"all": 80},
            "sys": {"sunrise": 1634567890, "sunset": 1634607890}
        }
        metrics = "metric"
        print_weather_data(weather_data, metrics)

    Output:
        Current weather in New York:
          Conditions: Cloudy
          Temperature: 20 °C
          Feels like: 18 °C
          Humidity: 70%
          Wind: 10 mph
          Wind direction: 180°
          Cloud cover: 80%
          Sunrise: 2021-10-19 07:38:10
          Sunset: 2021-10-19 19:04:50
    """

    def celsius_to_kelvin(temperature: float) -> float:
        """
        Converts a temperature in Celsius units to Kelvin units.

        Args:
            temperature (float): The temperature in Celsius units.

        Returns:
            float: The temperature in Kelvin units.
        """
        return temperature + 273.15

    # Open weather API does not return data in Kelvin units, so we convert from metric to Kelvin as needed.
    if metrics == "kelvin":
        weather_data["main"]["temp"] = celsius_to_kelvin(weather_data["main"]["temp"])
        weather_data["main"]["feels_like"] = celsius_to_kelvin(
            weather_data["main"]["feels_like"]
        )

    degree_sign = "\N{DEGREE SIGN}"

    temp_units = {"metric": "C", "imperial": "F", "kelvin": "K"}

    if "sys" in weather_data and "sunrise" in weather_data["sys"]:
        sunrise_time: datetime = datetime.fromtimestamp(
            weather_data["sys"]["sunrise"]
        ).strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
    else:
        sunrise_time = "N/A"  # type: ignore

    if "sys" in weather_data and "sunset" in weather_data["sys"]:
        sunset_time: datetime = datetime.fromtimestamp(
            weather_data["sys"]["sunset"]
        ).strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
    else:
        sunset_time = "N/A"  # type: ignore

    print(f"Current weather in {weather_data.get('name', 'N/A')}:")
    print(f"  Conditions: {weather_data['weather'][0]['description']}")
    print(
        f"  Temperature: {weather_data['main'].get('temp', 'N/A')} {degree_sign}{temp_units.get(metrics, 'N/A')}"
    )
    print(
        f"  Feels like: {weather_data['main'].get('feels_like', 'N/A')} {degree_sign}{temp_units.get(metrics, 'N/A')}"
    )
    print(f"  Humidity: {weather_data['main'].get('humidity', 'N/A')}%")
    print(f"  Wind: {weather_data['wind'].get('speed', 'N/A')} mph")
    print(f"  Wind direction: {weather_data['wind'].get('deg', 'N/A')}{degree_sign}")
    print(f"  Cloud cover: {weather_data['clouds'].get('all', 'N/A')}%")
    print(f"  Sunrise: {sunrise_time}")
    print(f"  Sunset: {sunset_time}")


if __name__ == "__main__":
    cli_args: argparse.Namespace = parse_user_cli_args()
    metrics = define_units(cli_args.imperial, cli_args.kelvin)
    open_weather_api_key: str = read_creds()
    query_url: str = api_url_query_string_builder(
        open_weather_api_key, cli_args.city, cli_args.imperial
    )
    print_weather_data(get_weather_data(query_url), metrics)
