# Spotify Playlist Report Generator

## Setting up Spotify Developer Access:
- go to Spotify for Developers Dashboard: https://developer.spotify.com/dashboard
- _Create app_
  - enter name and description
  - Redirect URI: http://127.0.0.1:8888/callback/ (8888 for spotipy's temporary server)(localhost no longer allowed)
  - check Web API
  - _Save_

## Authentication
To use Spotify Web API, the app needs permission from a logged in Spotify user
- install spotipy: (will be in requirements.txt)
  - `pip install spotipy --upgrade`
- client ID and client secret need to be set as environment variables
  - `pip install python-dotenv`
  - create `.env` file
  - create `.gitignore` to keep private
    - add `.env` to it
- can then set client id, client secret and redirect URI in script

## Get playlist data
spotipy documentation: https://spotipy.readthedocs.io/en/2.25.1/
- define the `playlist` as an argument to be given when script is run
  - `parser = argparse.ArgumentParser(description="Generate a Spotify playlist report.")`
  - `parser.add_argument("--playlist", type=str, required=True, help="Spotify playlist URL or ID")`
- parse:
  - `args = parser.parse_args()`
- get playlist from parsed args:
  - `playlist_input = args.playlist`
- check if a link was given, and strip down to playlist ID if so
- use spotipy to put tracks into list that contains a dictionary of details for each one
- check all tracks are valid - some may be stored locally or unavailable in region

## Analyse
Since there is no longer access to audio features, do what we can with basic info
- convert tracks to a pandas dataframe
- set up a pdf for the report with reportlab