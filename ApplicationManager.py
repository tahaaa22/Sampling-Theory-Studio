from PyQt5 import QtCore
class ApplicationManager:
    def __init__(self, ui_window):
        self.ui_window = ui_window

    def load_signal(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui_window.Load_Button.setText(_translate("MainWindow", "    YAAAY"))
