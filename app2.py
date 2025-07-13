import base64
import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from streamlit_lottie import st_lottie

# Spotify API credentials
CLIENT_ID = "bceab9d31ba84f14a439cd894d322aa9"
CLIENT_SECRET = "d2cb6d92f4fe4351b84e74625f07c9ac"

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Fetch top tracks of an artist
def get_artist_top_tracks(artist_name):
    results = sp.search(q=artist_name, type="artist")
    if results and results["artists"]["items"]:
        artist = results["artists"]["items"][0]
        top_tracks = sp.artist_top_tracks(artist['id'])
        tracks = [(track['name'], track['preview_url'], track['external_urls']['spotify']) for track in top_tracks['tracks']]
        return tracks
    else:
        return []

# Fetch artist image
def get_artist_image(artist_name):
    results = sp.search(q=artist_name, type="artist")
    if results and results["artists"]["items"]:
        artist = results["artists"]["items"][0]
        if artist["images"]:
            return artist["images"][0]["url"]
        else:
            return None
    else:
        return None

# Get album cover for song
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

# Song recommendation logic
def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        song_name = music.iloc[i[0]].song
        album_cover_url = get_song_album_cover_url(song_name, artist)
        recommended_music.append((song_name, album_cover_url))
    return recommended_music

# Streamlit app configuration
st.set_page_config(page_title="Song Recommender", page_icon=":musical_note:")

# CSS styling
st.markdown("""
    <style>
    .recommendation {
        text-align: center;
    }
    .song-title {
        font-weight: bold;
    }
    .centered-header {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: red;
        margin-bottom: 1em;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: black;
        text-align: center;
        padding: 10px;
        color: yellow;
    }
    .artist-column {
        padding-bottom: 20px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# App header
st.markdown('<div class="centered-header">🎵 Song Recommender Model 🎵</div>', unsafe_allow_html=True)

# Load recommendation data
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Lottie animation
lottie_url = "https://lottie.host/43dd85bb-1e38-4038-aaa5-cead040c6532/pffTbodcEz.json"
st_lottie(lottie_url, height=200)

# Song selection
music_list = music['song'].values
selected_song = st.selectbox("Type or select a song from the dropdown", music_list)

# Show recommendations
if st.button('Show Recommendation'):
    with st.spinner('Fetching recommendations...'):
        recommended_music = recommend(selected_song)

    st.write("")
    st.write("")
    for song_name, album_cover_url in recommended_music:
        st.markdown(f'<p style="color:yellow; font-weight:bold; font-size:1.2em;">{song_name}</p>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(album_cover_url, width=100)

        with col2:
            track = sp.search(q=song_name, type="track")["tracks"]["items"][0]
            artist = track["artists"][0]["name"]
            album = track["album"]["name"]
            release_date = track["album"]["release_date"]
            preview_url = track["preview_url"]
            external_url = track["external_urls"]["spotify"]

            st.text(f"Artist: {artist}")
            st.text(f"Album: {album}")
            st.text(f"Release Date: {release_date}")

            if preview_url:
                st.audio(preview_url, format='audio/mp3')
            else:
                st.text("Preview not available")

            st.markdown(f'<a href="{external_url}" style="color:yellow; font-weight:bold;">Listen on Spotify</a>', unsafe_allow_html=True)
            st.markdown("---")

# Top artists list
top_20_artists = [
    'Michael Jackson', 'The Beatles', 'Queen', 'Elvis Presley', 'Taylor Swift',
    'Ariana Grande', 'Ed Sheeran', 'Justin Bieber', 'Rihanna', 'Eminem',
    'Lady Gaga', 'Madonna', 'Whitney Houston', 'Coldplay', 'Linkin Park',
    'Beyoncé', 'Maroon 5', 'Adele', 'Katy Perry', 'Bruno Mars'
]

# Toggle artist section
show_artists_section = st.checkbox("Show Top 20 Artists Section")
if show_artists_section:
    st.markdown('<div class="centered-header">🎤 Top 20 Artists 🎤</div>', unsafe_allow_html=True)

    if 'top_tracks_display' not in st.session_state:
        st.session_state['top_tracks_display'] = {artist: False for artist in top_20_artists}

    for i in range(0, len(top_20_artists), 5):
        cols = st.columns(5)
        for idx, artist_name in enumerate(top_20_artists[i:i+5]):
            with cols[idx]:
                artist_image_url = get_artist_image(artist_name)
                if artist_image_url:
                    st.image(artist_image_url, use_container_width=True, caption=artist_name)
                    if st.button(f"Show {artist_name}'s Top Tracks", key=f"tracks_{artist_name}"):
                        st.session_state['top_tracks_display'][artist_name] = not st.session_state['top_tracks_display'][artist_name]

                    if st.session_state['top_tracks_display'][artist_name]:
                        artist_top_tracks = get_artist_top_tracks(artist_name)
                        if artist_top_tracks:
                            st.write(f"**Top Tracks by {artist_name}:**")
                            for track_name, preview_url, spotify_url in artist_top_tracks:
                                st.write(f"- [{track_name}]({preview_url}) ([Listen on Spotify]({spotify_url}))")
                        else:
                            st.write(f"No top tracks found for {artist_name}")

# Footer
st.markdown(
    '<div class="footer">Developed with ❤️ by Sachin <br> Data Source: Spotify API</div>',
    unsafe_allow_html=True
)
