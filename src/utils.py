import tkinter as tk

def copy_text(widget, event=None):
    """Копирует текст из поля ввода."""
    widget.event_generate("<<Copy>>")
    return "break"


def paste_text(widget, event=None):
    """Вставляет текст в поле ввода."""
    widget.event_generate("<<Paste>>")
    return "break"


def select_all_text(widget, event=None):
    """Выделяет весь текст в поле ввода."""
    widget.event_generate("<<SelectAll>>")
    return "break"


def show_context_menu(root, event):
    """Показывает контекстное меню для копирования/вставки."""
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Копировать", command=lambda: copy_text(event.widget))
    menu.add_command(label="Вставить", command=lambda: paste_text(event.widget))
    menu.add_command(label="Выделить всё", command=lambda: select_all_text(event.widget))
    menu.post(event.x_root, event.y_root)