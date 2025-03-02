import os
import sys
import configparser

def get_resource_path(relative_path):
    """Получает абсолютный путь к ресурсу."""
    # Если программа запущена из исполняемого файла
    if getattr(sys, 'frozen', False):
        # Путь к временной директории PyInstaller
        base_path = sys._MEIPASS
    else:
        # Путь к текущей директории (корень проекта)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Полный путь к ресурсу
    return os.path.join(base_path, relative_path)

class ConfigManager:
    """Класс для управления конфигурацией приложения."""

    def __init__(self, config_path):
        """Инициализирует ConfigManager с указанным путем к config.ini."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')

    def get(self, section, key, default=None):
        """
        Получает значение параметра из указанной секции.

        :param section: Название секции в конфигурационном файле.
        :param key: Название параметра.
        :param default: Значение по умолчанию, если параметр не найден.
        :return: Значение параметра или значение по умолчанию.
        """
        try:
            value = self.config[section][key]
            return self._clean_value(value)  # Очищаем значение от внешних кавычек
        except KeyError:
            return default  # Возвращаем значение по умолчанию

    def get_int(self, section, key, default=0):
        """Получает целочисленное значение параметра."""
        value = self.get(section, key)
        return int(value) if value else default

    def get_float(self, section, key, default=0.0):
        """Получает вещественное значение параметра."""
        value = self.get(section, key)
        return float(value) if value else default

    def get_boolean(self, section, key, default=False):
        """Получает логическое значение параметра."""
        value = self.get(section, key)
        return self.config.getboolean(section, key, fallback=default)

    @staticmethod
    def _clean_value(value):
        """
        Удаляет внешние кавычки из строки.

        :param value: Исходное значение.
        :return: Очищенное значение.
        """
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            return value.strip('"')  # Удаляем внешние кавычки
        return value

    @staticmethod
    def get_default_config_path():
        """Возвращает путь к конфигурационному файлу по умолчанию."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "..", "config.ini")


# Глобальный экземпляр менеджера конфигурации
config_manager = None


def initialize_config():
    """Инициализирует конфигурацию."""
    global config_manager  # Указываем, что используем глобальную переменную
    config_path = get_resource_path("config.ini")
    config_manager = ConfigManager(config_path)  # Обновляем глобальную переменную
    return config_manager


def get_config():
    """
    Возвращает глобальный экземпляр менеджера конфигурации.

    :return: Экземпляр ConfigManager.
    """
    global config_manager
    if config_manager is None:
        # Инициализируем конфигурацию, если она ещё не инициализирована
        initialize_config()
    return config_manager