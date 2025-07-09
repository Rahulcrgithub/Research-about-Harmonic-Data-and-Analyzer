import numpy as np

# Constants
SAMPLE_RATE = 1000  # 1ms intervals
FUNDAMENTAL_FREQ = 50  # Hz
V_RMS = 240
V_PEAK = V_RMS * np.sqrt(2)
SAMPLES = SAMPLE_RATE * 1  # 1 second

def generate_test_waveform():
    t = np.arange(SAMPLES) / SAMPLE_RATE
    signal = V_PEAK * np.sin(2 * np.pi * FUNDAMENTAL_FREQ * t)

    # Random harmonic selection (3–49 odd)
    harmonics = np.random.choice(range(3, 50, 2), size=np.random.randint(2, 6), replace=False)
    for h in harmonics:
        mag = V_PEAK * np.random.uniform(0.01, 0.08)
        phase = np.random.uniform(0, 2*np.pi)
        signal += mag * np.sin(2 * np.pi * FUNDAMENTAL_FREQ * h * t + phase)

    return signal

# Generate and convert to comma-separated string
waveform = generate_test_waveform()
input_data_str = ",".join([f"{v:.3f}" for v in waveform])
print("Paste this into predict_model.py:\n")
print(f'input_data = "{input_data_str}"')
