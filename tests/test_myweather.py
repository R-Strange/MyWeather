from my_weather.src.my_weather import read_creds, parse_user_cli_args, api_url_query_string_builder, print_weather_data
import yaml
import argparse
import io
import sys


# needs pytest-mock!!!
import pytest

class TestReadCreds:
    
    def mock_open_yaml(self, mocker, yaml_data="mock data", return_value={"open_weather_api_key": "12345"}, side_effect=None):
        mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data=yaml_data))
        mock_yaml_load = mocker.patch('yaml.safe_load', side_effect=side_effect)
        mock_yaml_load.return_value = return_value
        return mock_open, mock_yaml_load
    
    def assert_yaml_open_and_load_called(self, mock_open, mock_yaml_load):
            mock_open.assert_called_once_with('/home/rstrange/Github/Portfolio/MyWeather/creds.yaml', 'r')
            mock_yaml_load.assert_called_once()

    # Reads the API key from creds.yaml file successfully
    def test_read_creds_success(self, mocker):
        # Given
        mock_open, mock_yaml_load = self.mock_open_yaml(mocker)

        # When
        result = read_creds()
        
        # Then
        assert str(result) == "12345", 'The API key read from the file does not match the expected value.'

    # Returns the API key as a string
    def test_return_type(self, mocker):
        # Mock the yaml.safe_load function to return a dictionary with the expected key-value pair
        
        mock_open, mock_yaml_load = self.mock_open_yaml(mocker)
    
        # Call the read_creds function
        result = read_creds()
    
        # Assert that the type of the result is a string
        assert isinstance(result, str)

    # Handles the file not found error and raises an exception
    def test_file_not_found(self, mocker):
        # Mock the open function to raise a FileNotFoundError
        mocker.patch("builtins.open", side_effect=FileNotFoundError)
    
        # Call the read_creds function and assert that it raises a FileNotFoundError
        with pytest.raises(FileNotFoundError):
            read_creds()

    # Handles the case when the creds.yaml file is empty and raises an exception
    def test_empty_file(self, mocker):
        # Mock the yaml.safe_load function to return None
        mock_open, mock_yaml_load = self.mock_open_yaml(mocker, return_value=None)

        # Call the read_creds function and assert that it raises a TypeError
        with pytest.raises(TypeError):
            read_creds()

    # Handles the case when the creds.yaml file has missing or incorrect keys and raises an exception
    def test_missing_keys(self, mocker):
        # Mock the yaml.safe_load function to return a dictionary with missing keys
        mock_open, mock_yaml_load = self.mock_open_yaml(mocker, return_value={})
    
        # Call the read_creds function and assert that it raises a KeyError
        with pytest.raises(KeyError):
            read_creds()

    # Handles the yaml file format error and raises an exception
    def test_yaml_format_error(self, mocker):
        # Mock the yaml.safe_load function to raise a yaml.YAMLError
        mock_open, mock_yaml_load = self.mock_open_yaml(mocker, side_effect=yaml.YAMLError)
    
        # Call the read_creds function and assert that it raises a yaml.YAMLError
        with pytest.raises(yaml.YAMLError):
            read_creds()
            
class TestParseUserCliArgs:

    # The function correctly parses a city name as a positional argument.
    def test_parse_city_name_positional_argument(self, mocker):
        # Given
        city_name = "New York"
        mocker.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(city=city_name))
    
        # When
        result = parse_user_cli_args()
    
        # Then
        assert result.city == city_name

    # The function correctly parses the imperial flag as an optional argument.
    def test_parse_imperial_flag_optional_argument(self, mocker):
        # Given
        mocker.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(imperial=True))
    
        # When
        result = parse_user_cli_args()
    
        # Then
        assert result.imperial is True

    # The function returns an argparse.Namespace object with the parsed arguments.
    def test_return_argparse_namespace_object(self, mocker):
        # Given
        city_name = "New York"
        mocker.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(city=city_name, imperial=True))
    
        # When
        result = parse_user_cli_args()
    
        # Then
        assert isinstance(result, argparse.Namespace)
        assert result.city == city_name
        assert result.imperial is True

    # The function should return the open weather API key when no city name is provided.
    def test_no_city_name_return_value(self, mocker):
        # Given
        mocker.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(city=None))

        # When
        result = parse_user_cli_args()

        # Then
        assert result == argparse.Namespace(city=None)

    # The function should raise a SystemExit when an invalid flag is provided.
    def test_raise_error_invalid_flag_fixed(self, mocker):
        # Given
        mocker.patch("argparse.ArgumentParser.parse_args", side_effect=SystemExit)

        # When/Then
        with pytest.raises(SystemExit):
            parse_user_cli_args()

    # The function does not raise a ValueError when an invalid city name is provided.
    def test_raise_error_invalid_city_name(self, mocker):
        # Given
        mocker.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(city="1234"))

        # When/Then
        parse_user_cli_args()
        
class TestApiUrlQueryStringBuilder:

    # Builds the URL query string with metric units by default.
    def test_builds_url_query_string_with_metric_units_by_default(self):
        # Given
        city = ["London"]
        imperial = False
        open_weather_api_key = "1234567890abcdef1234567890abcdef"

        # When
        result = api_url_query_string_builder(open_weather_api_key, city, imperial)

        # Then
        assert result == "https://api.openweathermap.org/data/2.5/weather?q=London&units=metric&appid=1234567890abcdef1234567890abcdef"

    # Builds the URL query string with imperial units when imperial=True.
    def test_builds_url_query_string_with_imperial_units_when_imperial_true(self):
        # Given
        city = ["London"]
        imperial = True
        open_weather_api_key = "1234567890abcdef1234567890abcdef"

        # When
        result = api_url_query_string_builder(open_weather_api_key, city, imperial)

        # Then
        assert result == "https://api.openweathermap.org/data/2.5/weather?q=London&units=imperial&appid=1234567890abcdef1234567890abcdef"

    # Joins multiple word cities into a single string for the query string.
    def test_joins_multiple_word_cities_into_single_string_for_query_string(self):
        # Given
        city = ["New", "York"]
        imperial = False
        open_weather_api_key = "1234567890abcdef1234567890abcdef"

        # When
        result = api_url_query_string_builder(open_weather_api_key, city, imperial)

        # Then
        assert result == "https://api.openweathermap.org/data/2.5/weather?q=New York&units=metric&appid=1234567890abcdef1234567890abcdef"

    # Ensures that the query string does not contain 'appid=' if the open_weather_api_key variable is None.
    def test_does_not_contain_appid_if_open_weather_api_key_variable_is_none(self):
        # Given
        city = ["London"]
        imperial = False
        open_weather_api_key = None

        # When
        query_string = api_url_query_string_builder(open_weather_api_key, city, imperial)

        # Then
        assert 'appid=' not in query_string

    # Raises a TypeError if the city argument is not a list.
    def test_raises_type_error_if_city_argument_not_list(self):
        # Given
        city = "London"
        imperial = False
        open_weather_api_key = "1234567890abcdef1234567890abcdef"

        # When, Then
        with pytest.raises(TypeError):
            query_string = api_url_query_string_builder(open_weather_api_key, city, imperial)

    # The test should not expect a ValueError to be raised when the city argument is an empty list.
    def test_does_not_raise_value_error_if_city_argument_empty_list(self):
        # Given
        city = []
        imperial = False
        open_weather_api_key = "1234567890abcdef1234567890abcdef"

        # When, Then
        api_url_query_string_builder(open_weather_api_key, city, imperial)

class TestPrintWeatherData:

    # Should print the weather data to the console
    def test_print_weather_data_console(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890, 'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: 2021-10-18 15:38:10\n" \
                          "  Sunset: 2021-10-19 02:44:50\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Should print the weather data for a given city
    def test_print_weather_data_city_name(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890, 'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: 2021-10-18 15:38:10\n" \
                          "  Sunset: 2021-10-19 02:44:50\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Should print the weather conditions
    def test_print_weather_data_conditions(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890, 'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: 2021-10-18 15:38:10\n" \
                          "  Sunset: 2021-10-19 02:44:50\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Should handle missing 'sys' key in weather_data
    def test_print_weather_data_missing_sys_key_fixed(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: N/A\n" \
                          "  Sunset: N/A\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Should handle missing 'sunrise' key in weather_data['sys']
    def test_print_weather_data_missing_sunrise_key_fixed(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: N/A\n" \
                          "  Sunset: 2021-10-19 02:44:50\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Should handle missing 'sunset' key in weather_data['sys']
    def test_print_weather_data_missing_sunset_key_fixed(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: 2021-10-18 15:38:10\n" \
                          "  Sunset: N/A\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Test that the printed sunrise and sunset times are in the correct format
    def test_printed_times_format(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890, 'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: 2021-10-18 15:38:10\n" \
                          "  Sunset: 2021-10-19 02:44:50\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Test that the printed sunrise and sunset times are in the correct format
    def test_printed_times_format(self):
        metrics="metric"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890, 'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 20 °C\n" \
                          "  Feels like: 18 °C\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: 2021-10-18 15:38:10\n" \
                          "  Sunset: 2021-10-19 02:44:50\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        print_weather_data(weather_data, metrics)

        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Test that imperial units are printed when the metrics are imperial
    def test_print_weather_data_imperial_conversion(self):
        # Given
        metrics="imperial"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890, 'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
            "  Conditions: Cloudy\n" \
            "  Temperature: 20 °F\n" \
            "  Feels like: 18 °F\n" \
            "  Humidity: 80%\n" \
            "  Wind: 10 mph\n" \
            "  Wind direction: 180°\n" \
            "  Cloud cover: 50%\n" \
            "  Sunrise: 2021-10-18 15:38:10\n" \
            "  Sunset: 2021-10-19 02:44:50\n"
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # When
        print_weather_data(weather_data, metrics)
        
        # Then
        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

    # Test that kelvin units are printed when the metrics are kelvin
    def test_print_weather_data_kelvin_conversion(self):
        # Given
        metrics="kelvin"
        weather_data = {
            'name': 'City',
            'weather': [{'description': 'Cloudy'}],
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 80},
            'wind': {'speed': 10, 'deg': 180},
            'clouds': {'all': 50},
            'sys': {'sunrise': 1634567890, 'sunset': 1634607890}
        }
        expected_output = "Current weather in City:\n" \
                          "  Conditions: Cloudy\n" \
                          "  Temperature: 293.15 °K\n" \
                          "  Feels like: 291.15 °K\n" \
                          "  Humidity: 80%\n" \
                          "  Wind: 10 mph\n" \
                          "  Wind direction: 180°\n" \
                          "  Cloud cover: 50%\n" \
                          "  Sunrise: 2021-10-18 15:38:10\n" \
                          "  Sunset: 2021-10-19 02:44:50\n"

        captured_output = io.StringIO()
        sys.stdout = captured_output

        # When
        print_weather_data(weather_data, metrics)

        # Then
        sys.stdout = sys.__stdout__
        assert captured_output.getvalue() == expected_output

