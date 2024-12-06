import logging


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("sync_log.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s || %(name)s || %(levelname)s || %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
