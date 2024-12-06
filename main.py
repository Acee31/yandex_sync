import os
from monitor import monitor_local_folder
from logger import setup_logger

logger = setup_logger(__name__)

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv

        load_dotenv()

        TOKEN = os.getenv("YANDEX_DISK_TOKEN")
        LOCAL_FOLDER = os.getenv("LOCAL_FOLDER")
        YANDEX_FOLDER = os.getenv("YANDEX_FOLDER")

        monitor_local_folder(LOCAL_FOLDER, YANDEX_FOLDER, TOKEN, interval=5)
    except KeyboardInterrupt:
        logger.info("Программа завершена пользователем.")
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
    finally:
        logger.info("Программа завершена.")
