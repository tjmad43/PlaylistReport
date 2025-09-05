# Spotify playlist report script
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib import colors

# Load variables from .env
load_dotenv()

# --- Authentication ---
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private",
    cache_path=".spotifycache"
))
# Check it worked
print("Authenticated as:", sp.current_user()['display_name'])



# --- Get playlist data ---
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
plname = sp.playlist(playlist_id)["name"]

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

# Check for invalid tracks
valid_track_ids = []
for t in tracks:
    try:
        sp.track(t["id"])
        valid_track_ids.append(t["id"])
    except spotipy.exceptions.SpotifyException as e:
        print(f"Track {t['name']}, ({t['id']}) not valid: {e}")



# --- Visualise ---
# Convert to dataframe
df = pd.DataFrame(tracks)

# Convert duration ms -> mins
df["duration_min"] = df["duration_ms"] / 60000

# Set up PDF for report
filename = "playlist_report.pdf"
doc = SimpleDocTemplate(filename, pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# Title
elements.append(Paragraph("Spotify Playlist Report - " + plname, styles["Title"]))
elements.append(Spacer(1, 20))

# Summary
total_tracks = len(df)
avg_popularity = df["popularity"].mean()
avg_duration = df["duration_min"].mean()

summary_text = f"""
<b>Total tracks:</b> {total_tracks}<br/>
<b>Average popularity:</b> {avg_popularity:.1f}<br/>
<b>Average duration:</b> {avg_duration:.2f} minutes<br/>
"""
elements.append(Paragraph(summary_text, styles["Normal"]))
elements.append(Spacer(1, 20))

# Table of tracks
table_data = [["#", "Track", "Artist", "Album"]]
for _, row in df.iterrows():
    table_data.append([row["position"], row["name"], row["artist"], row["album"]])

table = Table(table_data, colWidths=[30, 190, 120, 170])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
]))
elements.append(table)
elements.append(Spacer(1, 30))


# Explicit?


# Popularity


# Duration


# Top artist(s)


# Top album(s)




# Build PDF
doc.build(elements)
print(f"Report saved as {filename}")