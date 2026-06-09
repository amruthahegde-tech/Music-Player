import os
import subprocess
import psutil
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

playlist_file = 'playlist.txt'
current_song_file = 'current_song.txt'
songs_file = 'songs.xlsx'

def kill_dsa_process():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'dsa.exe':
            proc.kill()
            print(f"Killed process {proc.info['pid']}")

@app.route('/static/audio/<path:filename>')
def static_audio_files(filename):
    print(f"Serving file: static/audio/{filename}")  # Debug output
    try:
        return send_from_directory('static/audio', filename)
    except Exception as e:
        print(f"Error serving file: {e}")
        return f"Error serving file: {e}", 404

def compile_c_program():
    try:
        kill_dsa_process()  # Kill existing dsa.exe process before attempting to delete

        if os.path.exists('dsa.exe'):  # Ensure the executable is deleted before attempting to compile
            try:
                os.remove('dsa.exe')
                print('Existing dsa.exe deleted.')  # Debug output
            except Exception as e:
                print(f'Failed to delete existing dsa.exe: {e}')
                return f'Failed to delete existing dsa.exe: {e}'

        # Compile the C program
        result = subprocess.run(['gcc', '-o', 'dsa.exe', 'dsa.c'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Compilation failed with error: {result.stderr}")  # Debug output
            return f'Failed to compile dsa.c: {result.stderr}'
        print("Compilation successful")  # Debug output
        return 'Compilation successful'
    except Exception as e:
        print(f'Exception occurred during compilation: {e}')  # Debug output
        return f'Exception occurred during compilation: {e}'

def load_playlist():
    try:
        playlist = []
        if os.path.exists(playlist_file):
            with open(playlist_file, 'r') as f:
                playlist = [line.strip().replace("\\", "/") for line in f.readlines() if '|' in line and line.count('|') == 2]
        
        # Add default songs if the playlist is empty
        if not playlist:
            print("Adding default songs to playlist.")
            default_songs = [
                {"name": "MAYAVI", "artist": "Sonu Nigam,Sanjith Hegde", "url": "audio1.mp3"},
                {"name": "PASOORI", "artist": "Ali Sethi,Shae Gill", "url": "audio2.mp3"},
                {"name": "NADAANIYA", "artist": "Akshath Acharya", "url": "audio3.mp3"}
            ]
            for song in default_songs:
                song_entry = f"{song['name']}|{song['artist']}|{song['url']}"
                playlist.append(song_entry)
            save_playlist(playlist)

        print("Playlist loaded successfully.")  # Debug output
        return list(dict.fromkeys(playlist))  # Remove duplicates and keep the order
    except Exception as e:
        print(f"Failed to load playlist: {e}")
        return []

def save_playlist(playlist):
    try:
        with open(playlist_file, 'w') as f:
            for song in playlist:
                f.write(song + '\n')
        print("Playlist saved successfully.")  # Debug output
    except Exception as e:
        print(f"Failed to save playlist: {e}")

def load_current_song():
    try:
        if os.path.exists(current_song_file):
            with open(current_song_file, 'r') as f:
                current_song = f.read().strip().split('|')
                if len(current_song) == 3:
                    return current_song
        return None
    except Exception as e:
        print(f"Failed to load current song: {e}")
        return None

def save_current_song(song_name, song_artist, song_url):
    try:
        with open(current_song_file, 'w') as f:
            f.write(f"{song_name}|{song_artist}|{song_url}")
        print("Current song saved successfully.")  # Debug output
    except Exception as e:
        print(f"Failed to save current song: {e}")

def clear_current_song():
    try:
        if os.path.exists(current_song_file):
            os.remove(current_song_file)
        print("Current song cleared successfully.")  # Debug output
    except Exception as e:
        print(f"Failed to clear current song: {e}")

def load_songs():
    try:
        print(f"Attempting to read the Excel file: {songs_file}")  # Debug output
        songs = []
        
        if os.path.exists(songs_file):
            songs_df = pd.read_excel(songs_file)
            if not songs_df.empty:
                print(f"Excel file read successfully: {songs_df.head()}")  # Debug output
                songs = songs_df.to_dict(orient='records')
            else:
                print("Excel file is empty.")  # Debug output
        else:
            print(f"Excel file {songs_file} does not exist.")  # Debug output

        # Add default songs if no songs were loaded from the Excel file
        if not songs:
            print("Loading default songs.")
            songs = [
                {"Song Name": "MAYAVI", "Artist": "Sonu Nigam,Sanjith Hegde", "Path": "/audio1.mp3"},
                {"Song Name": "PASOORI", "Artist": "Ali Sethi,Shae Gill", "Path": "/audio2.mp3"},
                {"Song Name": "NADAANIYA", "Artist": "Akshath Acharya", "Path": "/audio3.mp3"}
            ]

        print("Loaded songs:", songs)  # Debug output
        return songs
    except Exception as e:
        print(f"Failed to load songs: {e}")
        return []


@app.route('/', methods=['GET', 'POST'])
def index():
    compile_result = compile_c_program()
    if compile_result != 'Compilation successful':
        return compile_result, 500

    song_name = request.args.get('song_name', '')

    if request.method == 'POST':
        if 'song_name' in request.form:
            song_name = request.form.get('song_name')
            print(f"Song name from form: {song_name}")  # Debug output

        if 'add_song' in request.form:
            song_name = request.form.get('song_name')
            song_artist = request.form.get('song_artist')
            song_url = request.form.get('song_url')
            song_url = song_url.replace("\\", "/").lstrip("/") # Normalize path to use forward slashes
            print(f"Received song details - Name: {song_name}, Artist: {song_artist}, URL: {song_url}")  # Debug output
            if song_name and song_artist and song_url:
                playlist = load_playlist()
                song_entry = f"{song_name}|{song_artist}|{song_url}"
                if song_entry.strip() not in [s.strip() for s in playlist]:
                    playlist.append(song_entry.strip())
                    save_playlist(playlist)

                    executable_path = os.path.abspath("dsa.exe")
                    try:
                        result = subprocess.run([executable_path, song_name, song_artist, song_url], capture_output=True, text=True, timeout=10)
                        print(f"dsa.exe run result: {result.stdout}")  # Debug output
                        if result.returncode != 0:
                            return f'Failed to add song: {result.stderr}', 400
                    except subprocess.TimeoutExpired:
                        return 'dsa.exe process timed out', 500
                    except Exception as e:
                        print(f'Exception occurred: {e}')  # Debug output
                        return f'Exception occurred: {e}', 500
            else:
                print("All fields are required")  # Debug output
                return 'All fields are required', 400

        if 'play_song' in request.form:
            song_name = request.form.get('song_name')
            song_artist = request.form.get('song_artist')
            song_url = request.form.get('song_url')
            save_current_song(song_name, song_artist, song_url)
            return redirect(url_for('index'))

    current_song = load_current_song()
    songs = load_songs()
    print(f"Requested song name: {song_name}")  # Debug output
    song_details = next((song for song in songs if song['Song Name'] == song_name), {})
    print(f"Song details to autofill: {song_details}")  # Debug output

    try:
        playlist = load_playlist()
        return render_template('index.html', playlist=playlist, current_song=current_song, songs=songs, song_details=song_details)
    except Exception as e:
        print(f"Exception occurred: {e}")  # Debug output
        return f'Exception occurred: {e}', 500

@app.route('/delete_song', methods=['POST'])
def delete_song():
    compile_result = compile_c_program()
    if compile_result != 'Compilation successful':
        return compile_result, 500

    song_name = request.form.get('song_name')
    if not song_name:
        return 'Song name is required', 400

    print(f"Deleting song: {song_name}")  # Debug output
    executable_path = os.path.abspath("dsa.exe")
    try:
        result = subprocess.run([executable_path, 'delete', song_name], capture_output=True, text=True, timeout=10)
        print(result.stdout)  # Debug output
        if result.returncode != 0:
            print(f"Failed to delete song: {result.stderr}")  # Debug output
            return f'Failed to delete song: {result.stderr}', 400
    except subprocess.TimeoutExpired:
        return 'dsa.exe process timed out', 500
    except Exception as e:
        print(f"Exception occurred: {e}")  # Debug output
        return f'Exception occurred: {e}', 500

    playlist = load_playlist()
    playlist = [song for song in playlist if not song.startswith(f"{song_name}|")]
    save_playlist(playlist)

    if not playlist:
        clear_current_song()

    print("Song deleted and playlist updated.")  # Debug output
    return redirect(url_for('index'))

@app.route('/next_song')
def next_song():
    current_song = load_current_song()
    playlist = load_playlist()
    if current_song and playlist:
        try:
            current_index = playlist.index('|'.join(current_song))
            next_index = (current_index + 1) % len(playlist)
            next_song = playlist[next_index].split('|')
            save_current_song(next_song[0], next_song[1], next_song[2])
        except ValueError:
            pass  # Current song not in playlist
    return redirect(url_for('index'))

@app.route('/previous_song')
def previous_song():
    current_song = load_current_song()
    playlist = load_playlist()
    if current_song and playlist:
        try:
            current_index = playlist.index('|'.join(current_song))
            previous_index = (current_index - 1) % len(playlist)
            previous_song = playlist[previous_index].split('|')
            save_current_song(previous_song[0], previous_song[1], previous_song[2])
        except ValueError:
            pass  # Current song not in playlist
    return redirect(url_for('index'))

@app.route('/playlist')
def playlist():
    compile_result = compile_c_program()
    if compile_result != 'Compilation successful':
        return compile_result, 500

    try:
        playlist = load_playlist()
        return render_template('playlist.html', playlist=playlist)
    except Exception as e:
        print(f"Exception occurred: {e}")  # Debug output
        return f'Exception occurred: {e}', 500

if __name__ == '__main__':
    app.run(debug=True)