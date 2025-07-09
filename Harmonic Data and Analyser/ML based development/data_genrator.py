import numpy as np
import pandas as pd
import os

# Constants
SAMPLE_RATE = 1000
FUNDAMENTAL_FREQ = 50
V_RMS = 240
V_PEAK = V_RMS * np.sqrt(2)
DURATION = 1  # 1 second window
SAMPLES = SAMPLE_RATE * DURATION
DATASET_SIZE = 500  # Number of labeled samples to generate

# Label thresholds
THD_THRESHOLDS = {
    "Low": 5,     # THD < 5%
    "Medium": 10, # 5% ≤ THD < 10%
    "High": 20    # 10% ≤ THD < 20%
}

# Output file
OUT_FILE = "harmonic_labeled_dataset.csv"


def generate_waveform_and_labels():
    t = np.arange(SAMPLES) / SAMPLE_RATE

    # Base signal
    signal = V_PEAK * np.sin(2 * np.pi * FUNDAMENTAL_FREQ * t)

    # Choose random harmonics (1–6 harmonics from 3rd to 49th odd)
    available_harmonics = list(range(3, 50, 2))
    num_harmonics = np.random.randint(1, 7)
    chosen_harmonics = sorted(np.random.choice(available_harmonics, size=num_harmonics, replace=False))

    harmonic_magnitudes = []

    for h in chosen_harmonics:
        mag = V_PEAK * np.random.uniform(0.01, 0.1)
        harmonic_magnitudes.append(mag)
        signal += mag * np.sin(2 * np.pi * FUNDAMENTAL_FREQ * h * t + np.random.uniform(0, 2*np.pi))

    # THD Calculation
    V1 = V_PEAK
    thd = np.sqrt(np.sum(np.square(harmonic_magnitudes))) / V1
    thd_percent = round(thd * 100, 2)

    # Classify THD level
    if thd_percent < THD_THRESHOLDS["Low"]:
        thd_class = "Low"
    elif thd_percent < THD_THRESHOLDS["Medium"]:
        thd_class = "Medium"
    else:
        thd_class = "High"

    return signal, thd_percent, thd_class, ",".join(map(str, chosen_harmonics))


def generate_dataset():
    data_rows = []

    for i in range(DATASET_SIZE):
        signal, thd, thd_class, harmonics = generate_waveform_and_labels()
        row = list(np.round(signal, 3)) + [thd, thd_class, harmonics]
        data_rows.append(row)

        if i % 50 == 0:
            print(f"Generated {i}/{DATASET_SIZE} samples")

    columns = [f"Va_{i}" for i in range(SAMPLES)] + ["THD", "THD_class", "harmonics_present"]
    df = pd.DataFrame(data_rows, columns=columns)
    df.to_csv(OUT_FILE, index=False)
    print(f"\nDataset saved to: {OUT_FILE}")


if __name__ == "__main__":
    if os.path.exists(OUT_FILE):
        os.remove(OUT_FILE)
    generate_dataset()
