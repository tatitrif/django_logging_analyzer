"""Функция parse_log_line строку лога и возвращает совпадение."""

import pytest

import main


def test_parse_log_line_success():
    """Тест удачного парсинга."""
    content = {
        "2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]": {
            "log_level": "INFO",
            "endpoint": "/api/v1/reviews/",
        },
        "2025-03-28 12:13:21,000 WARNING django.security: ConnectionError: Failed to connect to payment gateway": None,
        "2025-03-28 12:05:33,000 INFO django.request: GET /admin/dashboard/ 204 OK [192.168.1.69]": {
            "log_level": "INFO",
            "endpoint": "/admin/dashboard/",
        },
        "2025-03-28 12:26:26,000 ERROR django.request: Internal Server Error: /api/v1/checkout/ [192.168.1.90]": {
            "log_level": "ERROR",
            "endpoint": "/api/v1/checkout/",
        },
        "2025-03-28 12:18:25,000 ERROR django.request: Internal Server Error: /admin/dashboard/ [192.168.1.90]": {
            "log_level": "ERROR",
            "endpoint": "/admin/dashboard/",
        },
    }
    for line, response in content.items():
        assert main.parse_log_line(line, ("endpoint", "log_level")) == response


def test_parse_log_line_valid():
    """Тест парсинга корректной строки."""
    line = "INFO django.request: GET /api/users"
    result = main.parse_log_line(line, ("endpoint", "log_level"))

    assert result == {"log_level": "INFO", "endpoint": "/api/users"}


def test_parse_log_line_invalid():
    """Тест некорректной строки."""
    line = "Some invalid log line"
    result = main.parse_log_line(line, ("endpoint", "log_level"))

    assert result is None


if __name__ == "__main__":
    pytest.main()
