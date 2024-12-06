import os
import time
from sync import SyncFolders
from logger import setup_logger


logger = setup_logger(__name__)


def monitor_local_folder(local_folder: str, yandex_folder: str, token: str, interval: int = 5) -> None:
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


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    TOKEN = os.getenv("YANDEX_DISK_TOKEN")
    LOCAL_FOLDER = os.getenv("LOCAL_FOLDER")
    YANDEX_FOLDER = os.getenv("YANDEX_FOLDER")

    monitor_local_folder(LOCAL_FOLDER, YANDEX_FOLDER, TOKEN)
