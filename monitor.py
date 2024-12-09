import os
import time

from sync import SyncFolders
from logger import setup_logger


logger = setup_logger(__name__)


def monitor_local_folder(local_folder: str, yandex_folder: str, token: str, interval: int = 5) -> None:
    """
    Мониторит локальную папку на предмет изменений
    и синхронизирует их с Яндекс.Диском
    :param local_folder: Путь к локальной папке
    :param yandex_folder: Путь к папке на Яндекс.Диске
    :param token: Токен доступа к Яндекс.Диску
    :param interval: Интервал проверки изменений в секундах (по умолчанию 5)
    """
    absolute_local_path = os.path.abspath(local_folder)
    logger.info(f"Программа начинает работу с локальной директорией: {absolute_local_path}")

    syncer = SyncFolders(local_folder, yandex_folder, token)

    while True:
        try:
            logger.info("Начинаем проверку изменений в локальной папке...")
            syncer.sync()
        except Exception as e:
            logger.error(f"Ошибка во время мониторинга: {e}")
        time.sleep(interval)
