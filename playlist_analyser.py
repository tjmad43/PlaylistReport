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
from pathlib import Path

# Load variables from .env
load_dotenv()

# --- Authentication ---
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private",
    cache_path=".cache"
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



# --- Organisation ---

# Convert to dataframe
df = pd.DataFrame(tracks)

# Convert duration ms -> mins
df["duration_min"] = df["duration_ms"] / 60000

# Set up folder for diagrams & report
folder_name = "playlist_report"
output_folder = Path(folder_name)
output_folder.mkdir(exist_ok=True)

pie_path = output_folder / "explicit_pie_chart.png"
popularity_path = output_folder / "popularity_chart.png"
duration_path = output_folder / "duration_line_chart.png"
top_artists_path = output_folder / "top_artists_chart.png"
top_albums_path = output_folder / "top_albums_chart.png"
pdf_path = output_folder / "playlist_report.pdf"

# Set up PDF for report
doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
styles = getSampleStyleSheet()
elements = []



# --- Visualise ---

spoticolor1 = "#1DB954"
spoticolor2 = "#212121"
spoticolor3 = "#B3B3B3"

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
explicit_counts = df['explicit'].value_counts()
plt.figure(figsize=(6,6))
plt.pie(
    explicit_counts,
    labels=['Explicit', 'Clean'],
    autopct='%1.1f%%',
    colors=[spoticolor1, spoticolor3],
    startangle=90
)
plt.title("Explicit vs Clean Tracks")
plt.savefig(pie_path)
plt.close()
elements.append(Image(pie_path, width=400, height=400))
elements.append(Spacer(1, 30))


# Popularity
plt.figure(figsize=(6,4))
df["popularity"].plot(kind="hist", bins=10, edgecolor=spoticolor2, color=spoticolor1)
plt.title("Track Popularity Distribution")
plt.xlabel("Popularity")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(popularity_path)
plt.close()
elements.append(Image(popularity_path, width=400, height=300))
elements.append(Spacer(1, 30))

# Duration
plt.figure(figsize=(10,5))
plt.plot(df["position"], df["duration_min"], marker='o', linestyle='-', color=spoticolor1)
plt.title("Track Duration Across Playlist")
plt.xlabel("Track Position")
plt.ylabel("Duration (minutes)")
plt.grid(True)
plt.tight_layout()
plt.savefig(duration_path)
plt.close()
elements.append(Image(duration_path, width=480, height=300))
elements.append(Spacer(1, 30))


# Top artists
# Number of tracks per artist
artist_counts = df['artist'].value_counts()

# Get top 5 artists
top_artists = artist_counts.head(5)

plt.figure(figsize=(8,5))
top_artists.plot(kind="bar", color=spoticolor1)
plt.title("Top Artists in Playlist")
plt.xlabel("Artist")
plt.ylabel("Number of Tracks")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(top_artists_path)
plt.close()
elements.append(Image(top_artists_path, width=450, height=300))
elements.append(Spacer(1, 30))


# Top albums
# Number of tracks per album
album_counts = df['album'].value_counts()

# Get top 5 albums
top_albums = album_counts.head(5)

plt.figure(figsize=(8,5))
top_albums.plot(kind="bar", color=spoticolor1)
plt.title("Top Albums in Playlist")
plt.xlabel("Album")
plt.ylabel("Number of Tracks")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(top_albums_path)
plt.close()
elements.append(Image(top_albums_path, width=450, height=300))



# Build PDF
doc.build(elements)
print(f"Report saved to {pdf_path}")