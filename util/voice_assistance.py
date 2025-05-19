import sys
import io
import speech_recognition as sr
import pyttsx3
import os
import pygame
import time

# Fix unicode print issue on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Initialize Pygame for music
pygame.init()
pygame.mixer.init()

MUSIC_FOLDER = os.path.join("static", "songs")
playlist = [song for song in os.listdir(MUSIC_FOLDER) if song.endswith('.mp3')]
current_index = 0
assistant_active = True  # Flag to keep assistant running

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(timeout=6):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening...")  # Will say and print "Listening..."
        try:
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}", flush=True)  # Show your spoken command
            return command.lower()
        except sr.UnknownValueError:
            print("You said: [Unrecognized Speech]", flush=True)
            speak("Sorry, I didn't understand that.")
        except sr.WaitTimeoutError:
            print("You said: [No command heard]", flush=True)
            speak("No command heard.")
        except Exception as e:
            print(f"You said: [Error occurred: {e}]", flush=True)
            speak("Error occurred.")
    return None

def play_song(index):
    global current_index
    current_index = index
    song_path = os.path.join(MUSIC_FOLDER, playlist[current_index])
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    speak(f"Now playing {playlist[current_index]}")

def handle_command(command):
    global current_index
    global assistant_active

    if "play" in command and "song" in command:
        play_song(current_index)
    elif "pause" in command:
        pygame.mixer.music.pause()
        speak("Paused the music.")
    elif "resume" in command:
        pygame.mixer.music.unpause()
        speak("Resumed playing.")
    elif "stop" in command:
        pygame.mixer.music.stop()
        speak("Stopped the music.")
    elif "next" in command:
        current_index = (current_index + 1) % len(playlist)
        play_song(current_index)
    elif "previous" in command:
        current_index = (current_index - 1) % len(playlist)
        play_song(current_index)
    elif "exit" in command or "quit" in command:
        speak("Goodbye! Assistant stopped.")
        assistant_active = False
    else:
        speak("Sorry, I don't understand that command.")

def main():
    speak("VibeSync Voice Assistant is ready.")
    while assistant_active:
        command = listen()
        if command:
            handle_command(command)
        time.sleep(1)  # Slight delay to avoid rapid loops

if __name__ == "__main__":
    main()
