"""Функция parse_args_cli парсит аргументы командной строки."""

from unittest.mock import patch

import pytest

import main


def test_parse_args_cli_with_default_report():
    """Тест парсинга аргументов с дефолтным значением --report."""
    test_args = ["logs/app1.log", "logs/app2.log"]

    with patch("sys.argv", ["main.py"] + test_args):
        args = main.parse_args_cli()

        assert args.log_files == test_args
        assert args.report == "handlers"


def test_parse_args_cli_with_report_specified():
    """Тест парсинга аргументов с явным указанием --report."""
    test_args = ["logs/app1.log", "logs/app2.log", "--report", "handlers"]

    with patch("sys.argv", ["main.py"] + test_args):
        args = main.parse_args_cli()

        assert args.log_files == ["logs/app1.log", "logs/app2.log"]
        assert args.report == "handlers"


def test_parse_args_cli_with_multiple_log_files():
    """Тест парсинга с несколькими файлами логов."""
    test_args = [
        "logs/app1.log",
        "logs/app2.log",
        "logs/app3.log",
        "--report",
        "handlers",
    ]

    with patch("sys.argv", ["main.py"] + test_args):
        args = main.parse_args_cli()

        assert args.log_files == ["logs/app1.log", "logs/app2.log", "logs/app3.log"]
        assert args.report == "handlers"


def test_parse_args_cli_with_invalid_report_type():
    """Тест обработки невалидного типа отчета."""
    test_args = ["logs/app1.log", "--report", "invalid_report"]

    with patch("sys.argv", ["main.py"] + test_args):
        with pytest.raises(SystemExit) as mock_print:
            main.parse_args_cli()

        assert mock_print.value.code == 2


def test_parse_args_cli_with_no_log_files():
    """Тест обработки отсутствия файлов логов."""
    test_args = ["--report", "handlers"]

    with patch("sys.argv", ["main.py"] + test_args):
        with pytest.raises(SystemExit) as mock_print:
            main.parse_args_cli()

        assert mock_print.value.code == 2


def test_parse_args_cli_help_message():
    """Тест вывода help сообщения."""
    with patch("sys.argv", ["main.py", "--help"]):
        with pytest.raises(SystemExit):
            with patch("argparse.ArgumentParser._print_message") as mock_print:
                main.parse_args_cli()

        help_text = mock_print.call_args[0][0]
        assert "Анализатор логов Django" in help_text
        assert "Пути к файлам лога" in help_text
        assert "Тип генерируемого отчета" in help_text


def test_parse_args_cli_with_relative_paths():
    """Тест с относительными путями к файлам."""
    test_args = ["./logs/app1.log", "../app2.log", "--report", "handlers"]

    with patch("sys.argv", ["main.py"] + test_args):
        args = main.parse_args_cli()

        assert args.log_files == ["./logs/app1.log"]
        assert args.log_files != ["../app2.log"]
        assert args.report == "handlers"


@pytest.fixture
def create_test_files(tmp_path):
    """Фикстура для создания тестовых файлов."""
    empty_file = tmp_path / "empty.log"
    empty_file.write_text("")
    return empty_file


def test_empty_file(create_test_files, caplog):
    """Тест с пустым файлом."""
    empty_file = create_test_files

    with patch("sys.argv", ["script.py", str(empty_file)]):
        with pytest.raises(SystemExit):
            main.parse_args_cli()

    assert any("Файл пустой" in record.message for record in caplog.records)


if __name__ == "__main__":
    pytest.main()
