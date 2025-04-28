"""Функция read_file построчно читает файлы и обрабатывает ошибки."""

from unittest.mock import patch, mock_open, call

import pytest

from main import read_files, logger

# Тестовые данные
TEST_CONTENT = ["line1\n", "line2\n", "line3\n"]


def test_read_files_success():
    """Тест успешного чтения файлов."""
    file_paths = ["file1.txt", "file2.txt"]
    m_open = mock_open(read_data="".join(TEST_CONTENT))
    with patch("builtins.open", m_open):
        result = list(read_files(file_paths))

        assert result == TEST_CONTENT * 2
        assert m_open.call_count == 2


def test_read_files_file_not_found():
    """Тест обработки отсутствующего файла."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with patch.object(logger, "error") as mock_error:
            result = list(read_files(["missing.txt"]))

            assert result == []
            mock_error.assert_called_once_with("Файл не найден: missing.txt")


def test_read_files_permission_error():
    """Тест обработки ошибки доступа."""
    with patch("builtins.open", side_effect=PermissionError()):
        with patch.object(logger, "error") as mock_error:
            result = list(read_files(["no_access.txt"]))

            assert result == []
            mock_error.assert_called_once_with("Ошибка доступа к файлу: no_access.txt")


def test_read_files_multiple_files_with_errors():
    """Тест обработки нескольких файлов с ошибками и одним успешным."""
    # Тестовые данные для успешного файла
    test_content = ["Line 1\n", "Line 2\n"]

    # Мокируем разные сценарии для каждого файла
    mock_success = mock_open(read_data="".join(test_content))
    exceptions = [
        FileNotFoundError(),  # Первый файл: не найден
        PermissionError(),  # Второй файл: доступ запрещен
        mock_success.return_value,  # успешное чтение
    ]
    with patch("builtins.open") as mocked_open:
        mocked_open.side_effect = exceptions
        with patch.object(logger, "error") as mock_error:
            with patch.object(logger, "debug") as mock_debug:
                result = list(read_files(["missing.txt", "no_access.txt", "good.txt"]))

                # Проверяем ошибки чтения
                assert mock_error.call_count == 2
                expected_errors = [
                    call("Файл не найден: missing.txt"),
                    call("Ошибка доступа к файлу: no_access.txt"),
                ]
                mock_error.assert_has_calls(expected_errors, any_order=True)

                # Проверка успешного чтения
                assert mock_debug.call_count == 2
                expected_debugs = [
                    call("Начато чтение файла: good.txt"),
                    call("Файл полностью прочитан: good.txt"),
                ]
                mock_debug.assert_has_calls(expected_debugs, any_order=True)
                assert result == test_content


if __name__ == "__main__":
    pytest.main()
