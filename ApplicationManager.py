from PyQt5.QtWidgets import QFileDialog
import wfdb, numpy as np
import SignalClass
class ApplicationManager:
    def __init__(self, ui_window):
        self.ui_window = ui_window

    @staticmethod
    def load_signal():
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            Record = wfdb.rdrecord(File_Path[:-4])
            Y_Coordinates = list(Record.p_signal[:, 0])
            X_Coordinates = list(np.arange(len(Y_Coordinates)))
            chosen_signal = SignalClass.Signal('r', X_Coordinates, Y_Coordinates)
