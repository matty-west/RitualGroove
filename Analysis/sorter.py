import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
from dotenv import load_dotenv  
import logging

load_dotenv()  # Load environment variables from .env

client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

scope = scope = "user-top-read user-library-read playlist-modify-private"  

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                               client_secret=client_secret, 
                                               redirect_uri="http://localhost:8888/",
                                               scope=scope))

def get_all_tracks_from_playlists(sp):
    """
    Fetches all tracks from the user's playlists.

    Args:
      sp: The authenticated Spotipy object.

    Returns:
      A list of track dictionaries.
    """
    all_tracks = []
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        results = sp.playlist_tracks(playlist['id'])
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        for track in tracks:
            track_info = track.get('track')
            if track_info and isinstance(track_info.get('id'), str):  # Check if 'id' is a string
                all_tracks.append({
                    'id': track_info['id'],
                    'name': track_info['name'],
                    'artist': track_info['artists'][0]['name'],
                    'album': track_info['album']['name']
                })
    return all_tracks

def get_track_genres(sp, track_ids):
    """
    Fetches genre information for the given tracks.
    Tries to get the artist's genre if no genre is found for the track.
    If no genre is found for both track and artist, returns 'unknown'.

    Args:
      sp: The authenticated Spotipy object.
      track_ids: A list of track IDs.

    Returns:
      A dictionary mapping track IDs to lists of genres.
    """
    track_genres = {}
    for i in range(0, len(track_ids), 50):
        batch_ids = track_ids[i:i + 50]
        try:
            tracks = sp.tracks(batch_ids)
            for track in tracks['tracks']:
                if 'genres' in track and track['genres']:
                    track_genres[track['id']] = track['genres']
                else:
                    artist_id = track['artists'][0]['id']
                    artist = sp.artist(artist_id)
                    if 'genres' in artist and artist['genres']:
                        track_genres[track['id']] = artist['genres']
                        logging.info(f"Using artist genres for track ID: {track['id']}")
                    else:
                        track_genres[track['id']] = ['unknown']  # Assign 'unknown' genre
                        logging.warning(f"No genre information found for track ID: {track['id']}")
        except Exception as e:
            logging.error(f"Error fetching genre information: {e}")
    return track_genres

# Get all tracks from playlists
all_tracks = get_all_tracks_from_playlists(sp)

# Get track IDs
track_ids = [track['id'] for track in all_tracks]

# Get genre information for all tracks
track_genres = get_track_genres(sp, track_ids)

# Create a DataFrame with track information and genres
df = pd.DataFrame(all_tracks)
df['genres'] = df['id'].map(track_genres)

print(df.head())

def create_genre_playlists(sp, df):
    """
    Creates genre-specific playlists from the given DataFrame.

    Args:
        sp: The authenticated Spotipy object.
        df: The DataFrame containing track information and genres.
    """
    playlists = {}  # Dictionary to store playlists by genre

    # Gather all unique genres
    all_genres = []
    for index, row in df.iterrows():
        genres = row['genres']
        if genres and isinstance(genres, list):
            all_genres.extend(genres)
    unique_genres = list(set(all_genres))  # Get unique genres

    # Create playlists for each genre
    for genre in unique_genres:
        playlist_name = f"{genre} - RitualGroove"
        playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_name, public=False)
        playlists[genre] = playlist['id']

    # Add tracks to playlists
    for index, row in df.iterrows():
        track_id = row['id']
        track_name = row['name']
        track_uri = f"spotify:track:{track_id}"
        genres = row['genres']
        if genres and isinstance(genres, list):
            for genre in genres:
                if genre in playlists:  # Check if playlist exists
                    sp.playlist_add_items(playlist_id=playlists[genre], items=[track_uri])
                    print(f"Added '{track_name}' to '{genre} - RitualGroove'")


# Create genre-specific playlists
#create_genre_playlists(sp, df)