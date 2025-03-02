from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QGridLayout
)
from PyQt5.QtGui import QFont, QIcon, QPalette, QBrush, QPixmap, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, QRect, QPoint, QUrl, pyqtSignal
from config_manager import get_config
from resource_manager import get_resource
from validation import validate_number
from parser import parse_directory
from analyzer import analyze_coverage
from map_window import MapWindow
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from visualizer import visualize_grid
from threading import Thread


class DirectoryWatcher(FileSystemEventHandler):
    """Класс для отслеживания новых файлов в директории."""

    def __init__(self, directory, callback):
        """
        Инициализирует DirectoryWatcher.

        :param directory: Директория для отслеживания.
        :param callback: Функция, которая будет вызвана при обнаружении нового файла.
        """
        self.directory = directory
        self.callback = callback

    def on_created(self, event):
        """Вызывается при создании нового файла."""
        if not event.is_directory:
            self.callback(event.src_path)  # Вызываем callback с путем к файлу


class GradientFrame(QFrame):
    """Кастомный QFrame"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)

    def paintEvent(self, event):
        """Переопределяем метод для отрисовки градиентного фона."""
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#6a11cb"))
        gradient.setColorAt(1, QColor("#2575fc"))
        painter.fillRect(self.rect(), QBrush(gradient))


class InputWindow(QMainWindow):
    # Сигнал для передачи событий из потока watchdog в основной поток
    new_file_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        # Получаем конфигурацию (она будет инициализирована автоматически, если ещё не инициализирована)
        self.config = get_config()

        # Устанавливаем иконку и заголовок
        self.setWindowTitle(self.config.get("Window", "title"))
        self.setWindowIcon(QIcon(get_resource("Window", "icon")))

        # Загрузка параметров окна из конфигурации
        window_width = self.config.get("Window", "width", default="1280")
        window_height = self.config.get("Window", "height", default="1024")
        min_width = self.config.get_int("Window", "min_width", default=800)
        min_height = self.config.get_int("Window", "min_height", default=850)

        self.setGeometry(100, 100, int(window_width), int(window_height))
        self.setMinimumSize(min_width, min_height)

        # Устанавливаем картинку как фон
        background_image = get_resource("Window", "background_image")
        self.set_background_image(background_image)

        # Устанавливаем стиль для главного окна
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);  /* Полупрозрачный белый фон */
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 20px;
            }
            QLabel {
                font-family: 'Roboto';
                font-size: 14px;
                color: #333333;
            }
            QLineEdit {
                font-family: 'Roboto';
                font-size: 14px;
                padding: 10px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QPushButton {
                font-family: 'Roboto';
                font-size: 14px;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                color: #ffffff;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #87CEEB, stop: 1 #90EE90);
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #6CA6CD, stop: 1 #7CCD7C);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #4A708B, stop: 1 #548B54);
            }
        """)

        # Главный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Заголовок
        title_label = QLabel(self.config.get("Messages", "title"))
        title_label.setFont(QFont("Roboto", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Карточка для ввода данных
        input_card = QFrame()
        input_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);  /* Полупрозрачный белый фон */
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 20px;
            }
        """)
        input_layout = QGridLayout(input_card)
        input_layout.setSpacing(15)
        input_layout.setContentsMargins(20, 20, 20, 20)

        # Устанавливаем растягивание колонок
        input_layout.setColumnStretch(0, 1)
        input_layout.setColumnStretch(1, 1)

        # Поля для ввода данных
        self.min_lat_entry = self.create_input_field(self.config.get("Messages", "min_lat"), "min_lat", self.get_range("latitude"))
        self.max_lat_entry = self.create_input_field(self.config.get("Messages", "max_lat"), "max_lat", self.get_range("latitude"))
        self.min_lon_entry = self.create_input_field(self.config.get("Messages", "min_lon"), "min_lon", self.get_range("longitude"))
        self.max_lon_entry = self.create_input_field(self.config.get("Messages", "max_lon"), "max_lon", self.get_range("longitude"))
        self.radius_entry = self.create_input_field(self.config.get("Messages", "radius"), "radius", validate_positive=True)

        input_layout.addWidget(self.min_lat_entry, 0, 0)
        input_layout.addWidget(self.max_lat_entry, 0, 1)
        input_layout.addWidget(self.min_lon_entry, 1, 0)
        input_layout.addWidget(self.max_lon_entry, 1, 1)
        input_layout.addWidget(self.radius_entry, 2, 0)

        # Поле для выбора директории
        dir_label = QLabel(self.config.get("Messages", "select_directory"))
        dir_label.setFont(QFont("Roboto", 12))
        input_layout.addWidget(dir_label, 3, 0, 1, 2)  # Подпись занимает две колонки

        dir_layout = QHBoxLayout()
        self.dir_entry = QLineEdit()
        self.dir_entry.setFont(QFont("Roboto", 12))
        self.dir_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dir_layout.addWidget(self.dir_entry)

        # Кнопка для выбора директории
        dir_button = QPushButton("Обзор")
        dir_button.setFont(QFont("Roboto", 12))
        dir_button.setIcon(QIcon("folder_icon.png"))
        dir_button.setIconSize(QSize(16, 16))
        dir_button.setToolTip(self.config.get("Messages", "select_directory"))
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(dir_button)

        input_layout.addLayout(dir_layout, 4, 0, 1, 2)
        layout.addWidget(input_card)

        # Кнопка "Запустить анализ"
        self.run_button = QPushButton(self.config.get("Messages", "run_analysis"))
        self.run_button.setFont(QFont("Roboto", 14, QFont.Bold))
        self.run_button.clicked.connect(self.run_analysis)
        layout.addWidget(self.run_button)

        # Таймер для обновления карты
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_map)

        # Переменные для хранения текущих параметров анализа
        self.current_min_lat = None
        self.current_max_lat = None
        self.current_min_lon = None
        self.current_max_lon = None
        self.current_radius = None
        self.current_directory = None
        self.map_window = None

        # Подключаем сигнал к слоту
        self.new_file_detected.connect(self.on_new_file)

    def set_background_image(self, image_path):
        """Устанавливает картинку как фон главного окна."""
        palette = self.palette()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            palette.setBrush(QPalette.Background, QBrush(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
            self.setPalette(palette)
        else:
            print(self.config.get("Error", "error_img_not_found") + image_path)

    def resizeEvent(self, event):
        """Переопределяем метод для изменения фона при изменении размера окна."""
        background_image = self.config.get("Window", "background_image")
        self.set_background_image(background_image)
        super().resizeEvent(event)

    def get_range(self, key):
        """Получает диапазон из config.ini."""
        range_str = self.config.get("Ranges", key, default="")
        return tuple(map(float, range_str.split(","))) if range_str else None

    def create_input_field(self, label_text, field_name, validate_range=None, validate_positive=False):
        """Создаёт поле для ввода данных с валидацией."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(5)

        label = QLabel(label_text)
        label.setFont(QFont("Roboto", 12))
        layout.addWidget(label)

        entry = QLineEdit()
        entry.setFont(QFont("Roboto", 12))
        entry.setMinimumHeight(40)  # Устанавливаем минимальную высоту поля ввода
        entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Поле растягивается по ширине
        layout.addWidget(entry)

        # Добавляем проверку при потере фокуса
        entry.editingFinished.connect(lambda: self.validate_on_focusout(entry, validate_range, validate_positive))
        return container

    def validate_on_focusout(self, entry, validate_range=None, validate_positive=False):
        """Проверяет данные при потере фокуса."""
        value = entry.text()
        error = validate_number(value, validate_range, validate_positive)

        if isinstance(error, str):
            entry.setStyleSheet("border: 1px solid red;")  # Подсвечиваем поле красным
            QMessageBox.critical(self, self.config.get("Error", "error"), error)  # Показываем ошибку в QMessageBox
        else:
            entry.setStyleSheet("")  # Убираем подсветку

    def select_directory(self):
        """Открывает диалог выбора директории."""
        directory = QFileDialog.getExistingDirectory(self, self.config.get("Messages", "select_directory"))
        if directory:
            self.dir_entry.setText(directory)

    def run_analysis(self):
        """Запускает анализ и визуализацию после проверки данных."""
        try:
            # Получаем данные из полей ввода
            min_lat = self.min_lat_entry.findChild(QLineEdit).text().strip()
            max_lat = self.max_lat_entry.findChild(QLineEdit).text().strip()
            min_lon = self.min_lon_entry.findChild(QLineEdit).text().strip()
            max_lon = self.max_lon_entry.findChild(QLineEdit).text().strip()
            radius_in_meters = self.radius_entry.findChild(QLineEdit).text().strip()
            directory = self.dir_entry.text().strip()

            # Функция для проверки и вывода ошибок
            def check_and_set_error(entry, value, validate_range=None, validate_positive=False, custom_error=None):
                if not value or not validate_number(value, validate_range, validate_positive):
                    error_message = custom_error or self.config.get("Error", "error_invalid_number")
                    entry.setStyleSheet("border: 1px solid red;")
                    QMessageBox.critical(self, self.config.get("Error", "error"), error_message)
                    return False
                return True

            # Проверяем каждое поле
            is_valid = (
                check_and_set_error(self.min_lat_entry.findChild(QLineEdit), min_lat, validate_range=self.get_range("latitude"), custom_error=self.config.get("Error", "error_latitude_range")) and
                check_and_set_error(self.max_lat_entry.findChild(QLineEdit), max_lat, validate_range=self.get_range("latitude"), custom_error=self.config.get("Error", "error_latitude_range")) and
                check_and_set_error(self.min_lon_entry.findChild(QLineEdit), min_lon, validate_range=self.get_range("longitude"), custom_error=self.config.get("Error", "error_longitude_range")) and
                check_and_set_error(self.max_lon_entry.findChild(QLineEdit), max_lon, validate_range=self.get_range("longitude"), custom_error=self.config.get("Error", "error_longitude_range")) and
                check_and_set_error(self.radius_entry.findChild(QLineEdit), radius_in_meters, validate_positive=True, custom_error=self.config.get("Error", "error_positive_number")) and
                bool(directory)
            )

            if not is_valid:
                return  # Прерываем выполнение, если есть ошибки

            # Преобразуем данные в числа
            self.current_min_lat = float(min_lat)
            self.current_max_lat = float(max_lat)
            self.current_min_lon = float(min_lon)
            self.current_max_lon = float(max_lon)
            self.current_radius = float(radius_in_meters)
            self.current_directory = directory

            # Дополнительные проверки
            if self.current_min_lat >= self.current_max_lat:
                QMessageBox.critical(self, self.config.get("Error", "error"), self.config.get("Error", "error_min_max_lat"))
                return
            if self.current_min_lon >= self.current_max_lon:
                QMessageBox.critical(self, self.config.get("Error", "error"), self.config.get("Error", "error_min_max_lon"))
                return

            # Выполняем анализ
            data = parse_directory(directory)
            grid, _, _ = analyze_coverage(data, self.current_min_lat, self.current_max_lat, self.current_min_lon, self.current_max_lon, self.current_radius)

            # Визуализируем сетку
            self.map_window = MapWindow(grid, self.current_min_lat, self.current_max_lat, self.current_min_lon, self.current_max_lon)
            self.map_window.show()

            # Запускаем наблюдатель за директорией
            self.start_directory_watcher(directory)

        except ValueError as e:
            QMessageBox.critical(self, self.config.get("Error", "error"), str(e))
        except Exception as e:
            QMessageBox.critical(self, self.config.get("Error", "error_unknown"), str(e))

    def start_directory_watcher(self, directory):
        """Запускает наблюдатель за директорией."""
        event_handler = DirectoryWatcher(directory, self.handle_new_file)
        self.observer = Observer()
        self.observer.schedule(event_handler, directory, recursive=False)
        self.observer.start()

    def handle_new_file(self, file_path):
        """Обрабатывает новый файл в потоке watchdog и передает событие в основной поток."""
        self.new_file_detected.emit(file_path)  # Используем сигнал для передачи данных

    def on_new_file(self, file_path):
        """Обрабатывает появление нового файла в основном потоке."""
        print(f"New file detected: {file_path}")
        # Запускаем таймер для обновления карты через 1 секунду
        self.update_timer.start(1000)

    def update_map(self):
        """Обновляет карту при появлении новых данных."""
        self.update_timer.stop()

        try:
            # Перезапускаем анализ с текущими параметрами
            data = parse_directory(self.current_directory)
            grid, _, _ = analyze_coverage(data, self.current_min_lat, self.current_max_lat, self.current_min_lon, self.current_max_lon, self.current_radius)

            # Обновляем карту
            self.map_window.browser.setUrl(QUrl.fromLocalFile(visualize_grid(grid, self.current_min_lat, self.current_max_lat, self.current_min_lon, self.current_max_lon)))
        except Exception as e:
            print(self.config.get("Error", "error_map_update") + e)

    def closeEvent(self, event):
        """Останавливает наблюдатель при закрытии окна."""
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        super().closeEvent(event)