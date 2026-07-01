import streamlit as st
import pickle
import requests

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
API_KEY = st.secrets["TMDB_API_KEY"]
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>

/* App Background */
.stApp{
    background-color:#0E1117;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background-color:#161A23;
}

/* Buttons */
.stButton>button{
    width:100%;
    border-radius:10px;
    font-weight:bold;
}

/* Images */
img{
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
# 🎬 Movie Recommendation System
### Discover movies you'll love using Content-Based Filtering
""")
st.markdown("Get movie recommendations based on your favorite movies")
st.sidebar.header("🎯 Movie Recommender")
st.divider()
selected_movie = st.sidebar.selectbox(
    "Select a Movie",
    movies['title'].values
)
selected_movie_data = movies[movies['title'] == selected_movie].iloc[0]
selected_movie_id = selected_movie_data.movie_id

@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

    except requests.exceptions.RequestException as e:
        print(f"TMDB Error: {e}")
    return None
selected_movie_poster = fetch_poster(selected_movie_id)
st.subheader("🎬 Selected Movie")

left, right = st.columns([1, 2])

with left:
    if selected_movie_poster:
        st.image(selected_movie_poster, width=250)
    else:
        st.warning("Poster not available")

with right:
    st.markdown(f"## {selected_movie_data.title}")

    st.write(f"⭐ **Rating:** {selected_movie_data.vote_average}/10")

    year = str(selected_movie_data.release_date)[:4]
    st.write(f"📅 **Release Year:** {year}")

    genres = ", ".join(selected_movie_data.genres)
    st.write(f"🎭 **Genres:** {genres}")

    st.write("📝 **Overview**")
    st.write(selected_movie_data.overview_original)
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )
    recommended_movies = []
    recommended_movies_ratings = []
    recommended_movies_release_date = []
    recommended_posters = []
    recommended_scores = []
    for i in movies_list[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_ratings.append(movies.iloc[i[0]].vote_average)
        recommended_movies_release_date.append(movies.iloc[i[0]].release_date)
        recommended_posters.append(fetch_poster(movie_id))
        recommended_scores.append(round(i[1], 2))
    return recommended_movies, recommended_movies_ratings,recommended_movies_release_date,recommended_posters, recommended_scores
recommend_button = st.sidebar.button("🍿Recommend")
st.sidebar.markdown("---")

st.sidebar.subheader("ℹ️ About this Project")

st.sidebar.info("""
**Recommendation Method:** Content-Based Filtering

**Algorithm:** Cosine Similarity

**Vectorization:** CountVectorizer

**Dataset:** TMDB 5000 Movies
""")
st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ How it Works")

st.sidebar.write("""
1. Select a movie.
2. The system finds similar movies.
3. Similarity is computed using Cosine Similarity.
4. Posters are fetched from TMDB.
""")
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Python & Streamlit")
st.sidebar.caption("Made by Prachi Sharma")

if recommend_button:
    with st.spinner("Fetching recommendations..."):
      names, ratings, date, posters, scores = recommend(selected_movie)
    st.subheader("Top 5 Recommendations")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            if posters[i]:
                st.image(posters[i])
            else:
                st.write("Poster Not Available")
            st.write(names[i])
            st.write("⭐", ratings[i])
            st.write(date[i])
            st.caption(f"Similarity Score : {scores[i]}")
            
