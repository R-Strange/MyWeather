from my_weather.src.my_weather import read_creds
import yaml


# Dependencies:
# pip install pytest-mock
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