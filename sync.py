import os
from typing import Dict, List

import requests

from yandex_class import YandexDisk
from logger import setup_logger

logger = setup_logger(__name__)


class SyncFolders:
    """
    Класс для синхронизации локальной папки с папкой на Яндекс.Диске
    """
    def __init__(self, local_folder: str, yandex_folder: str, token: str):
        self.local_folder = local_folder
        self.yandex_folder = yandex_folder
        self.token = token
        self.yandex_disk = YandexDisk(token, yandex_folder)
        self.yandex_disk.check_or_create_yandex_folder()

    def get_yandex_folder_content(self, folder_name: str) -> List[Dict[str, str]]:
        """
        Получает содержимое указанной папки на Яндекс.Диске
        :param folder_name: Путь к папке на Яндекс.Диске
        :return: Список с содержимым папки на Яндекс.Диске
        """
        try:
            params = {"path": folder_name}
            response = requests.get(self.yandex_disk.base_url, headers=self.yandex_disk.headers, params=params)
            if response.status_code == 200:
                return response.json()["_embedded"]["items"]
            else:
                logger.error(f"Ошибка при получении содержимого папки: {response.status_code}, {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с Яндекс.Диском: {e}")
            return []

    def sync(self) -> None:
        """
        Синхронизирует локальную папку с папкой на Яндекс.Диске
        """
        try:
            yandex_contents = self.get_yandex_folder_content(self.yandex_folder)
            yandex_files = {item["name"]: item for item in yandex_contents if item["type"] == "file"}

            local_files_set = set()
            for root, _, files in os.walk(self.local_folder):
                for filename in files:
                    local_file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(local_file_path, self.local_folder)
                    yandex_file_path = f"{self.yandex_folder}/{relative_path}"

                    logger.info(f"Проверяем файл '{filename}'...")

                    local_files_set.add(filename)

                    local_file_hash = self.yandex_disk.get_local_file_hash(local_file_path)
                    if local_file_hash is None:
                        continue
                    yandex_file_hash = yandex_files.get(filename, {}).get("md5") if filename in yandex_files else None

                    if yandex_file_hash == local_file_hash:
                        logger.info(f"Файл '{filename}' актуален.")
                    else:
                        if filename in yandex_files:
                            logger.info(f"Файл '{filename}' изменён. Загружаем обновлённую версию...")
                        else:
                            logger.info(f"Файл '{filename}' отсутствует на Яндекс.Диске. Загружаем...")
                        self.yandex_disk.reload(local_file_path, yandex_file_path)

            for yandex_file in yandex_files.values():
                if yandex_file["name"] not in local_files_set:
                    logger.info(f"Файл '{yandex_file['name']}' отсутствует локально. Удаляем с Яндекс.Диска...")
                    self.yandex_disk.delete(yandex_file["path"])

        except Exception as e:
            logger.error(f"Ошибка при синхронизации: {e}")
