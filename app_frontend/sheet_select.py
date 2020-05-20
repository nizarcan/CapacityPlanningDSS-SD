from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class SheetSelect(object):
    def __init__(self):
        self.sayfa_listesi = None
        self.onay_butonu = None
        self.bottom_gradient = None
        self.top_gradient = None
        self.soru = None

    def init_ui(self, Form, l):
        Form.setObjectName("Form")
        Form.resize(372, 182)
        Form.setStyleSheet("background: #c5c1bb;")
        self.sayfa_listesi = QtWidgets.QComboBox(Form)
        self.sayfa_listesi.setGeometry(QtCore.QRect(40, 60, 291, 22))
        self.sayfa_listesi.setStyleSheet("background: rgb(222, 222, 222);")
        self.sayfa_listesi.setObjectName("sayfa_listesi")
        self.sayfa_listesi.addItems(l)
        self.onay_butonu = QtWidgets.QPushButton(Form)
        self.onay_butonu.setGeometry(QtCore.QRect(40, 100, 291, 51))
        self.onay_butonu.setStyleSheet("background: #eff0eb;\n"
                                       "border-style: outset;\n"
                                       "border-width: 2px;\n"
                                       "border-radius: 20px;\n"
                                       "border-color: beige;\n"
                                       "font: bold 12px;\n"
                                       "min-width: 10em;\n"
                                       "padding: 6px;")
        self.onay_butonu.setObjectName("onay_butonu")
        self.onay_butonu.clicked.connect(self.fetch_selection)
        self.bottom_gradient = QtWidgets.QFrame(Form)
        self.bottom_gradient.setGeometry(QtCore.QRect(0, 160, 371, 21))
        self.bottom_gradient.setStyleSheet(
            "background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(72, 78, 74, 255), stop:1 rgba(197, 193, 187, 255));")
        self.bottom_gradient.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.bottom_gradient.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bottom_gradient.setObjectName("bottom_gradient")
        self.top_gradient = QtWidgets.QFrame(Form)
        self.top_gradient.setGeometry(QtCore.QRect(0, 0, 371, 21))
        self.top_gradient.setStyleSheet(
            "background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(197, 193, 187, 255), stop:1 rgba(72, 78, 74, 255));")
        self.top_gradient.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.top_gradient.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_gradient.setObjectName("top_gradient")
        self.soru = QtWidgets.QLabel(Form)
        self.soru.setGeometry(QtCore.QRect(0, 30, 371, 20))
        self.soru.setStyleSheet("font: bold 14px;")
        self.soru.setObjectName("soru")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        # self.sayfa_listesi.setItemText(0, _translate("Form", "ListItem1"))
        # self.sayfa_listesi.setItemText(1, _translate("Form", "ListItem2"))
        self.onay_butonu.setText(_translate("Form", "Sayfayı Seç"))
        self.soru.setText(_translate("Form",
                                     "<html><head/><body><p align=\"center\"><span style=\" font-size:11pt;\">Eklemek İstediğiniz İçerik Hangi Sayfada?</span></p></body></html>"))

    def fetch_selection(self):
        print(self.sayfa_listesi.currentText())


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = SheetSelect()
    ui.init_ui(Form, ["a", "b", "c"])
    Form.show()
    app.exec_()
    Form.close()
    # sys.exit(app.exec_())
    print("heyo")
