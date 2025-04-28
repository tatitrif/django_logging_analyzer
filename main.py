"""Анализ журнала логирования."""

import argparse
import logging
import re
import sys
from collections import defaultdict
from collections.abc import Generator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def read_files(file_paths: list[str]) -> Generator[str, None, None]:
    """Генератор для построчного чтения файлов с обработкой ошибок."""
    for file_path in file_paths:
        try:
            with open(file_path, encoding="utf-8", errors="replace") as file:
                logger.debug(f"Начато чтение файла: {file_path}")
                yield from file
                logger.debug(f"Файл полностью прочитан: {file_path}")
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
        except PermissionError:
            logger.error(f"Ошибка доступа к файлу: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {str(e)}")


def parse_log_line(line: str, match_groups: tuple) -> dict | None:
    """Парсит строку лога и возвращает совпадение."""
    log_pattern = re.compile(
        rf"(?P<log_level>{'|'.join(LOG_LEVELS)})"
        r".*?django\.request:"
        r"\s(?:GET|POST|PUT|DELETE|PATCH|Internal\sServer\sError:)\s"
        r"(?P<endpoint>/[^\s]+)"
    )
    if match := log_pattern.search(line):
        return {group: match.group(group) for group in match_groups}


def collect_statistics(
    log_files: list[str], report_type: str
) -> dict[str, dict[str, int]]:
    """Собирает статистику из лог-файлов."""
    stats = defaultdict(lambda: defaultdict(int))
    if report_type == "handlers":
        match_group = ("endpoint", "log_level")
    else:
        logger.critical(f"Тип отчета '{report_type}' не реализован")
        sys.exit(1)

    for line in read_files(log_files):
        if parsed := parse_log_line(line, match_group):
            if report_type == "handlers":
                stats[parsed["endpoint"]][parsed["log_level"]] += 1

    return stats


def create_report(stats: dict[str, dict[str, int]]) -> list[str]:
    """Создание отчета и вывод в консоль."""
    # Подготовка данных
    sorted_handlers = sorted(stats.keys())
    level_counts = defaultdict(int)
    total = 0

    # Создаем таблицу
    header = ["HANDLER", *LOG_LEVELS]
    rows = [header]
    col_widths = [len(h) for h in header]

    # Заполняем данные
    for i, handler in enumerate(sorted_handlers):
        row = [handler]
        for level in LOG_LEVELS:
            # обновляем отступы
            for i, cell in enumerate(row):
                cell_len = len(str(cell))
                if cell_len > col_widths[i]:
                    col_widths[i] = cell_len

            # добавляем строку с handler
            count = stats[handler].get(level, 0)
            row.append(count)
            level_counts[level] += count

            # добавляем в итоговую сумму всех requests
            total += count

        rows.append(row)

    # Добавляем строку со статистикой по log_level
    total_by_lvl_row = [" "] + [level_counts[lvl] for lvl in LOG_LEVELS]
    rows.append(total_by_lvl_row)

    # Форматирование отчета с отступами
    formatted_rows = [
        "".join(f"{cell:<{width + 4}}" for cell, width in zip(row, col_widths))
        for row in rows
    ]

    return [f"Total requests: {total}\n", *formatted_rows]


def parse_args_cli():
    """Парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Анализатор логов Django")
    parser.add_argument("log_files", nargs="+", help="Пути к файлам лога")
    parser.add_argument(
        "--report",
        choices=[
            "handlers",
            # TODO: добавить другие отчеты
        ],
        default="handlers",
        help="Тип генерируемого отчета",
    )
    return parser.parse_args()


def main():
    """Точка входа в приложение."""
    args = parse_args_cli()

    try:
        stats = collect_statistics(args.log_files, args.report)
        report = create_report(stats)
        print("\n".join(report))  # noqa
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
