import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:8888",
                                               scope="user-library-read"))

# Replace with a track ID from the failed list
track_id = "6cV43RzcqQMmA48Y8heq3A"  

track = sp.track(track_id)
print(f"Track: {track['name']} by {track['artists'][0]['name']}")
print(f"Track genres: {track.get('genres')}")

artist_id = track['artists'][0]['id']
artist = sp.artist(artist_id)
print(f"Artist genres: {artist.get('genres')}")