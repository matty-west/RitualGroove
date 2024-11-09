import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

scope = scope = "user-top-read user-library-read playlist-modify-private"  

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

def get_recommendations(track_ids):
    """
    Gets song recommendations based on seed tracks.
    """
    recommendations = sp.recommendations(seed_tracks=track_ids[:5])
    recommended_tracks = [track['id'] for track in recommendations['tracks']]
    return recommended_tracks

# Create playlists for each cluster
for cluster_id in df_clustered['cluster'].unique():
    cluster_tracks = df_clustered[df_clustered['cluster'] == cluster_id]['track_id'].tolist()
    create_playlist(f"Cluster {cluster_id}", cluster_tracks)

    # Use the cluster playlist as a seed for a new playlist
    recommended_tracks = get_recommendations(cluster_tracks)
    create_playlist(f"Recommendations from Cluster {cluster_id}", recommended_tracks)