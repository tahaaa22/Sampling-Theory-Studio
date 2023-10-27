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

    
    def get_current_loaded_signal_slot(self, index):
        self.current_loaded_signal = self.loaded_signals[index]
        self.load_graph_1.clear()
        self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.Y_Coordinates, pen = 'b')

    def load_signal(self):
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            Record = wfdb.rdrecord(File_Path[:-4])
            Y_Coordinates = list(Record.p_signal[:1000, 0])
            X_Coordinates = list(np.arange(len(Y_Coordinates)))
            self.loaded_signals.append(Classes.Signal(X_Coordinates, Y_Coordinates))
            self.current_loaded_signal = self.loaded_signals[-1]
            self.current_loaded_signal.max_freq = max(np.abs(np.fft.rfft(self.current_loaded_signal.Y_Coordinates)))
            if len(self.loaded_signals) > 1:
                Temporary_String = f"Signal {len(self.loaded_signals)}"
                self.ui_window.Load_Signals_ComboBox.addItem(Temporary_String)
                self.ui_window.Load_Signals_ComboBox.setCurrentIndex(len(self.loaded_signals) - 1)
            self.load_graph_1.clear()
            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen = 'b')
            
    def get_sampling_frequency(self):
        if self.ui_window.Load_Sampling_Frequency_Slider.value():
            #Read the value of the Load_Sampling_Frequency_Slider
            return self.ui_window.Load_Sampling_Frequency_Slider.value()
       
                
    def plot_samples(self):
        freq = self.get_sampling_frequency()
        if freq is None:

            return
        self.sampling_period = 1 / freq
        # Calculate the number of samples per period
        samples_per_period = int(len(self.current_loaded_signal.X_Coordinates) * self.sampling_period)
        # Sample the signal at the given frequency
        self.sampled_points = [self.current_loaded_signal.noisy_Y_Coordinates[i] for i in range(0, len(self.current_loaded_signal.noisy_Y_Coordinates), samples_per_period)]
        # Generate x-coordinate points based on the length of sampled_points
        self.sampled_Xpoints = np.linspace(self.current_loaded_signal.X_Coordinates[0], self.current_loaded_signal.X_Coordinates[-1], len(self.sampled_points))
        # if len(sampled_Xpoints) < 2:
        #     print("Not enough sampled points for interpolation")
        #     return
        self.load_graph_1.clear()
        # Plot the sampled points on load_graph_1
        self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.noisy_Y_Coordinates, pen = 'b')
        self.load_graph_1.plot(self.sampled_Xpoints, self.sampled_points, pen=None, symbol='o')
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
        self.reconstructed_signal = self.ShannonInterpolation(self.sampled_points, self.sampled_Xpoints, self.sampled_Xpoints)
        self.load_graph_2.clear()
        self.load_graph_2.plot(self.sampled_Xpoints, self.reconstructed_signal, pen='r')
        
    def plot_difference(self):
        # Interpolate self.current_loaded_signal.Y_Coordinates to the length of self.reconstructed_signal
        interpolated_Y_Coordinates = np.interp(self.sampled_Xpoints, self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.noisy_Y_Coordinates)
        # Calculate the difference between the original and reconstructed signals
        difference = interpolated_Y_Coordinates - np.array(self.reconstructed_signal)
        # Plot the difference on load_graph_3
        self.load_graph_3.clear()
        self.load_graph_3.plot(self.sampled_Xpoints, difference.tolist(), pen='g')
            
    def load_update_sampling_slider(self):
        print("ENTERED")
        if self.ui_window.Load_Hertz_RadioButton.isChecked():
            self.ui_window.Load_Sampling_Frequency_Slider.setMinimum(1)
            self.ui_window.Load_Sampling_Frequency_Slider.setMaximum(4 * int(self.current_loaded_signal.max_freq))
            self.ui_window.Load_Sampling_Frequency_Slider.setTickInterval(int(4 * self.current_loaded_signal.max_freq / 5))
        else:
            self.ui_window.Load_Sampling_Frequency_Slider.setMinimum(1)
            self.ui_window.Load_Sampling_Frequency_Slider.setMaximum(4)
            self.ui_window.Load_Sampling_Frequency_Slider.setTickInterval(1)

    def compose_update_sampling_slider(self):
        if self.ui_window.Compose_Hertz_RadioButton.isChecked():
            self.ui_window.Compose_Sampling_Frequency_Slider.setMinimum(1)
            self.ui_window.Compose_Sampling_Frequency_Slider.setMaximum(4 * int(self.current_loaded_signal.max_freq))
            self.ui_window.Compose_Sampling_Frequency_Slider.setTickInterval(int(4 * self.current_loaded_signal.max_freq / 10))
        else:
            self.ui_window.Compose_Sampling_Frequency_Slider.setMinimum(1)
            self.ui_window.Compose_Sampling_Frequency_Slider.setMaximum(4)
            self.ui_window.Compose_Sampling_Frequency_Slider.setTickInterval(1)

    

    def add_noise(self, SNR_value, compose=False):
        if compose:
            signal_power = sum(y ** 2 for y in self.Composed_Signal.Y_Coordinates) / len(self.Composed_Signal.Y_Coordinates)
            noise_power = signal_power / (10 ** (SNR_value / 10))
            noise_std = math.sqrt(noise_power)
            noise = [random.gauss(0, noise_std) for _ in range(len(self.Composed_Signal.Y_Coordinates))]
            self.Composed_Signal.noisy_Y_Coordinates = [s + n for s, n in zip(self.Composed_Signal.Y_Coordinates, noise)]
            self.compose_graph_1.clear()
            self.compose_graph_1.plot(self.Composed_Signal.X_Coordinates,self.Composed_Signal.noisy_Y_Coordinates, pen='g')
            return
        signal_power = sum(y ** 2 for y in self.current_loaded_signal.Y_Coordinates) / len(self.current_loaded_signal.Y_Coordinates)
        noise_power = signal_power / (10**(SNR_value / 10))
        noise_std = math.sqrt(noise_power)
        noise = [random.gauss(0, noise_std) for _ in range(len(self.current_loaded_signal.Y_Coordinates))]
        self.current_loaded_signal.noisy_Y_Coordinates = [s + n for s, n in zip(self.current_loaded_signal.Y_Coordinates, noise)]
        self.plot_samples()
        # Reconstruct the signal and plot the difference
        self.reconstruct_signal()
        self.plot_difference()

    


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

        signal_X = np.linspace(0, 1, 500)
        signal_Y = 0
        for component in self.COMPONENTS:
            signal_Y += component.magnitude * np.sin(2 * np.pi * component.frequency * signal_X)

        self.compose_graph_1.clear()
        self.compose_graph_1.plot(signal_X, signal_Y, pen='g')

        self.Composed_Signal = Classes.Signal(signal_X, signal_Y)