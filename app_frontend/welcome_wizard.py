from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class WelcomeWizard(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(641, 382)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("background: #c5c1bb;")
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(0, 0, 641, 71))
        self.frame.setStyleSheet("background: #484e4a;")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 20, 201, 31))
        self.label.setObjectName("label")
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setGeometry(QtCore.QRect(490, 10, 141, 41))
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap(":/logo/resources/tc_mango_logo.png"))
        self.label_6.setScaledContents(True)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 110, 361, 61))
        self.pushButton_2.setStyleSheet("background: #eff0eb;\n"
                                        "border-style: outset;\n"
                                        "border-width: 2px;\n"
                                        "border-radius: 30px;\n"
                                        "border-color: beige;\n"
                                        "font: bold 12px;\n"
                                        "min-width: 10em;\n"
                                        "padding: 6px;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(270, 190, 361, 61))
        self.pushButton_3.setStyleSheet("background: #eff0eb;\n"
                                        "border-style: outset;\n"
                                        "border-width: 2px;\n"
                                        "border-radius: 30px;\n"
                                        "border-color: beige;\n"
                                        "font: bold 12px;\n"
                                        "min-width: 10em;\n"
                                        "padding: 6px;")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(270, 270, 361, 61))
        self.pushButton_4.setStyleSheet("background: #eff0eb;\n"
                                        "border-style: outset;\n"
                                        "border-width: 2px;\n"
                                        "border-radius: 30px;\n"
                                        "border-color: beige;\n"
                                        "font: bold 12px;\n"
                                        "min-width: 10em;\n"
                                        "padding: 6px;")
        self.pushButton_4.setObjectName("pushButton_4")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(250, 70, 20, 271))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(270, 80, 361, 16))
        self.label_2.setStyleSheet("font: bold 14px;")
        self.label_2.setObjectName("label_2")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(10, 210, 241, 121))
        self.pushButton_5.setStyleSheet("background: #eff0eb;\n"
                                        "border-style: outset;\n"
                                        "border-width: 2px;\n"
                                        "border-radius: 10px;\n"
                                        "border-color: beige;\n"
                                        "font: bold 12px;\n"
                                        "min-width: 10em;\n"
                                        "padding: 6px;")
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(10, 80, 241, 121))
        self.pushButton_6.setStyleSheet("background: #eff0eb;\n"
                                        "border-style: outset;\n"
                                        "border-width: 2px;\n"
                                        "border-radius: 10px;\n"
                                        "border-color: beige;\n"
                                        "font: bold 12px;\n"
                                        "min-width: 10em;\n"
                                        "padding: 6px;")
        self.pushButton_6.setObjectName("pushButton_6")
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setGeometry(QtCore.QRect(0, 340, 641, 21))
        self.frame_3.setStyleSheet(
            "background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(72, 78, 74, 255), stop:1 rgba(197, 193, 187, 255));")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.pushButton_2.raise_()
        self.pushButton_3.raise_()
        self.pushButton_4.raise_()
        self.line.raise_()
        self.frame.raise_()
        self.label_2.raise_()
        self.pushButton_5.raise_()
        self.pushButton_6.raise_()
        self.frame_3.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 641, 21))
        self.menubar.setObjectName("menubar")
        self.menuDosya = QtWidgets.QMenu(self.menubar)
        self.menuDosya.setObjectName("menuDosya")
        self.menuAnal_z = QtWidgets.QMenu(self.menubar)
        self.menuAnal_z.setObjectName("menuAnal_z")
        self.menuHakk_nda = QtWidgets.QMenu(self.menubar)
        self.menuHakk_nda.setObjectName("menuHakk_nda")
        MainWindow.setMenuBar(self.menubar)
        self.actionTKPM = QtWidgets.QAction(MainWindow)
        self.actionTKPM.setObjectName("actionTKPM")
        self.actionOKPM = QtWidgets.QAction(MainWindow)
        self.actionOKPM.setObjectName("actionOKPM")
        self.actionOKPB = QtWidgets.QAction(MainWindow)
        self.actionOKPB.setObjectName("actionOKPB")
        self.actionAr_iv_A = QtWidgets.QAction(MainWindow)
        self.actionAr_iv_A.setObjectName("actionAr_iv_A")
        self.actionAr_iv_A_2 = QtWidgets.QAction(MainWindow)
        self.actionAr_iv_A_2.setObjectName("actionAr_iv_A_2")
        self.action_k = QtWidgets.QAction(MainWindow)
        self.action_k.setObjectName("action_k")
        self.actionTC_MANGO = QtWidgets.QAction(MainWindow)
        self.actionTC_MANGO.setObjectName("actionTC_MANGO")
        self.menuDosya.addAction(self.actionAr_iv_A)
        self.menuDosya.addAction(self.actionAr_iv_A_2)
        self.menuDosya.addAction(self.action_k)
        self.menuAnal_z.addAction(self.actionTKPM)
        self.menuAnal_z.addAction(self.actionOKPM)
        self.menuAnal_z.addAction(self.actionOKPB)
        self.menuHakk_nda.addAction(self.actionTC_MANGO)
        self.menubar.addAction(self.menuDosya.menuAction())
        self.menubar.addAction(self.menuAnal_z.menuAction())
        self.menubar.addAction(self.menuHakk_nda.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow",
                                      "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600; color:#ffffff;\">Kapasite Planlama KDS</span></p></body></html>"))
        self.pushButton_2.setText(_translate("MainWindow", "Taktiksel Seviyede Kaynak Planlama Modeli"))
        self.pushButton_3.setText(_translate("MainWindow", "Operasyonel Seviyede Kapasite Planlama Modeli"))
        self.pushButton_4.setText(_translate("MainWindow", "Operasyonel Seviyede Kapasite Benzetim Modeli"))
        self.label_2.setText(_translate("MainWindow",
                                        "<html><head/><body><p align=\"center\"><span style=\" font-size:11pt;\">ÇIKTI ANALİZİ</span></p></body></html>"))
        self.pushButton_5.setText(_translate("MainWindow", "Arşivi Geri Yükle"))
        self.pushButton_6.setText(_translate("MainWindow", "Yeni Arşiv Oluştur"))
        self.menuDosya.setTitle(_translate("MainWindow", "Dosya"))
        self.menuAnal_z.setTitle(_translate("MainWindow", "Analız"))
        self.menuHakk_nda.setTitle(_translate("MainWindow", "Hakkında"))
        self.actionTKPM.setText(_translate("MainWindow", "TKPM"))
        self.actionOKPM.setText(_translate("MainWindow", "OKPM"))
        self.actionOKPB.setText(_translate("MainWindow", "OKPB"))
        self.actionAr_iv_A.setText(_translate("MainWindow", "Yeni Arşiv"))
        self.actionAr_iv_A_2.setText(_translate("MainWindow", "Arşiv Aç"))
        self.action_k.setText(_translate("MainWindow", "Çıkış"))
        self.actionTC_MANGO.setText(_translate("MainWindow", "TC MANGO"))


# import new_resource_pack_rc

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = WelcomeWizard()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
