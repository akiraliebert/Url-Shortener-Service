import logging
import logging.handlers
import os

LOG_DIR = "logs"
LOG_FILE = "app.log"


def setup_logger(name: str = "app") -> logging.Logger:
    """
    Настраивает логирование для всего проекта.
    Вызывается один раз в main.py.
    """
    os.makedirs(LOG_DIR, exist_ok=True)  # если нет папки logs — создаём

    logger = logging.getLogger(name)

    # Если хендлеры уже есть, значит логгер уже настроен, повторно не трогаем
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # общий уровень логгера — пропускаем всё, фильтруют хендлеры

    # Создаём обработчик для записи в файл с ротацией
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILE),
        maxBytes=5_000_000,   # максимум 5 МБ на файл, потом создаст новый
        backupCount=3,        # сколько старых файлов хранить (app.log.1, app.log.2...)
        encoding="utf-8"      # важно для русских символов
    )
    file_handler.setLevel(logging.INFO)  # фильтр для файла — только INFO и выше
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Создаём обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # на консоль можно выводить и DEBUG
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Возвращает логгер с именем модуля.
    Обычно вызывать как: get_logger(__name__)
    """
    return logging.getLogger(name or "app")