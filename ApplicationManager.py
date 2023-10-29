import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import wfdb, numpy as np, math, random
import Classes
import csv
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
        self.reconstructed_signal = None
        self.component_count = 0
        self.frequency = None
        self.sampled_points = None
        self.sampling_period = None
        self.loaded_signals = []
        self.current_loaded_signal = None
        self.COMPONENTS = []
        self.Composed_Signal = None
        self.sampled_Xpoints = None
        self.current_tab = "Load"
        self.samples_per_period = None
        self.counter = 0

    
    def get_current_loaded_signal_slot(self, index):
        self.current_loaded_signal = self.loaded_signals[index]
        self.load_graph_1.clear()
        self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.Y_Coordinates, pen = 'b')

    def update_current_tab(self):
        if self.current_tab == "Compose":
            self.current_tab = "Load"
        else:
            self.current_tab = "Compose"

    def load_signal(self):
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            if File_Path[-4:] == ".csv":
                Coordinates_List = ["x", "y", "f"]
                Signal = pd.read_csv(File_Path, usecols=Coordinates_List)
                X_Coordinates = Signal["x"]
                Y_Coordinates = Signal["y"]
                max_frequency = Signal["f"]

            else:
                Record = wfdb.rdrecord(File_Path[:-4])
                Y_Coordinates = list(Record.p_signal[:1000, 0])
                X_Coordinates = list(np.arange(len(Y_Coordinates)))

            self.loaded_signals.append(Classes.Signal(X_Coordinates, Y_Coordinates))
            self.current_loaded_signal = self.loaded_signals[-1]
            if File_Path[-4:] == ".csv":
                self.current_loaded_signal.max_freq = max_frequency[0]
            else:
                self.current_loaded_signal.max_freq = max(np.abs(np.fft.rfft(self.current_loaded_signal.Y_Coordinates)))
            if len(self.loaded_signals) > 1:
                Temporary_String = f"Signal {len(self.loaded_signals)}"
                self.ui_window.Load_Signals_ComboBox.addItem(Temporary_String)
                self.ui_window.Load_Signals_ComboBox.setCurrentIndex(len(self.loaded_signals) - 1)
            self.load_graph_1.clear()
            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen='b')
            self.update_sampling_slider()
            
    def get_sampling_frequency(self):
        if self.current_tab == "Load":
            self.current_loaded_signal.sampling_rate = self.ui_window.Load_Sampling_Frequency_Slider.value()
            if self.ui_window.Load_Sampling_Frequency_Slider.value():
                if self.ui_window.Load_Fmax_RadioButton.isChecked():
                    return self.ui_window.Load_Sampling_Frequency_Slider.value() * self.current_loaded_signal.max_freq
                elif self.ui_window.Load_Hertz_RadioButton.isChecked():
                    return self.ui_window.Load_Sampling_Frequency_Slider.value()
            else:
                return None
        else:
            if self.ui_window.Compose_Sampling_Frequency_Slider.value():
                if self.ui_window.Compose_Fmax_RadioButton.isChecked():
                    return self.ui_window.Compose_Sampling_Frequency_Slider.value() * self.Composed_Signal.max_freq
                elif self.ui_window.Compose_Hertz_RadioButton.isChecked():
                    return self.ui_window.Compose_Sampling_Frequency_Slider.value()
            else:
                return None

    def plot_samples(self):
        if self.current_tab == "Load":
            freq = self.get_sampling_frequency()
            if (freq is None) or (freq == 0):
                return
            self.sampling_period = float(1 / freq)
            # Calculate the number of samples per period
            self.samples_per_period = float(len(self.current_loaded_signal.X_Coordinates) * self.sampling_period)
            if self.samples_per_period <= 1:
                self.samples_per_period = 1
            else:
               self.samples_per_period = math.floor(self.samples_per_period)

            # Sample the signal at the given frequency
            self.sampled_points = [self.current_loaded_signal.noisy_Y_Coordinates[i] for i in range(0, len(self.current_loaded_signal.noisy_Y_Coordinates), (self.samples_per_period))]
            self.sampled_points = np.array(self.sampled_points)
            # Generate x-coordinate points based on the length of sampled_points
            self.sampled_Xpoints = [self.current_loaded_signal.X_Coordinates[i] for i in range(0, len(self.current_loaded_signal.noisy_Y_Coordinates), (self.samples_per_period))]
            self.sampled_Xpoints = np.array(self.sampled_Xpoints)  # Convert to a NumPy array
            self.load_graph_1.clear()
            # Plot the sampled points on load_graph_1
            self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.noisy_Y_Coordinates, pen = 'b')
            self.load_graph_1.plot(self.sampled_Xpoints, self.sampled_points, pen=None, symbol='o')
            # Reconstruct the signal and plot the difference
            self.reconstruct_signal()
            self.plot_difference()
        else:
            freq = self.get_sampling_frequency()
            if (freq is None) or (freq == 0):
                return
            self.sampling_period = float(1 / freq)
            # Calculate the number of samples per period
            self.samples_per_period = float(len(self.Composed_Signal.X_Coordinates) * self.sampling_period)
            if self.samples_per_period <= 1:
                self.samples_per_period = 1
            else:
               self.samples_per_period = math.floor(self.samples_per_period)
            # Sample the signal at the given frequency
            self.sampled_points = [self.Composed_Signal.noisy_Y_Coordinates[i] for i in range(0, len(self.Composed_Signal.noisy_Y_Coordinates), (self.samples_per_period))]
            self.sampled_points = np.array(self.sampled_points)
            # Generate x-coordinate points based on the length of sampled_points
            self.sampled_Xpoints = [self.Composed_Signal.X_Coordinates[i] for i in range(0, len(self.Composed_Signal.noisy_Y_Coordinates), (self.samples_per_period))]
            self.sampled_Xpoints = np.array(self.sampled_Xpoints)  # Convert to a NumPy array
            self.compose_graph_1.clear()
            # Plot the sampled points on load_graph_1
            self.compose_graph_1.plot(self.Composed_Signal.X_Coordinates, self.Composed_Signal.noisy_Y_Coordinates, pen = 'b')
            self.compose_graph_1.plot(self.sampled_Xpoints, self.sampled_points, pen=None, symbol='o')
            # Reconstruct the signal and plot the difference
            self.reconstruct_signal()
            self.plot_difference()
        
    def ShannonInterpolation(self, input_magnitude, input_time, original_time):
        if len(input_magnitude) != len(input_time):
            print('Input magnitude and time are not the same length')
            return

        if len(input_time) != 0:
            T = input_time[1] - input_time[0]

        sincM = np.tile(original_time, (len(input_time), 1)) - np.tile(input_time[:, np.newaxis], (1, len(original_time)))
        output_magnitude = np.dot(input_magnitude, np.sinc(sincM/T))

        return output_magnitude

    def reconstruct_signal(self):
        if self.current_tab == "Load":    
            self.reconstructed_signal = self.ShannonInterpolation(self.sampled_points, self.sampled_Xpoints, self.current_loaded_signal.X_Coordinates)
            self.load_graph_2.clear()
            self.load_graph_2.plot(self.current_loaded_signal.X_Coordinates, self.reconstructed_signal, pen='r')
        else:
            self.reconstructed_signal = self.ShannonInterpolation(self.sampled_points, self.sampled_Xpoints, self.Composed_Signal.X_Coordinates)
            self.compose_graph_2.clear()
            self.compose_graph_2.plot(self.Composed_Signal.X_Coordinates, self.reconstructed_signal, pen='r')
        
    def plot_difference(self):
        if self.current_tab == "Load": 
            difference = [y - x for y, x in zip(self.reconstructed_signal, self.current_loaded_signal.noisy_Y_Coordinates)]
            # Plot the difference on load_graph_3
            self.load_graph_3.clear()
            self.load_graph_3.plot(self.current_loaded_signal.X_Coordinates, difference, pen='g')
        else:
            difference = [y - x for y, x in zip(self.reconstructed_signal, self.Composed_Signal.noisy_Y_Coordinates)]
            # Plot the difference on compose_graph_3
            self.compose_graph_3.clear()
            self.compose_graph_3.plot(self.Composed_Signal.X_Coordinates, difference, pen='g')

    def update_sampling_slider(self):
        if self.current_tab == "Load":

            if self.ui_window.Load_Hertz_RadioButton.isChecked():
                self.ui_window.Load_Sampling_Frequency_Slider.setMinimum(1)
                self.ui_window.Load_Sampling_Frequency_Slider.setMaximum(6 * int(self.current_loaded_signal.max_freq))
                self.ui_window.Load_Sampling_Frequency_Slider.setTickInterval(int(6 * self.current_loaded_signal.max_freq / 10))
            else:
                self.ui_window.Load_Sampling_Frequency_Slider.setMinimum(1)
                self.ui_window.Load_Sampling_Frequency_Slider.setMaximum(6)
                self.ui_window.Load_Sampling_Frequency_Slider.setTickInterval(1)
        else:

            if self.ui_window.Compose_Hertz_RadioButton.isChecked():
                self.ui_window.Compose_Sampling_Frequency_Slider.setMinimum(1)
                max_component_freq = 0
                for component in self.COMPONENTS:
                    if component.frequency > max_component_freq:
                        max_component_freq = component.frequency
                # self.Composed_Signal.max_freq = max_component_freq
                self.ui_window.Compose_Sampling_Frequency_Slider.setMaximum(6 * int(max_component_freq))
                self.ui_window.Compose_Sampling_Frequency_Slider.setTickInterval(int(6 * max_component_freq / 10))
            else:
                self.ui_window.Compose_Sampling_Frequency_Slider.setMinimum(1)
                self.ui_window.Compose_Sampling_Frequency_Slider.setMaximum(6)
                self.ui_window.Compose_Sampling_Frequency_Slider.setTickInterval(1)

    def add_noise(self, SNR_value, compose=False):
        if compose:
            signal_power = sum(y ** 2 for y in self.Composed_Signal.Y_Coordinates) / len(self.Composed_Signal.Y_Coordinates)
            noise_power = signal_power / (10 ** (SNR_value / 10))
            noise_std = math.sqrt(noise_power)
            noise = [random.gauss(0, noise_std) for _ in range(len(self.Composed_Signal.Y_Coordinates))]
            self.Composed_Signal.noisy_Y_Coordinates = [s + n for s, n in zip(self.Composed_Signal.Y_Coordinates, noise)]
            self.plot_samples()
            return
        
        self.current_loaded_signal.noise = self.ui_window.Load_Signal_to_Noise_Slider.value()
        signal_power = sum(y ** 2 for y in self.current_loaded_signal.Y_Coordinates) / len(self.current_loaded_signal.Y_Coordinates)
        noise_power = signal_power / (10**(SNR_value / 10))
        noise_std = math.sqrt(noise_power)
        noise = [random.gauss(0, noise_std) for _ in range(len(self.current_loaded_signal.Y_Coordinates))]
        self.current_loaded_signal.noisy_Y_Coordinates = [s + n for s, n in zip(self.current_loaded_signal.Y_Coordinates, noise)]
        self.plot_samples()

    def add_component(self):
        self.component_count += 1
        if self.component_count == 1:
            new_component = Classes.Component()
            self.COMPONENTS.append(new_component)
            self.update_sampling_slider()
            return

        Temporary_String = f"Component {self.component_count}"
        self.ui_window.Compose_Components_ComboBox.addItem(Temporary_String)

        new_component = Classes.Component()
        self.COMPONENTS.append(new_component)

    def remove_component(self):
        if self.component_count == 1:
            return
        self.component_count -= 1
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        self.COMPONENTS.pop(selected_index)

        if selected_index == self.ui_window.Compose_Components_ComboBox.count() - 1:
            self.ui_window.Compose_Components_ComboBox.removeItem(selected_index)
        else:
            self.ui_window.Compose_Components_ComboBox.removeItem(selected_index)
            for index in range(self.ui_window.Compose_Components_ComboBox.count()):
                if self.ui_window.Compose_Components_ComboBox.itemText(index)[-1] != index + 1:
                    self.ui_window.Compose_Components_ComboBox.setItemText(index, f"Component {index+1}")

        self.update_signal()

    def update_sliders(self):
        if self.current_tab == "Load":
            self.ui_window.Load_Sampling_Frequency_Slider.setValue(self.current_loaded_signal.sampling_rate)
            self.ui_window.Load_Signal_to_Noise_Slider.setValue(self.current_loaded_signal.noise)
            self.load_graph_2.clear()
            self.load_graph_3.clear()
            self.reconstruct_signal()
            self.plot_difference()
        else:    
            selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
            selected_component = self.COMPONENTS[selected_index]

            self.ui_window.Compose_Signal_Magnitude_Slider.setValue(selected_component.magnitude)
            self.ui_window.Compose_Signal_Frequency_Slider.setValue(selected_component.frequency)

    def update_magnitude(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        selected_component.magnitude = self.ui_window.Compose_Signal_Magnitude_Slider.value()
        self.update_signal()

    def update_frequency(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        selected_component.frequency = self.ui_window.Compose_Signal_Frequency_Slider.value()
        self.update_signal()

    def update_signal(self):

        signal_X = np.linspace(0, 1, 1000)
        signal_Y = 0
        for component in self.COMPONENTS:
            signal_Y += component.magnitude * np.sin(2 * np.pi * component.frequency * signal_X)

        self.compose_graph_1.clear()
        self.compose_graph_1.plot(signal_X, signal_Y, pen='b')

        self.Composed_Signal = Classes.Signal(signal_X, signal_Y)
        for component in self.COMPONENTS:
            if component.frequency > self.Composed_Signal.max_freq:
                self.Composed_Signal.max_freq = component.frequency

    def save_composed_signal(self):

        self.counter+=1
        filename = f'Composed_Signal_{self.counter}.csv'

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['x', 'y', 'max_frequency'])

            for i in range(len(self.Composed_Signal.X_Coordinates)):
                writer.writerow([self.Composed_Signal.X_Coordinates[i], self.Composed_Signal.Y_Coordinates[i], self.Composed_Signal.max_freq])