import requests
import hashlib
from typing import Optional
from logger import setup_logger

logger = setup_logger(__name__)


class YandexDisk:
    def __init__(self, token: str, yandex_folder: str):
        self.token = token
        self.yandex_folder = yandex_folder
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {"Authorization": f"OAuth {self.token}"}

    def check_or_create_yandex_folder(self) -> bool:
        try:
            params = {"path": self.yandex_folder}
            response = requests.get(self.base_url, headers=self.headers, params=params)

            if response.status_code == 200:
                logger.info(f"Папка {self.yandex_folder} уже создана на Яндекс.Диске.")
                return True
            elif response.status_code == 404:
                response_put = requests.put(self.base_url, headers=self.headers, params=params)
                if response_put.status_code == 201:
                    logger.info(f"Папка {self.yandex_folder} успешно создана на Яндекс.Диске")
                    return True
                else:
                    logger.error(f"Ошибка при создании папки: {response_put.status_code} {response_put.text}")
            else:
                logger.error(f"Ошибка при проверке папки: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с Яндекс.Диском: {e}")
        return False

    def upload(self, local_path: str, yandex_path: str) -> bool:
        try:
            params = {"path": yandex_path, "overwrite": "true"}
            response = requests.get(f"{self.base_url}/upload", headers=self.headers, params=params)
            if response.status_code == 200:
                upload_url = response.json().get("href")
            else:
                logger.error(f"Ошибка при получении URL для загрузки: {response.status_code} {response.text}")
                return False
            try:
                with open(local_path, "rb") as file:
                    upload_response = requests.put(upload_url, files={"file": file})
                    if upload_response.status_code == 201:
                        logger.info(f"Файл {local_path} успешно загружен на Яндекс.Диск")
                        return True
                    else:
                        logger.error(f"Ошибка при загрузке файла: {upload_response.status_code}, {upload_response.text}")
            except FileNotFoundError:
                logger.error(f"Файл '{local_path}' не найден. Пропускаем.")
            except IOError as e:
                logger.error(f"Ошибка чтения файла '{local_path}': {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с Яндекс.Диском: {e}")
        return False

    @staticmethod
    def get_local_file_hash(local_file_path: str) -> Optional[str]:
        hash_md5 = hashlib.md5()
        try:
            with open(local_file_path, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_md5.update(chunk)
                return hash_md5.hexdigest()
        except FileNotFoundError:
            logger.error(f"Файл '{local_file_path}' не найден.")
        except IOError as e:
            logger.error(f"Ошибка чтения файла '{local_file_path}': {e}")
        return None

    def get_yandex_file_hash(self, yandex_file_path: str) -> Optional[str]:
        try:
            params = {"path": yandex_file_path}
            response = requests.get(self.base_url, headers=self.headers, params=params)

            if response.status_code == 200:
                file_info = response.json()
                return file_info.get("md5")
            elif response.status_code == 404:
                logger.error(f"Файл '{yandex_file_path}' не найден на Яндекс.Диске.")
            else:
                logger.error(f"Ошибка при получении хэша файла с Яндекс.Диска: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с Яндекс.Диском: {e}")
        return None

    def reload(self, local_path: str, yandex_path: str) -> bool:
        local_file_hash = self.get_local_file_hash(local_path)
        if local_file_hash is None:
            return False

        yandex_file_hash = self.get_yandex_file_hash(yandex_path)
        if yandex_file_hash is None or yandex_file_hash != local_file_hash:
            logger.info(f"Перезаписываем файл '{yandex_path}' на Яндекс.Диске.")
            return self.upload(local_path, yandex_path)
        else:
            logger.info(f"Файл '{yandex_path}' на Яндекс.Диске уже актуален.")
            return True

    def delete(self, yandex_file_path: str) -> bool:
        try:
            params = {"path": yandex_file_path}
            response = requests.delete(self.base_url, headers=self.headers, params=params)
            if response.status_code == 204:
                logger.info(f"Файл '{yandex_file_path}' успешно удалён с Яндекс.Диска.")
                return True
            else:
                logger.error(f"Ошибка при удалении файла '{yandex_file_path}': {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с Яндекс.Диском: {e}")
        return False
