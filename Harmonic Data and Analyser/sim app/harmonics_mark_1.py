import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Constants
fs = 5000  # Sampling frequency
T = 1 / fs
t = np.linspace(0, 0.1, int(0.1 * fs), endpoint=False)
base_freq = 50  # Fundamental frequency

class HarmonicVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("FFT Signal Analysis")

        self.harmonics = {n: {"magnitude": 0, "phase": 0} for n in range(2, 8)}

        self.create_widgets()
        self.update_plot()

    def create_widgets(self):
        # Matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=7)

        # Harmonic controls
        row = 1
        for n in range(2, 8):
            ttk.Label(self.root, text=f"{n}x Harmonic ({n*base_freq} Hz)").grid(row=row, column=0, sticky='w')

            ttk.Label(self.root, text="Mag").grid(row=row, column=1)
            mag = tk.Scale(self.root, from_=0, to=10, orient='horizontal', resolution=0.1,
                           command=lambda val, h=n: self.set_and_update(h, 'magnitude', val))
            mag.set(0)
            mag.grid(row=row, column=2)

            ttk.Label(self.root, text="Phase").grid(row=row, column=3)
            phase = tk.Scale(self.root, from_=0, to=360, orient='horizontal',
                             command=lambda val, h=n: self.set_and_update(h, 'phase', val))
            phase.set(0)
            phase.grid(row=row, column=4)

            row += 1

    def set_and_update(self, harmonic, key, value):
        self.harmonics[harmonic][key] = float(value)
        self.update_plot()

    def generate_signal_components(self):
        fundamental = np.sin(2 * np.pi * base_freq * t)
        harmonic_signals = {1: fundamental}
        for n in range(2, 8):
            mag = self.harmonics[n]["magnitude"]
            phase = np.radians(self.harmonics[n]["phase"])
            harmonic_signals[n] = mag * np.sin(2 * np.pi * n * base_freq * t + phase)
        return harmonic_signals

    def update_plot(self):
        components = self.generate_signal_components()
        signal = sum(components.values())

        # Clear axes
        self.ax1.cla()
        self.ax2.cla()

        # Time-domain plot
        colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink']
        self.ax1.plot(t, signal, label="Combined Signal", color='black', linewidth=1.5)

        for i, (n, comp) in enumerate(components.items()):
            label = f"{n}x Harmonic" if n > 1 else "Fundamental"
            self.ax1.plot(t, comp, label=label, linestyle='--', color=colors[n % len(colors)])

        self.ax1.set_xlim(0, 0.1)
        self.ax1.set_xlabel("Seconds")
        self.ax1.set_ylabel("Amplitude")
        self.ax1.set_title("Time Domain")
        self.ax1.grid(True)
        self.ax1.legend(loc='upper right')

        # Frequency-domain plot
        fft_vals = np.fft.fft(signal)
        fft_freqs = np.fft.fftfreq(len(signal), 1/fs)
        half_n = len(signal) // 2

        self.ax2.bar(fft_freqs[:half_n], 2/len(signal) * np.abs(fft_vals[:half_n]), width=2.5, color='blue')
        self.ax2.set_xlim(0, 400)
        self.ax2.set_xlabel("Frequency (Hz)")
        self.ax2.set_ylabel("Magnitude")
        self.ax2.set_title("FFT Spectrum")
        self.ax2.grid(True)

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = HarmonicVisualizer(root)
    root.mainloop()