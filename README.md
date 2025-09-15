# Spotify Playlist Report Generator

A Python tool that connects to the Spotify API and generates PDF reports for any playlist.  
The report includes playlist details, summary statistics, tables, and visualizations such as:

- Track duration trends (line chart)  
- Explicit vs clean tracks (pie chart)  
- Top artists (bar chart)  
- Top albums (bar chart)  
- Popularity scores  

Built with **Spotipy**, **Pandas**, **Matplotlib**, and **ReportLab**.

---

## Features
- Authenticate with your Spotify account
- Fetch playlist data (name, description, tracks, artists, albums, popularity, duration, explicit flag)
- Generate charts and tables with Matplotlib + Pandas
- Export a multi-page PDF report
- Organize outputs neatly in a playlist-specific folder

---

## Output
- Call as `python playlist_analyser.py --playlist <ID or "link">`
- Folder will be created called `playlist_report - <playlist name>` containing the chart images and the full report `playlist_report.pdf`
