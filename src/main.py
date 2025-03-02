import sys
from PyQt5.QtWidgets import QApplication
from input_window import InputWindow

def main():
    app = QApplication(sys.argv)
    input_window = InputWindow()
    input_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()