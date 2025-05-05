"""Функция collect_statistics собирает статистику из лог-файлов."""

from unittest.mock import mock_open, patch

import pytest

from main import collect_statistics

TEST_CASES = [
    (
        [
            """
            2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]
            2025-03-28 12:11:57,000 ERROR django.request: Internal Server Error: /admin/dashboard/
            2025-03-28 12:05:13,000 INFO django.request: GET /api/v1/reviews/ 201 OK
            """
        ],
        {
            "/api/v1/reviews/": {"INFO": 2},
            "/admin/dashboard/": {"ERROR": 1},
        },
        "A log entries with different endpoints",
        # "log-файл с записями различного типа"
    ),
    (
        [],
        {},
        "Empty log file",
        # "Пустой log файл"
    ),
    (
        [
            """
            2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]
            2025-03-28 12:44:47,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]
            2025-03-28 12:44:48,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]
            """
        ],
        {
            "/api/v1/reviews/": {"INFO": 3},
        },
        "A log entries of the same type",
        # "log-файл с записями одного типа"
    ),
    (
        [
            """
            2025-03-28 12:44:46,000 INFO django.request: GET /admin/dashboard/ 204 OK [192.168.1.59]
            2025-03-28 12:21:51,000 INFO django.request: GET /admin/dashboard/ 200 OK [192.168.1.68]
            2025-03-28 12:09:06,000 ERROR django.request: Internal Server Error: /admin/dashboard/
            """,
            """
            2025-03-28 12:44:46,000 INFO django.request: GET /admin/dashboard/ 204 OK [192.168.1.59]
            2025-03-28 12:21:51,000 WARNING django.request: GET /admin/dashboard/ 200 OK [192.168.1.68]
            """,
        ],
        {
            "/admin/dashboard/": {"ERROR": 1, "WARNING": 1, "INFO": 3},
        },
        "Multiple log files with the same endpoints",
        # "Несколько log-файлов с одинаковыми конечными точками"
    ),
]


@pytest.fixture
def list_mock_files(request):
    """Фикстура, создающая mock-файлы на основе параметра request."""
    log_contents = request.param
    return [mock_open(read_data=content).return_value for content in log_contents]


@pytest.mark.parametrize(
    "list_mock_files,expected_stats,test_id",
    [(case[0], case[1], case[2]) for case in TEST_CASES],
    indirect=["list_mock_files"],
    ids=[case[2] for case in TEST_CASES],
)
def test_collect_statistics(list_mock_files, expected_stats, test_id):
    """Тест сбора статистики из нескольких файлов."""
    with patch("builtins.open", side_effect=list_mock_files):
        result = collect_statistics(list_mock_files, report_type="handlers")
        assert result == expected_stats


if __name__ == "__main__":
    pytest.main()
