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


results = sp.playlist_items(playlist_id, additional_types=['track'])

tracks = []
for item in results['items']:
    track = item['track']
    tracks.append({
        "name": track['name'],
        "artist": track['artists'][0]['name'],
        "album": track['album']['name'],
        "duration_ms": track['duration_ms'],
        "popularity": track['popularity'],
        "id": track['id']
    })


# Get audio features
track_ids = [t["id"] for t in tracks if t["id"]]
features = sp.audio_features(track_ids)

for i, feat in enumerate(features):
    if feat:  # Sometimes a track may not have features
        tracks[i].update({
            "danceability": feat['danceability'],
            "energy": feat['energy'],
            "tempo": feat['tempo'],
            "valence": feat['valence']
        })


# Analyse
df = pd.DataFrame(tracks)

print(df.head())
print("\nAverage tempo:", df['tempo'].mean())
print("Most popular artist:", df['artist'].mode()[0])


# Visualise
# Histogram of tempos
plt.hist(df['tempo'].dropna(), bins=20, edgecolor='black')
plt.title("Tempo Distribution")
plt.xlabel("Tempo (BPM)")
plt.ylabel("Number of Tracks")
plt.show()

# Bar chart of top 5 artists
df['artist'].value_counts().head(5).plot(kind='bar')
plt.title("Top 5 Artists in Playlist")
plt.show()