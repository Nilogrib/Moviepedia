import string
import pickle
import pandas as pd
import ast
import requests
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import dns.resolver
from requests.adapters import HTTPAdapter
from urllib3.util.connection import create_connection
from urllib3.poolmanager import PoolManager  # Added this import
import socket

# Object for porterStemmer
ps = PorterStemmer()
nltk.download('stopwords')
import streamlit as st

# Configure DNS resolver to use Google DNS
def create_connection_with_google_dns(*args, **kwargs):
    host = args[0][0]
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        answer = resolver.resolve(host, 'A')
        ip_address = str(answer[0])
        return create_connection((ip_address, args[0][1]), **kwargs)
    except Exception as e:
        return create_connection(*args, **kwargs)

# Modified GoogleDNSAdapter class
class GoogleDNSAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.poolmanager = None  # Initialize the poolmanager attribute
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        # Define default socket options
        pool_kwargs['socket_options'] = [
            (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        ]
        
        # Create the pool manager
        self.poolmanager = PoolManager(  # Use self.poolmanager instead of self._pool_manager
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            **pool_kwargs
        )
        
        # Set the custom connection factory if needed
        if hasattr(self.poolmanager.pool_classes_by_scheme['https'], 'ConnectionCls'):
            self.poolmanager.pool_classes_by_scheme['https'].ConnectionCls.create_connection = create_connection_with_google_dns
        
        return self.poolmanager

def get_genres(obj):
    lista = ast.literal_eval(obj)
    l1 = []
    for i in lista:
        l1.append(i['name'])
    return l1

def get_cast(obj):
    a = ast.literal_eval(obj)
    l_ = []
    len_ = len(a)
    for i in range(0, 10):
        if i < len_:
            l_.append(a[i]['name'])
    return l_

def get_crew(obj):
    l1 = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            l1.append(i['name'])
            break
    return l1

def read_csv_to_df():
    credit_ = pd.read_csv(r'Files/tmdb_5000_credits.csv')
    movies = pd.read_csv(r'Files/tmdb_5000_movies.csv')
    movies = movies.merge(credit_, on='title')

    movies2 = movies
    movies2.drop(['homepage', 'tagline'], axis=1, inplace=True)
    movies2 = movies2[['movie_id', 'title', 'budget', 'overview', 'popularity', 'release_date', 'revenue', 'runtime',
                       'spoken_languages', 'status', 'vote_average', 'vote_count']]

    movies = movies[
        ['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew', 'production_companies', 'release_date']]
    movies.dropna(inplace=True)

    movies['genres'] = movies['genres'].apply(get_genres)
    movies['keywords'] = movies['keywords'].apply(get_genres)
    movies['top_cast'] = movies['cast'].apply(get_cast)
    movies['director'] = movies['crew'].apply(get_crew)
    movies['prduction_comp'] = movies['production_companies'].apply(get_genres)

    movies['overview'] = movies['overview'].apply(lambda x: x.split())
    movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
    movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
    movies['tcast'] = movies['top_cast'].apply(lambda x: [i.replace(" ", "") for i in x])
    movies['tcrew'] = movies['director'].apply(lambda x: [i.replace(" ", "") for i in x])
    movies['tprduction_comp'] = movies['prduction_comp'].apply(lambda x: [i.replace(" ", "") for i in x])

    movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['tcast'] + movies['tcrew']

    new_df = movies[['movie_id', 'title', 'tags', 'genres', 'keywords', 'tcast', 'tcrew', 'tprduction_comp']]

    new_df['genres'] = new_df['genres'].apply(lambda x: " ".join(x))
    new_df['tcast'] = new_df['tcast'].apply(lambda x: " ".join(x))
    new_df['tprduction_comp'] = new_df['tprduction_comp'].apply(lambda x: " ".join(x))

    new_df['tcast'] = new_df['tcast'].apply(lambda x: x.lower())
    new_df['genres'] = new_df['genres'].apply(lambda x: x.lower())
    new_df['tprduction_comp'] = new_df['tprduction_comp'].apply(lambda x: x.lower())

    new_df['tags'] = new_df['tags'].apply(stemming_stopwords)
    new_df['keywords'] = new_df['keywords'].apply(stemming_stopwords)

    return movies, new_df, movies2

def stemming_stopwords(li):
    ans = []
    for i in li:
        ans.append(ps.stem(i))

    stop_words = set(stopwords.words('english'))
    filtered_sentence = []
    for w in ans:
        w = w.lower()
        if w not in stop_words:
            filtered_sentence.append(w)

    str_ = ''
    for i in filtered_sentence:
        if len(i) > 2:
            str_ = str_ + i + ' '

    punc = string.punctuation
    str_.translate(str_.maketrans('', '', punc))
    return str_


def fetch_posters(movie_id):
    session = requests.Session()
    adapter = GoogleDNSAdapter()
    session.mount('https://', adapter)
    
    try:
        # Add error handling for the API key
        api_key = 'Your-API-Key'
        if not api_key:
            return "No API key configured"

        response = session.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}',
            params={'api_key': api_key},
            timeout=10
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        if data.get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            # Verify the image URL is accessible
            img_response = session.head(poster_url, timeout=5)
            if img_response.status_code == 200:
                return poster_url
        
        # Return a default image if any step fails
        return "https://via.placeholder.com/500x750.png?text=No+Image+Available"
        
    except requests.RequestException as e:
        print(f"Error fetching poster for movie {movie_id}: {e}")
        return "https://via.placeholder.com/500x750.png?text=Error+Loading+Image"

def recommend(new_df, movie, pickle_file_path):
    with open(pickle_file_path, 'rb') as pickle_file:
        similarity_tags = pickle.load(pickle_file)

    movie_idx = new_df[new_df['title'] == movie].index[0]
    movie_list = sorted(list(enumerate(similarity_tags[movie_idx])), reverse=True, key=lambda x: x[1])[1:26]

    rec_movie_list = []
    rec_poster_list = []

    for i in movie_list:
        rec_movie_list.append(new_df.iloc[i[0]]['title'])
        rec_poster_list.append(fetch_posters(new_df.iloc[i[0]]['movie_id']))

    return rec_movie_list, rec_poster_list

def vectorise(new_df, col_name):
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vec_tags = cv.fit_transform(new_df[col_name]).toarray()
    sim_bt = cosine_similarity(vec_tags)
    return sim_bt

def fetch_person_details(id_):
    session = requests.Session()
    adapter = GoogleDNSAdapter()
    session.mount('https://', adapter)
    
    try:
        response = session.get(
            f'https://api.themoviedb.org/3/person/{id_}',
            params={'api_key': 'Your-API-Key'},
            timeout=10
        )
        data = response.json()
        
        if 'profile_path' in data and data['profile_path']:
            url = f"https://image.tmdb.org/t/p/w220_and_h330_face{data['profile_path']}"
        else:
            url = "https://media.istockphoto.com/vectors/error-icon-vector-illustration-vector-id922024224?k=6&m=922024224&s=612x612&w=0&h=LXl8Ul7bria6auAXKIjlvb6hRHkAodTqyqBeA6K7R54="
        
        biography = data.get('biography', '')
        return url, biography
        
    except Exception as e:
        print(f"Error fetching person details for ID {id_}: {e}")
        return ("https://media.istockphoto.com/vectors/error-icon-vector-illustration-vector-id922024224?k=6&m=922024224&s=612x612&w=0&h=LXl8Ul7bria6auAXKIjlvb6hRHkAodTqyqBeA6K7R54=", "")

def get_details(selected_movie_name):
    pickle_file_path = r'Files/movies_dict.pkl'
    with open(pickle_file_path, 'rb') as pickle_file:
        loaded_dict = pickle.load(pickle_file)

    movies = pd.DataFrame.from_dict(loaded_dict)

    pickle_file_path = r'Files/movies2_dict.pkl'
    with open(pickle_file_path, 'rb') as pickle_file:
        loaded_dict_2 = pickle.load(pickle_file)

    movies2 = pd.DataFrame.from_dict(loaded_dict_2)

    a = pd.DataFrame(movies2[movies2['title'] == selected_movie_name])
    b = pd.DataFrame(movies[movies['title'] == selected_movie_name])

    budget = a.iloc[0, 2]
    overview = a.iloc[0, 3]
    release_date = a.iloc[:, 5].iloc[0]
    revenue = a.iloc[:, 6].iloc[0]
    runtime = a.iloc[:, 7].iloc[0]
    available_lang = ast.literal_eval(a.iloc[0, 8])
    vote_rating = a.iloc[:, 10].iloc[0]
    vote_count = a.iloc[:, 11].iloc[0]
    movie_id = a.iloc[:, 0].iloc[0]
    cast = b.iloc[:, 9].iloc[0]
    director = b.iloc[:, 10].iloc[0]
    genres = b.iloc[:, 3].iloc[0]
    this_poster = fetch_posters(movie_id)
    cast_per = b.iloc[:, 5].iloc[0]
    a = ast.literal_eval(cast_per)
    cast_id = []
    for i in a:
        cast_id.append(i['id'])
    lang = []
    for i in available_lang:
        lang.append(i['name'])

    info = [this_poster, budget, genres, overview, release_date, revenue, runtime, available_lang, vote_rating,
            vote_count, movie_id, cast, director, lang, cast_id]

    return info
