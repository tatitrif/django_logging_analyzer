"""Функция collect_statistics собирает статистику из лог-файлов."""

from unittest.mock import patch, mock_open

import pytest

import main

TEST_LOG_CONTENT = [
    "2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]",
    "2025-03-28 12:11:57,000 ERROR django.request: Internal Server Error: /admin/dashboard/",
    "2025-03-28 12:05:13,000 INFO django.request: GET /api/v1/reviews/ 201 OK [192.168.1.97]",
]

EXPECTED_STATS = {
    "/api/v1/reviews/": {"INFO": 1},
    "/admin/dashboard/": {"INFO": 1},
    "/api/v1/checkout/": {"ERROR": 1},
    "/api/v1/users/": {"DEBUG": 1},
}


@pytest.fixture
def mock_file():
    """Фикстура для мока файлов."""
    return mock_open(read_data="".join(TEST_LOG_CONTENT))


def test_collect_statistics(mock_file):
    """Тест сбора статистики."""
    with patch("builtins.open", mock_file):
        with patch("main.read_files") as mock_read_files:
            mock_read_files.return_value = TEST_LOG_CONTENT
            stats = main.collect_statistics(["dummy.log"], "handlers")

            assert stats["/api/v1/reviews/"]["INFO"] == 2
            assert stats["/admin/dashboard/"]["ERROR"] == 1


def test_collect_statistics_empty_files():
    """Тест с пустыми файлами."""
    with patch("main.read_files") as mock_read_files:
        mock_read_files.return_value = []

        result = main.collect_statistics(["empty.log"], "handlers")

        assert not result


if __name__ == "__main__":
    pytest.main()
