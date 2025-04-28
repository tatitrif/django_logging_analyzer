"""Создание отчета и вывод в консоль."""

from collections import defaultdict

import pytest

from main import create_report, LOG_LEVELS


def test_create_report_basic_case():
    """Успешное создание отчета."""
    stats = {"handler1": {"INFO": 3, "ERROR": 2}}
    report = create_report(stats)

    assert report[0] == "Total requests: 5\n"

    header = report[1]
    assert "HANDLER" in header
    for level in LOG_LEVELS:
        assert level in header

    handler_line = report[2]
    assert "handler1" in handler_line
    assert "3" in handler_line.split()[LOG_LEVELS.index("INFO") + 1]
    assert "2" in handler_line.split()[LOG_LEVELS.index("ERROR") + 1]

    total_line = report[3]
    assert "3" in total_line.split()[LOG_LEVELS.index("INFO")]
    assert "2" in total_line.split()[LOG_LEVELS.index("ERROR")]


def test_missing_levels():
    """Создание отчета неполных данных."""
    stats = {"handler": {"DEBUG": 5}}
    report = create_report(stats)

    handler_line = report[2]
    debug_index = LOG_LEVELS.index("DEBUG") + 1
    assert "5" in handler_line.split()[debug_index]

    total_line = report[-1]
    debug_index = LOG_LEVELS.index("DEBUG")
    assert "5" in total_line.split()[debug_index]


def test_empty_stats():
    """Создание отчета без данных."""
    report = create_report({})

    assert report[0] == "Total requests: 0\n"
    assert len(report) == 3  # Header, total line, и пустая строка

    total_line = report[-1]
    for i in range(1, len(LOG_LEVELS)):
        assert "0" in total_line.split()[i]

    total_line = report[-1]
    for i in range(0, len(LOG_LEVELS)):
        assert "0" in total_line.split()[i]


def test_create_report_format():
    """Тест форматирования отчета."""
    stats = defaultdict(lambda: defaultdict(int))
    stats["/api/users"]["INFO"] = 2
    stats["/api/auth"]["ERROR"] = 1

    report = create_report(stats)

    assert "HANDLER" in report[1]
    assert "INFO" in report[1]
    assert "Total requests: 3" in report[0]


if __name__ == "__main__":
    pytest.main()
