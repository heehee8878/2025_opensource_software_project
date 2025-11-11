import sys
from PyQt5.QtWidgets import QApplication
from editor_window import EditorWindow

def main():
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()