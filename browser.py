import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-top-read user-library-read playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="e71190aac1b74450861923dcffa6295e",
                                               client_secret="0a8d73bd89b74a12bb9f06cdcc91845a",
                                               redirect_uri="http://localhost:8888/",
                                               scope=scope))

# Get available genre seeds
genre_seeds = sp.recommendation_genre_seeds()
print("Available Genre Seeds:")
for genre in genre_seeds['genres']:
    print(genre)

# Get available categories
categories = sp.categories(limit=50)  # Fetch up to 50 categories
print("\nAvailable Categories:")
for category in categories['categories']['items']:
    print(f"{category['name']} - {category['id']}")