"""Tests for utility modules."""
import pytest
import logging
from unittest.mock import patch, MagicMock

from src.utils.validators import validate_url
from src.utils.error_handlers import ErrorHandler
from src.utils.logging_config import setup_logging


class TestValidators:
    """Tests for the validators module."""
    
    def test_validate_url_valid_http(self):
        """Test URL validation with valid HTTP URL."""
        assert validate_url("http://example.com") is True
    
    def test_validate_url_valid_https(self):
        """Test URL validation with valid HTTPS URL."""
        assert validate_url("https://example.com") is True
    
    def test_validate_url_invalid_no_protocol(self):
        """Test URL validation with no protocol."""
        assert validate_url("example.com") is False
    
    def test_validate_url_invalid_wrong_protocol(self):
        """Test URL validation with wrong protocol."""
        assert validate_url("ftp://example.com") is False
    
    def test_validate_url_empty_string(self):
        """Test URL validation with empty string."""
        assert validate_url("") is False
    
    def test_validate_url_none(self):
        """Test URL validation with None raises TypeError."""
        with pytest.raises(AttributeError):
            validate_url(None)


class TestErrorHandler:
    """Tests for the ErrorHandler class."""
    
    def test_handle_error_with_string_error(self):
        """Test error handling with string error."""
        error = "Test error message"
        result = ErrorHandler.handle_error(error)
        assert result == {"error": "Test error message"}
    
    def test_handle_error_with_exception(self):
        """Test error handling with Exception object."""
        error = ValueError("Invalid value")
        result = ErrorHandler.handle_error(error)
        assert result == {"error": "Invalid value"}
    
    def test_handle_error_with_custom_exception(self):
        """Test error handling with custom exception."""
        class CustomError(Exception):
            pass
        
        error = CustomError("Custom error message")
        result = ErrorHandler.handle_error(error)
        assert result == {"error": "Custom error message"}
    
    def test_handle_error_with_none(self):
        """Test error handling with None."""
        result = ErrorHandler.handle_error(None)
        assert result == {"error": "None"}


class TestLoggingConfig:
    """Tests for the logging_config module."""
    
    @patch('src.utils.logging_config.logging.basicConfig')
    def test_setup_logging(self, mock_basic_config):
        """Test that setup_logging configures logging correctly."""
        setup_logging()
        mock_basic_config.assert_called_once_with(level=logging.INFO)
    
    @patch('src.utils.logging_config.logging.basicConfig')
    def test_setup_logging_called_multiple_times(self, mock_basic_config):
        """Test that setup_logging can be called multiple times."""
        setup_logging()
        setup_logging()
        assert mock_basic_config.call_count == 2
