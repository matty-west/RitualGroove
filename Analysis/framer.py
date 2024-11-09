import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from dotenv import load_dotenv
import os
from tqdm import tqdm  # Import tqdm for the progress bar
import time
from requests.exceptions import RequestException

load_dotenv()  # Load environment variables from .env

client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

scope = "user-top-read user-library-read playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri="http://localhost:8888/",  # Or your specific redirect URI
                                                scope=scope))

def get_playlist_tracks(sp, playlist_name):
    """
    Gets all tracks from a specific playlist.

    Args:
      sp: The Spotipy object.
      playlist_name: The name of the playlist.

    Returns:
      A list of dictionaries, where each dictionary contains information about a track.
    """
    all_tracks = []
    playlists = sp.current_user_playlists()

    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:  # Check if the playlist name matches
            results = sp.playlist_tracks(playlist['id'])
            tracks = results['items']
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])

            for track in tracks:
                track_info = track['track']
                all_tracks.append({
                    'playlist_name': playlist['name'],
                    'track_name': track_info['name'],
                    'artist': track_info['artists'][0]['name'],
                    'album': track_info['album']['name'],
                    'track_id': track_info['id'],
                    'popularity': track_info['popularity']
                })
            break  # Exit the loop once the playlist is found

    return all_tracks

def enrich_with_audio_features(sp, all_tracks):
    """
    Enriches track information with audio features.

    Args:
      sp: The Spotipy object.
      all_tracks: A list of dictionaries, where each dictionary contains information about a track.
    """
    track_ids = [track['track_id'] for track in all_tracks]
    audio_features = []

    for track_id in tqdm(track_ids, desc="Fetching audio features"):
        retries = 3  # Number of retries
        delay = 1  # Initial delay in seconds

        for _ in range(retries):
            try:
                features = sp.audio_features(track_id)[0]
                audio_features.append(features)
                break  # Break out of the retry loop if successful
            except RequestException as e:
                if e.response is not None and e.response.status_code == 429:
                    print(f"Rate limit hit. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff: double the delay
                else:
                    raise  # Raise other exceptions
        else:
            print(f"Failed to fetch audio features for track ID: {track_id} after multiple retries.")

    for track, features in zip(all_tracks, audio_features):
        if features:
            track.update(features)

def main():
    global sp
    playlist_name = "4TC"  # Replace with the actual name of your playlist
    all_tracks = get_playlist_tracks(sp, playlist_name)
    enrich_with_audio_features(sp, all_tracks)

    df = pd.DataFrame(all_tracks)
    print(df.head())

    df.to_csv('4TC_playlist.csv', index=False) 
    df.to_pickle('4TC_playlist.pkl')
    
if __name__ == "__main__":
    main()