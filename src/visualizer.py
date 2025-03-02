import plotly.graph_objects as go
import tempfile
import os


def visualize_grid(grid, min_lat, max_lat, min_lon, max_lon):
    """
    Визуализирует сетку с пройденными и пропущенными участками.
    :param grid: Сетка из analyzer.py.
    :param min_lat, max_lat, min_lon, max_lon: Границы участка.
    :return: Путь к сохраненному HTML-файлу.
    """
    # Размер сетки
    grid_size_lat, grid_size_lon = grid.shape

    # Шаг сетки
    lat_step = (max_lat - min_lat) / grid_size_lat
    lon_step = (max_lon - min_lon) / grid_size_lon

    # Создаем фигуру
    fig = go.Figure()

    # Рисуем ячейки
    for i in range(grid_size_lat):
        for j in range(grid_size_lon):
            # Координаты углов ячейки
            x = [min_lon + j * lon_step, min_lon + (j + 1) * lon_step, min_lon + (j + 1) * lon_step, min_lon + j * lon_step, min_lon + j * lon_step]
            y = [min_lat + i * lat_step, min_lat + i * lat_step, min_lat + (i + 1) * lat_step, min_lat + (i + 1) * lat_step, min_lat + i * lat_step]

            # Цвет ячейки (зеленый - пройдена, красный - не пройдена)
            color = 'rgba(0, 255, 0, 0.5)' if grid[i, j] == 1 else 'rgba(255, 0, 0, 0.5)'

            # Добавляем ячейку
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                fill='toself',
                fillcolor=color,
                line=dict(color='white', width=2),  # Белые границы
                hoverinfo='text',
                text=f"Широта: {min_lat + (i + 0.5) * lat_step:.6f}<br>Долгота: {min_lon + (j + 0.5) * lon_step:.6f}<br>Статус: {'Пройдено' if grid[i, j] == 1 else 'Не пройдено'}"
            ))

    # Настраиваем макет
    fig.update_layout(
        title=None,
        xaxis_title="Долгота",
        yaxis_title="Широта",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(range=[min_lon, max_lon], scaleanchor='y', scaleratio=1),
        yaxis=dict(range=[min_lat, max_lat]),
        margin=dict(l=0, r=0, t=40, b=0),  # Убираем отступы
        autosize=True,  # Автоматически растягиваем график
        width=None,  # Ширина графика будет занимать всю доступную область
        height=None,  # Высота графика будет занимать всю доступную область
        plot_bgcolor='rgba(240, 240, 240, 1)',  # Светло-серый фон
        paper_bgcolor='rgba(240, 240, 240, 1)',  # Светло-серый фон вокруг графика
    )

    # Сохраняем график в HTML-файл
    html_file = os.path.join(tempfile.gettempdir(), "plotly_graph.html")
    fig.write_html(html_file)

    return html_file