import numpy as np
import csv
import time
import sys

# Configuration
SAMPLE_RATE = 1000
FUNDAMENTAL_FREQ = 50
BASE_VOLTAGE = 240 * np.sqrt(2)
HARMONICS = [3, 5, 7, 11, 13, 17, 19, 23, 25, 31, 35, 41, 43, 47]
PHASE_SHIFT = 2 * np.pi / 3

def generate_voltage(t, phase_offset=0):
    signal = BASE_VOLTAGE * np.sin(2 * np.pi * FUNDAMENTAL_FREQ * t + phase_offset)
    for h in HARMONICS:
        mag = BASE_VOLTAGE * np.random.uniform(0.01, 0.15)
        phase_noise = np.random.uniform(-0.1, 0.1)
        signal += mag * np.sin(2 * np.pi * h * FUNDAMENTAL_FREQ * t + phase_noise)
    signal += np.random.normal(0, 0.5)
    return signal

def init_csv(filename):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Time(ms)', 'PhaseA(V)', 'PhaseB(V)', 'PhaseC(V)'])

# Initialize CSV files
init_csv('realtime_data.csv')
init_csv('datalog.csv')

t = 0
cycle_count = 0
print("Data generator started", flush=True)

try:
    while True:
        start_time = time.time()
        realtime_buffer = []
        
        # Generate 1 second of data (1000 samples)
        for i in range(1000):
            va = generate_voltage(t)
            vb = generate_voltage(t, PHASE_SHIFT)
            vc = generate_voltage(t, 2 * PHASE_SHIFT)
            realtime_buffer.append([t * 1000, va, vb, vc])
            t += 0.001
            
            # Print progress every 100 samples
            if i % 100 == 0:
                print(f"Generating samples... {i+100}/1000", flush=True)
        
        # Update realtime CSV
        with open('realtime_data.csv', 'w') as f_rt:
            writer = csv.writer(f_rt)
            writer.writerow(['Time(ms)', 'PhaseA(V)', 'PhaseB(V)', 'PhaseC(V)'])
            writer.writerows(realtime_buffer)
        
        # Append to datalog
        with open('datalog.csv', 'a') as f_log:
            writer = csv.writer(f_log)
            writer.writerows(realtime_buffer)
        
        cycle_count += 1
        print(f"Cycle {cycle_count}: Generated 1000 samples (1.00s)", flush=True)
        
        # Maintain timing
        elapsed = time.time() - start_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
            
except KeyboardInterrupt:
    print("Data generator stopped", flush=True)