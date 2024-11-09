import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import altair as alt

# Load the dataframe
df = pd.read_pickle('Data/4TC_playlist.pkl')

# Select the columns for clustering
df_numeric = df[['popularity', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']].copy()

# Scale the numeric features
scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df_numeric), columns=df_numeric.columns)

# Fit KMeans with 4 clusters
kmeans = KMeans(n_clusters=4, random_state=42)
df_clustered = df.copy()
df_clustered['cluster'] = kmeans.fit_predict(df_scaled)

df_clustered.to_csv('Data/clustered_playlist.csv', index=False)