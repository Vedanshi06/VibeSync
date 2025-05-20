from flask import Flask, render_template, jsonify, url_for, request, redirect
from humming_detection import record_chunk, recognize
import os
import random
import subprocess
app = Flask(__name__, static_folder='static', template_folder='templates')

# Home page
@app.route('/')
def index():
    songs = []
    song_folder  = os.path.join(app.static_folder, 'songs')
    cover_folder = os.path.join(app.static_folder, 'covers')

    for filename in os.listdir(song_folder):
        if not filename.lower().endswith('.mp3'):
            continue
        base = os.path.splitext(filename)[0]
        songs.append({
            'name':      base.replace('_', ' ').title(),
            'file_url':  f'songs/{filename}',
            'cover_url': f'covers/{base}.jpg'
        })

    return render_template('index.html', songs=songs)

@app.route('/detect_hum', methods=['POST'])
def detect_hum():
    filename = "static/temp_hum.wav"
    try:
        record_chunk(filename, 15, 44100)
        result = recognize(filename)
        os.remove(filename)
        if result:
            title, artist = result
            return jsonify({'status': 'success', 'title': title, 'artist': artist})
        else:
            return jsonify({'status': 'fail', 'message': 'No match found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Library page
@app.route('/library')
def library():
    return render_template('library.html')

# Playlist page
def get_songs_for_mood(mood):
    music_dir = os.path.join(app.static_folder, 'music', mood)
    try:
        files = [f for f in os.listdir(music_dir) if f.lower().endswith('.mp3')]
    except FileNotFoundError:
        files = []
    songs = [
        {
            'title': os.path.splitext(fname)[0].replace('_', ' ').title(),
            'file': url_for('static', filename=f'music/{mood}/{fname}')
        }
        for fname in files
    ]
    return songs

@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    if request.method == 'POST':
        mood = request.form.get('mood')
        songs = get_songs_for_mood(mood)
        autoplay_url = random.choice(songs)['file'] if songs else None
        return render_template('playlist.html', mood=mood, songs=songs, autoplay=autoplay_url)
    return render_template('playlist.html', mood='', songs=[], autoplay=None)

# @app.route('/detect-emotion', methods=['POST'])
# def detect_emotion():
#     result = subprocess.run(['python', 'emotion_detector.py'], capture_output=True, text=True)
#     print("RAW OUTPUT:", result.stdout)  # <- Debug line
#     mood = result.stdout.strip().split('\n')[-1].lower()
#     songs = get_songs_for_mood(mood)
#     autoplay_url = random.choice(songs)['file'] if songs else None
#     return jsonify({'mood': mood, 'songs': songs, 'autoplay': autoplay_url})

if __name__ == '__main__':
    app.run(debug=True)
