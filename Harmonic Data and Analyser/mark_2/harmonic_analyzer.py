import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq

SAMPLE_RATE = 1000

def calculate_thd(fft_magnitude, fundamental_bin, harmonic_bins):
    fundamental_mag = fft_magnitude[fundamental_bin]
    harmonic_power = sum(fft_magnitude[h]**2 for h in harmonic_bins)
    return 100 * np.sqrt(harmonic_power) / fundamental_mag

print("Harmonic analyzer started", flush=True)
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

cycle = 0
try:
    while True:
        start_time = time.time()
        cycle += 1
        
        try:
            df = pd.read_csv('realtime_data.csv')
        except Exception as e:
            print(f"Error reading data: {e}", flush=True)
            time.sleep(0.5)
            continue
            
        if len(df) < 1000:
            print("Waiting for more data...", flush=True)
            time.sleep(0.1)
            continue
            
        # Extract Phase A voltage
        signal = df['PhaseA(V)'].values
        N = len(signal)
        t = df['Time(ms)'].values / 1000
        
        # Compute RMS and fundamental metrics
        rms_voltage = np.sqrt(np.mean(signal**2))
        fundamental_peak = np.max(signal[:20])
        
        # Perform FFT
        yf = rfft(signal)
        xf = rfftfreq(N, 1/SAMPLE_RATE)
        magnitude = np.abs(yf) / N * 2
        
        # Identify key frequencies
        fundamental_bin = np.argmax(magnitude[:100])
        fundamental_freq = xf[fundamental_bin]
        
        # Find harmonic bins
        harmonic_bins = []
        harmonic_freqs = []
        for h in range(2, 50):
            target_freq = h * fundamental_freq
            if target_freq > SAMPLE_RATE/2:
                break
            bin_idx = np.argmin(np.abs(xf - target_freq))
            harmonic_bins.append(bin_idx)
            harmonic_freqs.append(xf[bin_idx])
        
        # Calculate THD
        thd = calculate_thd(magnitude, fundamental_bin, harmonic_bins)
        
        # Terminal Output
        print("\n" + "="*50, flush=True)
        print(f"ANALYSIS CYCLE {cycle}", flush=True)
        print(f"Fundamental: {fundamental_freq:.2f} Hz | Magnitude: {magnitude[fundamental_bin]:.2f} V", flush=True)
        print(f"THD: {thd:.2f}% | RMS Voltage: {rms_voltage:.2f} V", flush=True)
        print("-"*50, flush=True)
        print("Harmonics:", flush=True)
        for i, h_bin in enumerate(harmonic_bins[:10]):
            print(f"  Harmonic {i+2}: {magnitude[h_bin]:.2f} V @ {xf[h_bin]:.2f} Hz", flush=True)
        print("="*50 + "\n", flush=True)
        
        # Live Plots
        ax1.clear()
        ax1.plot(t, signal, 'b-')
        ax1.set_title(f'Phase A Voltage (THD={thd:.1f}%)')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Voltage (V)')
        ax1.set_ylim(-1.5*fundamental_peak, 1.5*fundamental_peak)
        
        ax2.clear()
        ax2.stem(xf[:500], magnitude[:500], 'r-', markerfmt=' ', basefmt=' ')
        ax2.set_title('Frequency Spectrum')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude (V)')
        ax2.set_xlim(0, 1000)
        ax2.grid(True)
        
        plt.tight_layout()
        plt.pause(0.01)
        
        # Maintain timing
        elapsed = time.time() - start_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
            
except KeyboardInterrupt:
    plt.ioff()
    plt.show()
    print("Harmonic analyzer stopped", flush=True)