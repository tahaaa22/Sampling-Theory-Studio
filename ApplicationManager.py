from PyQt5.QtWidgets import QFileDialog
import wfdb, numpy as np, math, random
import SignalClass
class ApplicationManager:
    def __init__(self, ui_window, load_graph_1, load_graph_2, load_graph_3, compose_graph_1, compose_graph_2, compose_graph_3):
        # Graph Numbers Guide   1 -> Original -----  2 -> Reconstructed ----- 3 -> Difference
        self.ui_window = ui_window
        self.load_graph_1 = load_graph_1
        self.load_graph_2 = load_graph_2
        self.load_graph_3 = load_graph_3
        self.compose_graph_1 = compose_graph_1
        self.compose_graph_2 = compose_graph_2
        self.compose_graph_3 = compose_graph_3
        self.main_signal = None
        self.noisy_signal = None
        self.component_count = 1

    def load_signal(self):
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            Record = wfdb.rdrecord(File_Path[:-4])
            Y_Coordinates = list(Record.p_signal[:1000, 0])
            X_Coordinates = list(np.arange(len(Y_Coordinates)))
            self.main_signal = SignalClass.Signal(X_Coordinates, Y_Coordinates, 'r')


            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen = 'b')


    def add_noise(self, SNR_value):
        signal_power = sum(y ** 2 for y in self.main_signal.Y_Coordinates) / len(self.main_signal.Y_Coordinates)
        noise_power = signal_power / (10**(SNR_value / 10))
        noise_std = math.sqrt(noise_power)
        noise = [random.gauss(0, noise_std) for _ in range(len(self.main_signal.Y_Coordinates))]
        self.noisy_signal = SignalClass.Signal(self.main_signal.X_Coordinates, [s + n for s, n in zip(self.main_signal.Y_Coordinates, noise)])
        self.load_graph_2.clear()
        self.load_graph_2.plot(self.noisy_signal.X_Coordinates, self.noisy_signal.Y_Coordinates, pen = 'r')

    def add_component(self):
        
        self.component_count += 1
        Temporary_String = f"Component {self.component_count}"
        self.ui_window.Compose_Components_ComboBox.addItem(Temporary_String)

    def remove_component(self):

        self.component_count -= 1
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        if selected_index == self.ui_window.Compose_Components_ComboBox.count() - 1:
            self.ui_window.Compose_Components_ComboBox.removeItem(selected_index)
        else:
            self.ui_window.Compose_Components_ComboBox.removeItem(selected_index)
            for index in range(self.ui_window.Compose_Components_ComboBox.count()):
                if self.ui_window.Compose_Components_ComboBox.itemText(index)[-1] != index + 1:
                    self.ui_window.Compose_Components_ComboBox.setItemText(index, f"Component {index+1}")

    def compose_signal(self):

        magnitude_1 = self.ui_window.Compose_Signal_Magnitude_Slider.value()
        frequency_1 = self.ui_window.Compose_Signal_Frequency_Slider.value()

        t = np.linspace(0, 1, 500)
        signal = magnitude_1 * np.sin(2 * np.pi * frequency_1 * t)

        self.compose_graph_1.clear()
        self.compose_graph_1.plot(t, signal, pen='g')