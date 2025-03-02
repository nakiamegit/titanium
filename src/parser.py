import os
import re
from config_manager import get_config
#from geopy.distance import geodesic


def parse_dms_to_decimal(dms_str):
    """
    Преобразует координаты из формата DMS (градусы, минуты, секунды) в десятичный формат.
    :param dms_str: Строка с координатами в формате "XX град YY.ZZZZZ мин СШ/ВД".
    :return: Координата в десятичном формате.
    """
    # Регулярное выражение для разбора строки DMS
    match = re.search(r"(\d+)\s+град\s+(\d+\.\d+)\s+мин\s+([СШЮЗВД]{1,2})", dms_str)
    if not match:
        raise ValueError(get_config().get("Error", "error_invalid_dms_format").format(dms_str=dms_str))
    
    degrees = float(match.group(1))  # Градусы
    minutes = float(match.group(2))  # Минуты
    direction = match.group(3).strip()  # Направление (СШ, ЮШ, ВД, ЗД)
    
    # Конвертация в десятичный формат
    decimal_degrees = degrees + minutes / 60
    
    # Если направление указывает на юг или запад, значение должно быть отрицательным
    if direction in ["ЮШ", "ЗД"]:
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

def parse_file(file_path):
    """Парсит один файл и извлекает координаты."""
    data = []
    delimiter = get_config().get("File", "delimiter")

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split(delimiter)
            if len(parts) < 5 or not parts[3].strip() or not parts[4].strip():
                continue  # Пропускаем строки без координат
            
            lat_str = parts[3].strip()
            lon_str = parts[4].strip()

            try:
                lat = parse_dms_to_decimal(lat_str)
                lon = parse_dms_to_decimal(lon_str)
                data.append((lat, lon))
            except ValueError:
                continue  # Пропускаем невалидные координаты
    
    return data

def parse_directory(directory):
    """Парсит все файлы из директории."""
    data = []
    file_extension = get_config().get("File", "file_extension")

    if not os.path.exists(directory):
        raise FileNotFoundError(get_config().get("Error", "error_directory_not_found").format(directory=directory))
    
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            filepath = os.path.join(directory, filename)
            data.extend(parse_file(filepath))
    
    return data