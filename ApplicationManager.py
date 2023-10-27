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

    @staticmethod
    def sinc(x):
        if abs(x) >= np.sqrt(np.sqrt(np.finfo(float).eps)):
            return np.sin(np.pi * x) / (np.pi * x)
        else:
            return 1 - x**2/6 + x**4/120

    def resample(self, ts, signal):
        def signal_func(t):
            return sum([s * self.sinc((t - n*ts)/ts) for n, s in enumerate(signal)])
        return signal_func
    
    
    
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
            if len(self.loaded_signals) > 1:
                Temporary_String = f"Signal {len(self.loaded_signals)}"
                self.ui_window.Load_Signals_ComboBox.addItem(Temporary_String)
                self.ui_window.Load_Signals_ComboBox.setCurrentIndex(len(self.loaded_signals) - 1)
            self.load_graph_1.clear()
            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen = 'b')
            #self.plot_sine_wave()
            
    def get_sampling_frequency(self):
        if self.ui_window.Load_x2Fmax_CheckBox.isChecked():
            # Calculate the maximum frequency of the loaded signal
            max_freq = max(np.abs(np.fft.rfft(self.current_loaded_signal.Y_Coordinates)))
            return 2 * max_freq 
        elif self.ui_window.Load_Hertz_CheckBox.isChecked():
            # Read the value of the Load_Sampling_Frequency_Slider
            return self.ui_window.Load_Sampling_Frequency_Slider.value()
        else:
            return None 
           
    def plot_sine_wave(self):
        
        magnitude_1 = 5
        frequency_1 = 2

        t = np.linspace(0, 1, 500)
        signal = magnitude_1 * np.sin(2 * np.pi * frequency_1 * t)

        # Resample the signal
        resampled_signal = self.resample(1/frequency_1, signal)

        x = np.arange(0, 1, 0.002)
        y1 = signal
        y2 = [resampled_signal(i) for i in x]

        self.load_graph_1.clear()
        self.load_graph_1.plot(x, y1, pen='g')
        self.load_graph_2.plot(x, y2, pen='b')

        # # Define the parameters of the sine wave
        # frequency = 5  # Frequency in Hz
        # duration = 1  # Duration in seconds
        # sampling_rate = 100  # Sampling rate in Hz (number of samples per second)

        # # Generate the time values for one period of the sine wave
        # t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

        # # Generate the sine wave
        # sine_wave = np.sin(2 * np.pi * frequency * t)
        # self.sampled_points = sine_wave[::sampling_rate]

        # # Plot the sine wave on load_graph_1
        # self.load_graph_1.plot(t, sine_wave, pen='b')

        # # Set the sine wave as the main signal
        # self.current_loaded_signal = Classes.Signal(t.tolist(), sine_wave.tolist())
        #  # Reconstruct the signal and plot the difference
        # self.reconstruct_signal()
        # self.plot_difference()

                
                
    def plot_samples(self):
        freq = self.get_sampling_frequency()
        if freq is None:
            return
        # Convert frequency to integer for slicing
        freq = int(freq)
        #TODO fix the slicing var it can not be using freq, but instead it have to be proven form freq.
        # Sample the signal at the given frequency
        self.sampled_points = self.current_loaded_signal.Y_Coordinates[::freq]
        self.sampling_period = 1 / freq
        self.load_graph_1.clear()
        # Plot the sampled points on load_graph_1
        self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates[::freq], self.sampled_points, pen=None, symbol='o')
        # Reconstruct the signal and plot the difference
        self.reconstruct_signal()
        self.plot_difference()

    def whittaker_shannon_interpolation(self, time , samples, period):
        # Calculate the sum of the product of the samples and the sinc function
        return sum(sample * np.sinc((time - index * period) / period) for index, sample in enumerate(samples))            
    
    
    # Step 2: Reconstruct the signal using Whittaker-Shannon interpolation formula
    def reconstruct_signal(self):
        # Use the Whittaker-Shannon interpolation formula to reconstruct the signal
        self.reconstructed_signal = [self.whittaker_shannon_interpolation(time, self.sampled_points, self.sampling_period) for time in self.current_loaded_signal.X_Coordinates]
        # Plot the reconstructed signal on load_graph_2
        self.load_graph_2.clear()
        self.load_graph_2.plot(self.current_loaded_signal.X_Coordinates, self.reconstructed_signal, pen='r')
        
    def plot_difference(self):
        # Calculate the difference between the original and reconstructed signals
        difference = np.array(self.current_loaded_signal.Y_Coordinates) - np.array(self.reconstructed_signal)
        # Plot the difference on load_graph_3\
        self.load_graph_3.clear()
        self.load_graph_3.plot(self.current_loaded_signal.X_Coordinates, difference.tolist(), pen='g')
        
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
        self.load_graph_1.clear()
        self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.noisy_Y_Coordinates, pen = 'b')

    


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