import os
import sys
import configparser

def get_resource_path(relative_path):
    """
    Возвращает абсолютный путь к ресурсу.

    :param relative_path: Относительный путь к ресурсу.
    :return: Абсолютный путь к ресурсу.
    """
    if getattr(sys, 'frozen', False):
        # Путь к временной директории PyInstaller
        base_path = sys._MEIPASS
    else:
        # Путь к текущей директории (корень проекта)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

def load_config(config_name="config.ini"):
    """
    Загружает конфигурационный файл.

    :param config_name: Имя конфигурационного файла (по умолчанию "config.ini").
    :return: Экземпляр ConfigParser с загруженным конфигом.
    """
    config_path = get_resource_path(config_name)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
    
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    return config

def get_resource_from_config(config, section, key, default=None):
    """
    Получает путь к ресурсу из конфигурационного файла.
    """
    try:
        relative_path = config[section][key]
        relative_path = _clean_value(relative_path)  # Очищаем значение от кавычек
        return get_resource_path(relative_path)
    except KeyError:
        return default

def _clean_value(value):
    """
    Удаляет внешние кавычки из строки.
    """
    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
        return value.strip('"')  # Удаляем внешние кавычки
    return value

# Глобальный экземпляр конфигурации
_config = None

def initialize_config(config_name="config.ini"):
    """
    Инициализирует конфигурацию.

    :param config_name: Имя конфигурационного файла (по умолчанию "config.ini").
    :return: Экземпляр ConfigParser.
    """
    global _config
    _config = load_config(config_name)
    return _config

def get_config():
    """
    Возвращает глобальный экземпляр конфигурации.

    :return: Экземпляр ConfigParser.
    """
    if _config is None:
        initialize_config()
    return _config

def get_resource(section, key, default=None):
    """
    Универсальная функция для получения пути к ресурсу.

    :param section: Секция в конфигурационном файле.
    :param key: Ключ в секции.
    :param default: Значение по умолчанию, если ключ не найден.
    :return: Абсолютный путь к ресурсу.
    """
    config = get_config()
    return get_resource_from_config(config, section, key, default)