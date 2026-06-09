# 🎵 Music Player

A web-based music player built with **Python (Flask)** and a **C backend** that manages the playlist using a **doubly linked list** data structure. The C program is compiled and executed at runtime by the Flask server.

---

## Features

- Play, pause, and navigate songs (next / previous)
- Add songs to the playlist from a pre-loaded song catalogue (Excel)
- Delete songs from the playlist
- Playlist persisted to a text file via a C program
- Audio continues playing without restarting when songs are added or deleted
- Auto-advances to the next song when the current one ends

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Data Structure | Doubly Linked List (C) |
| Frontend | HTML, CSS, Jinja2 |
| Data | Excel (songs catalogue via pandas), plain text (playlist) |

---

## Project Structure

```
music-player/
├── app.py               # Flask application
├── dsa.c                # C program — doubly linked list for playlist management
├── songs.xlsx           # Song catalogue (name, artist, file path)
├── playlist.txt         # Persisted playlist (runtime generated)
├── templates/
│   └── index.html       # Main UI
├── static/
│   ├── hello.css        # Stylesheet
│   └── audio/           # Place your .mp3 files here
│       ├── audio1.mp3
│       ├── audio2.mp3
│       └── audio3.mp3
└── requirements.txt
```

---

## How It Works

1. On startup, Flask compiles `dsa.c` into `dsa.exe` using GCC
2. When a song is added or deleted, Flask calls `dsa.exe` with arguments
3. The C program loads `playlist.txt` into a doubly linked list, modifies it, and saves it back
4. The frontend reads the updated playlist and renders it via Jinja2 templates

---

## Setup & Run

### Prerequisites
- Python 3.x
- GCC (MinGW on Windows)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/music-player.git
cd music-player

# 2. Install Python dependencies
pip install flask psutil pandas openpyxl

# 3. Add your .mp3 files to static/audio/
#    and update songs.xlsx with their names and paths

# 4. Run the app
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

---

## Requirements

```
flask
psutil
pandas
openpyxl
```

> GCC must be installed and available in your system PATH for the C program to compile on startup.
