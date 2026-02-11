import spotipy
from spotipy.oauth2 import SpotifyOAuth
import statistics
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import requests
import random

scope = "user-top-read user-library-read playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="",
                                               client_secret="",
                                               redirect_uri="http://localhost:8888/",
                                               scope=scope))

user = sp.current_user()
print(user['display_name'])

top_tracks = sp.current_user_top_tracks(limit=50)
audio_features = sp.audio_features([track['id'] for track in top_tracks['items']])

for feature in audio_features[0].keys():
    if feature in ['duration_ms', 'mode', 'type', 'id', 'uri', 'track_href', 'analysis_url']:
        continue

    feature_values = [features[feature] for features in audio_features if isinstance(features[feature], (int, float))]
    if feature_values:
        avg_feature = statistics.mean(feature_values)
        #print(f"Average {feature} of your top tracks: {avg_feature}")

all_feature_data = []
for track, features in zip(top_tracks['items'], audio_features):
    track_data = {'track_name': track['name'], 'artist': track['artists'][0]['name'], 'artist_id': track['artists'][0]['id']}
    track_data.update(features)
    all_feature_data.append(track_data)

df = pd.DataFrame(all_feature_data)

features = ['danceability', 'energy', 'valence', 'tempo', 'key']
X = df[features].values

optimal_k = 5
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

for cluster_id in range(optimal_k):
    cluster_tracks = df[df['cluster'] == cluster_id]

    for feature in features:
        mean_value = cluster_tracks[feature].mean()

playlists = sp.current_user_playlists()
random_playlist = random.choice(playlists['items'])
tracks = sp.playlist_tracks(random_playlist['id'])
random_track = random.choice(tracks['items'])['track']
artist_id = random_track['artists'][0]['id']

target_cluster = random.choice(df['cluster'].unique())
cluster_tracks = df[df['cluster'] == target_cluster]
random_track = cluster_tracks.sample(1).iloc[0]
artist_id = random_track['artist_id']
genres = sp.recommendation_genre_seeds()['genres']
random_genre = random.choice(genres)

cluster_means = df[df['cluster'] == target_cluster][features].mean()

access_token = sp.auth_manager.get_access_token(as_dict=False)

url = "https://api.spotify.com/v1/recommendations"

headers = {
    "Authorization": f"Bearer {access_token}",
}

# Category IDs for "New Releases" and "Trending"
new_releases_category_id = "0JQ5DAqbMKFGaKcChsSgUO"
trending_category_id = "0JQ5DAqbMKFQIL0AXnG5AK"

# Fetch tracks from these categories
new_releases_playlist_id = sp.category_playlists(category_id=new_releases_category_id, limit=1)['playlists']['items'][0]['id']
trending_playlist_id = sp.category_playlists(category_id=trending_category_id, limit=1)['playlists']['items'][0]['id']

# Extract track IDs (assuming the first track in each playlist)
new_release_track_id = sp.playlist_tracks(new_releases_playlist_id)['items'][0]['track']['id']
trending_track_id = sp.playlist_tracks(trending_playlist_id)['items'][0]['track']['id']

params = {
    "seed_artists": [artist_id],
    "seed_tracks": [random_track['id'], new_release_track_id, trending_track_id],
    "seed_genres": [random_genre],
    "target_danceability": cluster_means['danceability'],
    "target_energy": cluster_means['energy'],
    "target_valence": cluster_means['valence'],
    "target_tempo": cluster_means['tempo'],
    "target_key": int(cluster_means['key']),
    "limit": 10
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    recommendations = response.json()

    playlist_tracks = []
    for playlist in sp.current_user_playlists()['items']:
        playlist_tracks.extend(sp.playlist_tracks(playlist['id'])['items'])

    playlist_track_ids = {track['track']['id'] for track in playlist_tracks}

    filtered_recommendations = sorted(
        (track for track in recommendations['tracks'] if track['id'] not in playlist_track_ids),
        key=lambda track: track['popularity'],
        reverse=True
    )

    for track in filtered_recommendations:
        print(f"{track['name']} by {track['artists'][0]['name']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
