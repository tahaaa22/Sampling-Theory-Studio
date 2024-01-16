# Sampling Theory Studio

Sampling Theory Studio is a desktop application that showcases the principles of signal sampling and recovery, emphasizing the importance and validation of the Nyquist rate. Sampling an analog signal is a crucial step in digital signal processing systems, and the Nyquist-Shannon sampling theorem guarantees the accurate recovery of the original signal when sampled with a frequency greater than or equal to its bandwidth (or double the maximum frequency for real signals).

![image](https://github.com/MoHazem02/Sampling-Theory-Studio/assets/66066832/2c2b9a46-5f0b-4ff1-8a54-83997149561f)

![image](https://github.com/MoHazem02/Sampling-Theory-Studio/assets/66066832/645d715a-0a96-45c3-a480-b62dfbae4679)

## Description

The Sampling Theory Studio project aims to provide a visual and interactive tool to understand and explore the concepts of signal sampling and recovery. The desktop application offers the following features:

1. Sample & Recover: This feature allows users to select an analog signal and sample it at a specified sampling rate. The sampled signal can then be recovered using various interpolation techniques, demonstrating the importance of the Nyquist rate.

2. Load and Compose: Users can load pre-recorded signals or compose their own signals using the provided signal generation tools. This feature enables the study of different signal characteristics and their impact on the sampling process.

3. Additive White Gaussian Noise: To simulate real-world scenarios, the application includes the option to introduce additive white Gaussian noise to the sampled signal. This feature helps users observe the effects of noise on the recovery process and understand the limitations of sampling in noisy environments.

4. Real-time Sampling and Recovery: The application supports real-time sampling and recovery, allowing users to visualize the effects of changing sampling rates dynamically. This feature enhances the understanding of the Nyquist rate in real-time signal processing scenarios.

5. Responsive Desktop App: The Sampling Theory Studio is designed as a responsive desktop application, providing an intuitive and user-friendly interface for an enhanced user experience.

## Libraries Used

The Sampling Theory Studio project utilizes the following libraries:

- PyQt5: Used for developing the responsive desktop application interface.
- wfdb: Enables the loading and handling of pre-recorded signals in various formats.
- pandas: Provides data manipulation and analysis capabilities for efficient signal processing.
- numpy: Essential library for numerical computations and array operations.
- math: Offers mathematical functions and utilities for signal transformations.
- csv: Enables reading and writing of CSV files for data storage and analysis.

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/tahaaa22/Sampling-Theory-Studio.git
    ```
2. Install the required Python libraries:

```shell
pip install pyqt5 wfdb pandas numpy
```

3. Launch the Sampling Theory Studio application:

```shell
python GUI.py
```
## Usage
1. Use the "Sample & Recover" feature to select an analog signal and specify the sampling rate. Observe the recovered signal and compare it with the original signal.

2. Explore the "Load and Compose" feature to load pre-recorded signals or generate custom signals. Experiment with different signal characteristics and observe their effects on the sampling and recovery process.

3. Utilize the "Additive White Gaussian Noise" option to introduce noise to the sampled signal. Observe the impact of noise on the recovery quality and understand the limitations of sampling in noisy environments.

4. Explore the real-time sampling and recovery capabilities to visualize the effects of changing sampling rates dynamically. Observe the behavior of the recovered signal in real-time scenarios.

## Contributing
Contributions to the Sampling Theory Studio project are welcome! If you find any bugs, have suggestions for improvements, or would like to add new features, please feel free to submit a pull request.


Acknowledgments
PyQt5
wfdb
pandas
numpy
math
csv
