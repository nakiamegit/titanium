from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from visualizer import visualize_grid


class MapWindow(QMainWindow):
    def __init__(self, grid, min_lat, max_lat, min_lon, max_lon):
        super().__init__()
        self.setWindowTitle("Визуализация анализа")
        self.setGeometry(100, 100, 1280, 1024)

        # Визуализируем сетку и получаем путь к HTML-файлу
        self.html_file = visualize_grid(grid, min_lat, max_lat, min_lon, max_lon)

        # Создаем QWebEngineView
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(self.html_file))

        # Устанавливаем браузер в главное окно
        self.setCentralWidget(self.browser)