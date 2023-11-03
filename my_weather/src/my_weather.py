import yaml
from typing import Dict, List
import argparse
import json
from urllib import parse, request
import os
CREDENTIALS_PATH: str = "./creds.yaml"
abs_credentials_path: str = os.path.abspath(CREDENTIALS_PATH)

def read_creds(path: str=abs_credentials_path) -> str:
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

 
def parse_user_cli_args() -> argparse.Namespace:
    """Parses the user's CLI arguments:
    city: a city name
    flags:
        -i, --imperial: display data in imperial units (metric by default)
    """
    parser = argparse.ArgumentParser(description="Weather CLI tool returning current weather conditions for a given city.")
    
    parser.add_argument("city", nargs="+", type=str, help="enter a city name (multiple words allowed)")
    parser.add_argument("-i", "--imperial", action="store_true", help="display data in imperial units (metric by default)")
    
    return parser.parse_args()

def api_url_query_string_builder(city: List[str], imperial: bool = False) -> str:
    """
    Builds the URL query string for the OpenWeather API.
    example API string: https://api.openweathermap.org/data/2.5/weather?q=London&units=metric&appid=1234567890abcdef1234567890abcdef
    """
    root_url: str = "https://api.openweathermap.org/data/2.5/weather"
    if imperial:
        units: str = "imperial"
    else:
        units: str = "metric"
    city_string: str = " ".join(city)  # joins  multiple word cities (e.g. New York) into a single string.
    query_string: str = f"{root_url}?q={city_string}&units={units}&appid={open_weather_api_key}"

    return query_string

def get_weather_data(query_url: str) -> Dict:
    """Gets the weather data from the OpenWeather API."""
    print(query_url)
    with request.urlopen(query_url) as response:
        return json.loads(response.read())
    
def print_weather_data(weather_data: Dict) -> None:
    """Prints the weather data to the console."""
    print(f"Current weather in {weather_data['name']}:")
    print(f"  Conditions: {weather_data['weather'][0]['description']}")
    print(f"  Temperature: {weather_data['main']['temp']} degrees")
    print(f"  Feels like: {weather_data['main']['feels_like']} degrees")
    print(f"  Humidity: {weather_data['main']['humidity']}%")
    print(f"  Wind: {weather_data['wind']['speed']} mph")
    print(f"  Wind direction: {weather_data['wind']['deg']} degrees")
    print(f"  Cloud cover: {weather_data['clouds']['all']}%")
    print(f"  Sunrise: {weather_data['sys']['sunrise']}")
    print(f"  Sunset: {weather_data['sys']['sunset']}")

if __name__ == "__main__":
    cli_args: argparse.Namespace = parse_user_cli_args()
    open_weather_api_key: str = read_creds()
    query_url: str = api_url_query_string_builder(cli_args.city, cli_args.imperial)
    print_weather_data(get_weather_data(query_url))
    
    
    