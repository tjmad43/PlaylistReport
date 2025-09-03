# Spotify playlist report script
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Load variables from .env
load_dotenv()

# Authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private"
))
# check it worked
print("Authenticated as:", sp.current_user()['display_name'])



# Get playlist data
# Define playlist as an argument the user has to provide
parser = argparse.ArgumentParser(description="Generate a Spotify playlist report.")
parser.add_argument("--playlist", type=str, required=True, help="Spotify playlist URL or ID")
# Parse the argument
args = parser.parse_args()

# Get the playlist input from the parsed arguments
playlist_input = args.playlist

# Get playlist ID if link was given
if "playlist" in playlist_input:
    playlist_id = playlist_input.split("/")[-1].split("?")[0]
else:
    playlist_id = playlist_input

print(f"Using playlist ID: {playlist_id}")

# Get tracks from playlist
results = sp.playlist_items(playlist_id, additional_types=['track'])

tracks = []
count = 0
for item in results['items']:
    track = item['track']
    count +=1
    tracks.append({
        "name": track['name'],
        "artist": track['artists'][0]['name'],
        "album": track['album']['name'],
        "duration_ms": track['duration_ms'],
        "popularity": track['popularity'],
        "id": track['id'],
        "position": count,
        "explicit": track['explicit']
    })

# Check all tracks are valid
valid_track_ids = []
for t in tracks:
    try:
        sp.track(t["id"])
        valid_track_ids.append(t["id"])
    except spotipy.exceptions.SpotifyException as e:
        print(f"Skipping track {t['name']} ({t['id']}): {e}")

# Print info
for i in tracks:
    print(f"{i['position']:>2}. {i['name']} by {i['artist']} "
          f"({i['album']}) - {i['duration_ms']//1000}s, Popularity: {i['popularity']}, Explicit: {i['explicit']}")



# Visualise
