import sounddevice as sd
import soundfile as sf
import json
import time
import os
from acrcloud.recognizer import ACRCloudRecognizer

# Configuration
config = {
    'host':          'identify-ap-southeast-1.acrcloud.com',
    'access_key':    '2f700dc165c461788a702a0f4a6404f0',
    'access_secret': 'dQPaVo4mUUzCSRBahzrCA4N0Ma7CHXcw5bLm6HeV',
    'timeout':       20
}
SR = 44100               # Sample rate
DURATION = 15            # Record window in seconds
TEMP_FILE = "realtime_hum.wav"

# Recognizer instance
acr = ACRCloudRecognizer(config)

def record_chunk(filename, duration, samplerate):
    print(f"Recording {duration}s…")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    sf.write(filename, audio, samplerate)
    return filename

def recognize(filename):
    print("Recognizing…")
    result_json = acr.recognize_by_file(filename, -1)
    result = json.loads(result_json)
    music_list = result.get("metadata", {}).get("music", [])
    if music_list:
        top = music_list[0]
        title = top.get("title", "Unknown")
        artist = top.get("artists", [{}])[0].get("name", "Unknown")
        print(f"Match: {title} — {artist}\n")
        return title, artist
    else:
        print("No match found.\n")
        return None

def main_loop():
    print("Real-time humming detector started. Hum a melody every few seconds.")
    try:
        while True:
            record_chunk(TEMP_FILE, DURATION, SR)
            recognize(TEMP_FILE)
            time.sleep(1)  # Small buffer between requests
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)

if __name__ == "__main__":
    main_loop()
