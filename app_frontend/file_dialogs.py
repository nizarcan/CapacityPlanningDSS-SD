import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon


class FileDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480

    def init_ui(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.open_file()
        self.open_files_list()
        self.save_path()

        # self.show()

    def open_file(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "",
                                                  "All Files (*);;Python Files (*.py)", options = options)
        if fileName:
            print(fileName)

    def open_files_list(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Dosyalar Seç", "",
                                                "All Files (*);;Python Files (*.py)", options = options)
        if files:
            print(files)

    def save_path(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Kaydet", "",
                                                  "All Files (*);;Text Files (*.txt)", options = options)
        if fileName:
            print(fileName)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileDialog()
    ex.save_path()
    sys.exit(app.exec_())