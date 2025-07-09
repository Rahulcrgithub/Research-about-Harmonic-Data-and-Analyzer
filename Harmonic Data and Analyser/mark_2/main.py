# main.py
import subprocess
import time
import sys
import signal
import threading

# Global references to processes
generator_process = None
analyzer_process = None

def stream_reader(prefix, stream):
    """Read lines from a stream and print them with a prefix."""
    try:
        for line in iter(stream.readline, ''):
            if line:
                print(f"[{prefix}] {line.strip()}")
                sys.stdout.flush()
    finally:
        stream.close()

def signal_handler(sig, frame):
    """Handle Ctrl+C to terminate child processes."""
    print("\nTerminating processes...")
    if generator_process:
        generator_process.terminate()
    if analyzer_process:
        analyzer_process.terminate()
    # Wait for processes to terminate
    if generator_process:
        generator_process.wait()
    if analyzer_process:
        analyzer_process.wait()
    print("All processes terminated")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting data generator...")
    generator_process = subprocess.Popen(
        [sys.executable, "data_generator.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    # Wait for initial data
    time.sleep(0.5)
    print("Data generator running")
    
    print("Starting harmonic analyzer...")
    analyzer_process = subprocess.Popen(
        [sys.executable, "harmonic_analyzer.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    print("Both processes running. Press Ctrl+C to stop")
    print("=" * 60)
    
    # Create threads to read the streams
    threads = [
        threading.Thread(target=stream_reader, args=("GEN", generator_process.stdout)),
        threading.Thread(target=stream_reader, args=("GEN-ERR", generator_process.stderr)),
        threading.Thread(target=stream_reader, args=("ANA", analyzer_process.stdout)),
        threading.Thread(target=stream_reader, args=("ANA-ERR", analyzer_process.stderr)),
    ]
    
    # Start all threads
    for t in threads:
        t.daemon = True  # Daemon threads will be terminated when the main program exits
        t.start()
    
    # Keep the main thread alive until both processes finish (or until Ctrl+C)
    try:
        # Wait for both processes to finish (if they do, we break out)
        while generator_process.poll() is None or analyzer_process.poll() is None:
            time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)