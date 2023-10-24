from PyQt5.QtWidgets import QFileDialog
import wfdb, numpy as np, math, random
import pyqtgraph as pg
import Classes
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
        self.reconstructed_signal = None
        self.noisy_signal = None
        self.component_count = 0
        self.frequency = None
        self.sampled_points = None
        self.COMPONENTS = []

    def load_signal(self):
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            Record = wfdb.rdrecord(File_Path[:-4])
            Y_Coordinates = list(Record.p_signal[:1000, 0])
            X_Coordinates = list(np.arange(len(Y_Coordinates)))
            self.main_signal = Classes.Signal(X_Coordinates, Y_Coordinates, 'r')
            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen = 'b')
            if self.frequency:
                self.reconstruct_signal(self.sampled_points, self.frequency, len(self.main_signal.X_Coordinates))
                

    # Step 1: Sample the signal
    def plot_samples(self, sampling_frequency):
        self.frequency = sampling_frequency
        sampling_period = 1 / sampling_frequency #float result, not expected nor needed
        self.sampled_points = self.main_signal.X_Coordinates[::sampling_period] # i need to skip in the slicing tech using integer
        # Create a scatter plot item
        scatter_plot = pg.ScatterPlotItem()
        # Set the x and y coordinates of the scatter plot
        x_coordinates = np.arange(0, len(self.main_signal.X_Coordinates), int(1 / sampling_frequency))
        y_coordinates = self.sampled_points
        scatter_plot.setData(x_coordinates, y_coordinates)
        # Set the color of the scatter plot markers
        scatter_plot.setPen(pg.mkPen(color='r'))
        # Add the scatter plot item to the plot
        self.load_graph_1.plot.addItem(scatter_plot)

    # Step 2: Reconstruct the signal using Whittaker-Shannon interpolation formula
    def reconstruct_signal(sampled_points, sampling_frequency, original_length):
        time = np.arange(0, original_length)
        reconstructed_signal = np.zeros(original_length)
        for i in range(len(sampled_points)):
            reconstructed_signal += sampled_points[i] * np.sinc(time - i / sampling_frequency)
        return reconstructed_signal

    def Reconstruction_signal(self):
        pass
        #reconstructed_signal = reconstruct_signal(sampled_points, sampling_frequency, len(signal_data))

    def difference(self):
        pass
        # Step 3: Calculate the difference between the original and reconstructed signal
        #difference = signal_data - reconstructed_signal


    def add_noise(self, SNR_value):
        signal_power = sum(y ** 2 for y in self.main_signal.Y_Coordinates) / len(self.main_signal.Y_Coordinates)
        noise_power = signal_power / (10**(SNR_value / 10))
        noise_std = math.sqrt(noise_power)
        noise = [random.gauss(0, noise_std) for _ in range(len(self.main_signal.Y_Coordinates))]
        self.noisy_signal = Classes.Signal(self.main_signal.X_Coordinates, [s + n for s, n in zip(self.main_signal.Y_Coordinates, noise)])
        self.load_graph_1.clear()
        self.load_graph_1.plot(self.noisy_signal.X_Coordinates, self.noisy_signal.Y_Coordinates, pen = 'b')
        
    
    
    
    

    def add_component(self):
        self.component_count += 1
        if self.component_count == 1:
            new_component = Classes.Component()
            self.COMPONENTS.append(new_component)
            return

        Temporary_String = f"Component {self.component_count}"
        self.ui_window.Compose_Components_ComboBox.addItem(Temporary_String)

        new_component = Classes.Component()
        self.COMPONENTS.append(new_component)


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


    def update_sliders(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        self.ui_window.Compose_Signal_Magnitude_Slider.setValue(selected_component.magnitude)
        self.ui_window.Compose_Signal_Frequency_Slider.setValue(selected_component.frequency)


    def update_magnitude(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        selected_component.magnitude = self.ui_window.Compose_Signal_Magnitude_Slider.value()
        self.compose_signal()


    def update_frequency(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        selected_component.frequency = self.ui_window.Compose_Signal_Frequency_Slider.value()
        self.compose_signal()


    def compose_signal(self):
        
        #magnitude_1 = self.ui_window.Compose_Signal_Magnitude_Slider.value()
        #frequency_1 = self.ui_window.Compose_Signal_Frequency_Slider.value()

        t = np.linspace(0, 1, 500)
        signal = 0
        for component in self.COMPONENTS:
            signal += component.magnitude * np.sin(2 * np.pi * component.frequency * t)

        self.compose_graph_1.clear()
        self.compose_graph_1.plot(t, signal, pen='g')