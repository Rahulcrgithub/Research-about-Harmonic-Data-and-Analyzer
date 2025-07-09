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
        self.root.title("Harmonic Waveform Visualizer")
        self.root.state("zoomed")

        self.theme = "light"
        self.bg_colors = {"light": "#f0f0f0", "dark": "#1e1e1e"}
        self.fg_colors = {"light": "#000000", "dark": "#ffffff"}

        self.root.configure(bg=self.bg_colors[self.theme])
        self.harmonics = {n: {"magnitude": 0, "phase": 0} for n in range(2, 20)}
        self.create_widgets()
        self.update_plot()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.root.configure(bg=self.bg_colors[self.theme])
        self.update_plot()

    def create_widgets(self):
        # Theme toggle button
        toggle_btn = ttk.Button(self.root, text="Toggle Theme", command=self.toggle_theme)
        toggle_btn.pack(anchor='ne', padx=10, pady=5)

        # Plot frame
        plot_frame = ttk.Frame(self.root, padding=10)
        plot_frame.pack(side="top", fill="both", expand=True)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 6))
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Scrollable harmonic controls
        container = ttk.Frame(self.root)
        container.pack(side="bottom", fill="both", expand=False)

        canvas = tk.Canvas(container, height=300)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for n in range(2, 20):
            row = n - 2
            ttk.Label(scrollable_frame, text=f"{n}x Harmonic ({n*base_freq} Hz):",
                      font=('Segoe UI', 10)).grid(row=row, column=0, padx=10, pady=5, sticky="w")

            ttk.Label(scrollable_frame, text="Mag", font=('Segoe UI', 9)).grid(row=row, column=1, padx=(20, 5))
            mag = tk.Scale(scrollable_frame, from_=0, to=10, orient='horizontal', resolution=0.1, length=200,
                           command=lambda val, h=n: self.set_and_update(h, 'magnitude', val))
            mag.set(0)
            mag.grid(row=row, column=2, padx=(0, 30), pady=5)

            ttk.Label(scrollable_frame, text="Phase", font=('Segoe UI', 9)).grid(row=row, column=3, padx=(10, 5))
            phase = tk.Scale(scrollable_frame, from_=0, to=360, orient='horizontal', length=200,
                             command=lambda val, h=n: self.set_and_update(h, 'phase', val))
            phase.set(0)
            phase.grid(row=row, column=4, pady=5)

    def set_and_update(self, harmonic, key, value):
        self.harmonics[harmonic][key] = float(value)
        self.update_plot()

    def generate_signal_components(self):
        fundamental = np.sin(2 * np.pi * base_freq * t)
        harmonic_signals = {1: fundamental}
        for n in self.harmonics:
            mag = self.harmonics[n]["magnitude"]
            phase = np.radians(self.harmonics[n]["phase"])
            harmonic_signals[n] = mag * np.sin(2 * np.pi * n * base_freq * t + phase)
        return harmonic_signals

    def update_plot(self):
        components = self.generate_signal_components()
        signal = sum(components.values())

        self.ax1.cla()
        self.ax2.cla()

        # Time Domain Plot
        colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        self.ax1.plot(t, signal, label="Combined Signal", color='yellow', linewidth=1.8)

        for i, (n, comp) in enumerate(components.items()):
            label = f"{n}x Harmonic" if n > 1 else "Fundamental"
            self.ax1.plot(t, comp, label=label, linestyle='--', color=colors[n % len(colors)])

        self.ax1.set_xlim(0, 0.1)
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Amplitude")
        self.ax1.set_title("Time Domain Waveform with Harmonics", fontsize=12)
        self.ax1.grid(True)
        self.ax1.legend(loc='upper right', fontsize=9)

        # Frequency Domain Plot
        fft_vals = np.fft.fft(signal)
        fft_freqs = np.fft.fftfreq(len(signal), 1/fs)
        half_n = len(signal) // 2
        magnitude = 2 / len(signal) * np.abs(fft_vals[:half_n])

        self.ax2.plot(fft_freqs[:half_n], magnitude, color='darkcyan', linewidth=1.5)
        self.ax2.set_xlim(0, 1000)
        self.ax2.set_xlabel("Frequency (Hz)")
        self.ax2.set_ylabel("Magnitude (V)")
        self.ax2.set_title("FFT Spectrum (0–1000 Hz)", fontsize=12)
        self.ax2.grid(True)

        for h in range(1, 20):
            freq = h * base_freq
            idx = np.argmin(np.abs(fft_freqs - freq))
            mag = magnitude[idx]
            self.ax2.axvline(x=freq, color='red', linestyle='--', alpha=0.4)
            self.ax2.annotate(f"{h}x\n{freq}Hz", xy=(freq, mag), xytext=(freq + 5, mag + 0.5),
                              textcoords="data", fontsize=8, color='red',
                              arrowprops=dict(arrowstyle='->', color='red', lw=0.5))

        # Theme settings
        bg = self.bg_colors[self.theme]
        fg = self.fg_colors[self.theme]
        self.fig.patch.set_facecolor(bg)
        self.ax1.set_facecolor(bg)
        self.ax2.set_facecolor(bg)
        self.ax1.title.set_color(fg)
        self.ax2.title.set_color(fg)
        self.ax1.xaxis.label.set_color(fg)
        self.ax2.xaxis.label.set_color(fg)
        self.ax1.yaxis.label.set_color(fg)
        self.ax2.yaxis.label.set_color(fg)
        self.ax1.tick_params(colors=fg)
        self.ax2.tick_params(colors=fg)

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = HarmonicVisualizer(root)
    root.mainloop()