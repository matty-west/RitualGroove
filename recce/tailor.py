import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Spotify API credentials
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')

# Spotify authorization
scope = "playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri="http://localhost:8888/",
                                                scope=scope))

# Load the clustered dataframe
df_clustered = pd.read_csv('Data/clustered_playlist.csv')

def create_playlist(name, track_ids):
    """
    Creates a new playlist and adds tracks to it,
    splitting the track list into smaller chunks if necessary.
    """
    playlist = sp.user_playlist_create(sp.me()['id'], name, public=False)
    chunk_size = 100
    for i in range(0, len(track_ids), chunk_size):
        sp.playlist_add_items(playlist['id'], track_ids[i:i+chunk_size])
    print(f"Created playlist '{name}' with {len(track_ids)} tracks.")

def get_recommendations(seed_tracks, target_attributes):
    """
    Gets song recommendations based on seed tracks and target attributes.
    """
    recommendations = sp.recommendations(seed_tracks=seed_tracks[:5], **target_attributes)
    recommended_tracks = [track['id'] for track in recommendations['tracks']]
    return recommended_tracks

# Define target attributes for each cluster
target_attributes = {
    0: {"target_danceability": 0.7, "target_energy": 0.8},  # Example for Cluster 0
    1: {"target_acousticness": 0.6, "target_valence": 0.4},  # Example for Cluster 1
    2: {"target_tempo": 120, "target_instrumentalness": 0.5},  # Example for Cluster 2
    3: {"target_speechiness": 0.2, "target_liveness": 0.3}  # Example for Cluster 3
}

# Generate recommendation playlists
for cluster_id in df_clustered['cluster'].unique():
    cluster_tracks = df_clustered[df_clustered['cluster'] == cluster_id]['track_id'].tolist()

    # Get recommendations with specific attributes
    recommended_tracks = get_recommendations(cluster_tracks, target_attributes[cluster_id])

    # Create a new playlist with the recommendations
    create_playlist(f"Recs from Cluster {cluster_id} (Tailored)", recommended_tracks)