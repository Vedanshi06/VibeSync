import speech_recognition as sr
import pyttsx3
import os
import pygame
import time

# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Initialize Pygame for music
pygame.init()
pygame.mixer.init()

# Music folder path
MUSIC_FOLDER = "music"

# Ensure the music folder exists
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)
    engine.say("Music folder created. Please add some songs and restart the assistant.")
    engine.runAndWait()
    exit()

# Load playlist
playlist = [song for song in os.listdir(MUSIC_FOLDER) if song.endswith('.mp3')]
print("Playlist loaded:", playlist)  # Debug print

if not playlist:
    engine.say("No songs found in the music folder. Please add some songs and restart the assistant.")
    engine.runAndWait()
    exit()

current_index = 0

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(timeout=6):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return None
        except sr.RequestError:
            speak("Speech service is unavailable.")
            return None
        except sr.WaitTimeoutError:
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

    elif "list songs" in command:
        speak("Here are the available songs:")
        for i, song in enumerate(playlist, 1):
            speak(f"{i}. {song}")

    elif "play" in command:
        song_name = command.replace("play", "").strip().lower()
        found = False
        for i, song in enumerate(playlist):
            if song_name in song.lower():
                play_song(i)
                found = True
                break
        if not found:
            speak("Song not found in playlist.")

    elif "exit" in command or "quit" in command:
        speak("Goodbye!")
        exit()

    else:
        speak("Sorry, I don't understand that command.")

# Main Loop
speak("VibeSync Voice Assistant is ready.")

while True:
    if not pygame.mixer.music.get_busy():  # Listen only when music is not playing
        user_command = listen(timeout=6)
        if user_command:
            handle_command(user_command)
        else:
            speak("No command detected. I'll keep waiting.")
    else:
        time.sleep(1)
