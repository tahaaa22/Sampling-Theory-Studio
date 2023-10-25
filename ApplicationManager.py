from PyQt5.QtWidgets import QFileDialog
import wfdb, numpy as np, math, random
import pyqtgraph as pg
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
        self.reconstructed_signal = None
        self.noisy_signal = None
        self.component_count = 1
        self.frequency = None
        self.sampled_points = None
        self.sampling_period = None

    def load_signal(self):
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            Record = wfdb.rdrecord(File_Path[:-4])
            Y_Coordinates = list(Record.p_signal[:1000, 0])
            X_Coordinates = list(np.arange(len(Y_Coordinates)))
            self.main_signal = SignalClass.Signal(X_Coordinates, Y_Coordinates, 'r')
            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen = 'b')
            
            
    def plot_sine_wave(self):
        # Define the parameters of the sine wave
        frequency = 100  # Frequency in Hz
        duration = 1  # Duration in seconds
        sampling_rate = 1000  # Sampling rate in Hz (number of samples per second)

        # Generate the time values for one period of the sine wave
        t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

        # Generate the sine wave
        sine_wave = np.sin(2 * np.pi * frequency * t)

        # Plot the sine wave on load_graph_1
        self.load_graph_1.plot(t, sine_wave, pen='b')

        # Set the sine wave as the main signal
        self.main_signal = SignalClass.Signal(t.tolist(), sine_wave.tolist())
                
    def whittaker_shannon_interpolation(self, t, samples, T):
        # Calculate the sum of the product of the samples and the sinc function
        return sum(sample * np.sinc((t - k * T) / T) for k, sample in enumerate(samples))            
                
    def plot_samples(self, frequency):
        self.plot_sine_wave()
        freq = 100
        # Sample the signal at the given frequency
        self.sampled_points = self.main_signal.Y_Coordinates[::freq]
        self.sampling_period = 1 / freq

        # Plot the sampled points on load_graph_1
        self.load_graph_1.plot(self.main_signal.X_Coordinates[::freq], self.sampled_points, pen=None, symbol='o')

        # Reconstruct the signal and plot the difference
        self.reconstruct_signal()
        self.plot_difference()

    def reconstruct_signal(self):
        # Use the Whittaker-Shannon interpolation formula to reconstruct the signal
        self.reconstructed_signal = [self.whittaker_shannon_interpolation(t, self.sampled_points, self.sampling_period) for t in self.main_signal.X_Coordinates]

        # Plot the reconstructed signal on load_graph_2
        self.load_graph_2.plot(self.main_signal.X_Coordinates, self.reconstructed_signal, pen='r')

    def plot_difference(self):
        # Calculate the difference between the original and reconstructed signals
        difference = np.array(self.main_signal.Y_Coordinates) - np.array(self.reconstructed_signal)
        # Plot the difference on load_graph_3
        self.load_graph_3.plot(self.main_signal.X_Coordinates, difference.tolist(), pen='g')
        
        
    # # Step 1: Sample the signal
    # def plot_samples(self, sampling_frequency):
    #     self.frequency = sampling_frequency
        
    #     #self.sampling_period = 1 / sampling_frequency #float result, not expected nor needed
    #     self.sampled_points = self.main_signal.X_Coordinates[::2] # i need to skip in the slicing tech using integer
    #     # Create a scatter plot item
    #     scatter_plot = pg.ScatterPlotItem()
    #     # Set the x and y coordinates of the scatter plot
    #     x_coordinates = np.arange(0, len(self.main_signal.X_Coordinates), 2)
    #     y_coordinates = self.sampled_points
    #     #scatter_plot.setData(x_coordinates, y_coordinates)
    #     #self.load_graph_2.plot(x_coordinates, y_coordinates, pen = 'r')
    #     # Set the color of the scatter plot markers
    #     #scatter_plot.setPen(pg.mkPen(color='r'))
    #     # Add the scatter plot item to the plot
    #     #self.load_graph_2.addItem(scatter_plot)
    #     self.load_graph_2.plot(x_coordinates, y_coordinates, pen = 'r')

    # # Step 2: Reconstruct the signal using Whittaker-Shannon interpolation formula
    # def Reconstruction_signal(self):
    #     # Step 2: Reconstruct the signal using Whittaker-Shannon interpolation formula
    #     time = np.arange(0, len(self.main_signal.X_Coordinates))
    #     reconstructed_signal = np.zeros(len(self.main_signal.X_Coordinates))
    #     for i in range(len(self.sampled_points)):
    #         reconstructed_signal += self.sampled_points[i] * np.sinc(time - i / self.frequency)
    
    #     # Plot the reconstructed signal
    #     #self.load_graph_2.clear()
    #     self.load_graph_2.plot(time, reconstructed_signal, pen='g')
        
    # def difference(self):
    #     # Step 3: Calculate the difference between the original and reconstructed signal
    #     difference = self.main_signal.Y_Coordinates - self.reconstructed_signal
    
    #     # Plot the difference
    #     #self.load_graph_3.clear()
    #     self.load_graph_3.plot(self.main_signal.X_Coordinates, difference, pen='b')


    def add_noise(self, SNR_value):
        signal_power = sum(y ** 2 for y in self.main_signal.Y_Coordinates) / len(self.main_signal.Y_Coordinates)
        noise_power = signal_power / (10**(SNR_value / 10))
        noise_std = math.sqrt(noise_power)
        noise = [random.gauss(0, noise_std) for _ in range(len(self.main_signal.Y_Coordinates))]
        self.noisy_signal = SignalClass.Signal(self.main_signal.X_Coordinates, [s + n for s, n in zip(self.main_signal.Y_Coordinates, noise)])
        self.load_graph_1.clear()
        self.load_graph_1.plot(self.noisy_signal.X_Coordinates, self.noisy_signal.Y_Coordinates, pen = 'b')
        

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