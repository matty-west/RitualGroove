import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Replace with your Spotify API credentials
client_id = "" 
client_secret = ""

# Authentication
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def analyze_album(album_id):
    """
    Analyzes all tracks in a given Spotify album.

    Args:
        album_id (str): The Spotify ID of the album.

    Returns:
        pandas.DataFrame: A DataFrame containing audio analysis features for each track.
    """

    try:
        # Get album tracks
        results = sp.album_tracks(album_id)
        track_ids = [track['id'] for track in results['items']]
        print(f"Retrieved {len(track_ids)} tracks from album.")  # Debug: Print number of tracks

        # Analyze each track
        analysis_data = []
        for track_id in track_ids:
            print(f"Analyzing track: {track_id}")  # Debug: Print track ID
            analysis = sp.audio_analysis(track_id)
            print(analysis)
            track_features = {
                "track_id": track_id,
                "tempo": analysis['track']['tempo'],
                "key": analysis['track']['key'],
                "time_signature": analysis['track']['time_signature'],
                "loudness": analysis['track']['loudness'],
                "mode": analysis['track']['mode'],  # Major or minor
                "danceability": analysis['track']['danceability'],  # Access from analysis['track']
                "energy": analysis['track']['energy'],          # Access from analysis['track']
                "speechiness": analysis['track']['speechiness'],    # Access from analysis['track']
                "acousticness": analysis['track']['acousticness'],  # Access from analysis['track']
                "instrumentalness": analysis['track']['instrumentalness'], # Access from analysis['track']
                "liveness": analysis['track']['liveness'],        # Access from analysis['track']
                "valence": analysis['track']['valence']         # Access from analysis['track']
            }
            analysis_data.append(track_features)

        df = pd.DataFrame(analysis_data)
        print(f"DataFrame length: {len(df)}")  # Check DataFrame length
        print(df.head().to_markdown(index=False, numalign="left", stralign="left"))  # Print first few rows as markdown
        return df

    except Exception as e:
        print(f"An error occurred: {e}")  # Catch and print any exceptions
        return None

# Example usage
album_id = "6GH7LVJh3U99L6phiXiUrE"  # Replace with a Spotify album ID
df = analyze_album(album_id)
if df is not None:
    print(df.to_markdown(index=False, numalign="left", stralign="left"))  # Display as markdown
