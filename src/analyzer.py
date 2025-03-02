import numpy as np
from math import radians, cos

def analyze_coverage(data, min_lat, max_lat, min_lon, max_lon, radius_in_meters):
    """
    Анализирует координаты и формирует сетку с пройденными и пропущенными участками.
    :param data: Список координат из parser.py.
    :param min_lat, max_lat, min_lon, max_lon: Границы участка.
    :param radius_in_meters: Радиус действия металлоискателя в метрах.
    :return: Сетка (numpy array), где 1 - пройдено, 0 - не пройдено.
    """
    # Переводим радиус из метров в градусы
    radius_in_degrees = radius_in_meters / 111320

    # Средняя широта для перевода радиуса по долготе
    avg_lat = radians((min_lat + max_lat) / 2)

    # Размер ячейки в градусах (примерно равен радиусу действия)
    cell_size_lat = radius_in_degrees
    cell_size_lon = radius_in_degrees / cos(avg_lat)

    # Количество ячеек по широте и долготе
    grid_size_lat = int((max_lat - min_lat) / cell_size_lat)
    grid_size_lon = int((max_lon - min_lon) / cell_size_lon)

    # Создаем сетку
    grid = np.zeros((grid_size_lat, grid_size_lon))

    # Шаг сетки
    lat_step = (max_lat - min_lat) / grid_size_lat
    lon_step = (max_lon - min_lon) / grid_size_lon

    # Проверяем покрытие каждой ячейки
    for i in range(grid_size_lat):
        for j in range(grid_size_lon):
            cell_lat = min_lat + i * lat_step
            cell_lon = min_lon + j * lon_step
            # Проверяем, есть ли точки в радиусе detector_radius
            for point in data:
                if abs(point[0] - cell_lat) <= radius_in_degrees and abs(point[1] - cell_lon) <= radius_in_degrees / cos(radians(cell_lat)):
                    grid[i, j] = 1  # Ячейка пройдена
                    break

    return grid, grid_size_lat, grid_size_lon