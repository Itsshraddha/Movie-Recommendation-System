import pandas as pd 
import pickle
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

session = requests.Session()

retries = Retry(
    total=3,
    connect=3,
    read=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)

df = pickle.load(open('movies.pkl' , 'rb'))
similarity = pickle.load(open('similarity.pkl' , 'rb'))

# css
st.markdown("""
<h1 style='
    text-align: center;
    color: #E50914;
    font-size: 50px;
    font-weight: bold;
'>
🎬 Movie Recommender System
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.stApp {
    background-color: #141414;
    color: white;
}
            
.caption-text {
    text-align: center;
    color: #b3b3b3;
    font-size: 14px;
    margin-top: -10px;
}
            
/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: #333333;
    color: white;
    border-radius: 8px;
}

/*  Button */
.stButton>button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #f6121d;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# Caption
st.markdown("""
<p class='caption-text'>
Discover movies similar to your favorite in seconds 
</p>
""", unsafe_allow_html=True)

# main function
@st.cache_data
def fetch_poster(movie_id, movie_name):
    api_key = "6a21f6dd87b92f8d02c45a9f9d44f631"

    try:
        # Step 1: Try with movie_id
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        data = session.get(url, timeout=5).json()

        poster_path = data.get('poster_path')

        # Step 2: If not found → search by name
        if not poster_path:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
            data = session.get(url, timeout=5).json()

            if data.get('results'):
                poster_path = data['results'][0].get('poster_path')

        #  Step 3: Return final image
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path

    except:
        pass

    #  Step 4: Fallback image (always safe)
    return "https://via.placeholder.com/300x450?text=No+Poster"

def recommend(movie):
    movie = movie.lower()
    
    if movie not in df['title'].str.lower().values:
         return [], []
    
    movie_index = df[df['title'].str.lower() == movie].index[0]
    distances = similarity[movie_index]
    
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies=  []
    recommended_posters = []
    for i in movies_list:
        movie_title = df.iloc[i[0]].title
        movie_id = df.iloc[i[0]].movie_id

        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_id, movie_title))
        # recommended_movies.append(df.iloc[i[0]].title)
        # recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies , recommended_posters

selected_movie = st.selectbox("" , df["title"].values)

if st.button("Recommend movies"):
    recommended_movies, recommended_posters = recommend(selected_movie)
    
    cols = st.columns(5)
    for col, movie, poster in zip(cols, recommended_movies, recommended_posters):
        with col:
            st.image(poster)
            st.write(movie)


