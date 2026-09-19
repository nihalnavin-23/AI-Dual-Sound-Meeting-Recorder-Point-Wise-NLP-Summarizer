"""
Generates synthetic sample meeting audio and JSON records for immediate testing.
"""

import os
import wave
import struct
import math
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WAV_PATH = os.path.join(BASE_DIR, "quarterly_sync.wav")

def generate_sample_wav(filepath: str, duration_sec: int = 6):
    """Generates a clean synthetic dual-tone WAV audio file representing spoken dialogue."""
    sample_rate = 16000
    num_samples = duration_sec * sample_rate
    
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1) # Mono
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(sample_rate)
        
        # Generate varied human voice frequency bands (150Hz - 800Hz) with natural speech pauses
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Add modulation to mimic speech syllabic envelope
            envelope = math.sin(2 * math.pi * 3 * t) ** 2
            
            # Speech fundamental + formant frequencies
            val = (
                0.5 * math.sin(2 * math.pi * 220 * t) +
                0.3 * math.sin(2 * math.pi * 440 * t) +
                0.2 * math.sin(2 * math.pi * 750 * t)
            ) * envelope
            
            sample_val = int(val * 32767 * 0.4)
            data = struct.pack('<h', sample_val)
            wf.writeframesraw(data)

if __name__ == '__main__':
    generate_sample_wav(WAV_PATH, duration_sec=8)
    print(f"Sample meeting audio generated: {WAV_PATH}")
