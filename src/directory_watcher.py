from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DirectoryWatcher(FileSystemEventHandler):
    """Класс для отслеживания новых файлов в директории."""
    def __init__(self, directory, callback):
        self.directory = directory
        self.callback = callback

    def on_created(self, event):
        """Вызывается при создании нового файла."""
        if not event.is_directory:
            self.callback(event.src_path)