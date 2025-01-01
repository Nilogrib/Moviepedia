# Movie Recommendation System 🎬

An intelligent movie recommendation system built with Streamlit that suggests movies based on content similarity, including genres, cast, production companies, and keywords.

## Features 🌟

- **Multiple Recommendation Criteria:**
  - Tag-based recommendations
  - Genre-based matching
  - Cast similarity
  - Production company connections
  - Keyword analysis

- **Detailed Movie Information:**
  - Movie posters
  - Cast details with biographies
  - Budget and revenue information
  - User ratings and vote counts
  - Release dates and runtime
  - Available languages
  - Director information

- **User Interface:**
  - Clean, intuitive Streamlit interface
  - Easy movie selection
  - Paginated movie browsing
  - Interactive movie details view

## Technology Stack 💻

- **Python 3.9**
- **Streamlit** - For the web interface
- **Pandas** - Data manipulation
- **scikit-learn** - For similarity calculations
- **NLTK** - Natural Language Processing
- **TMDB API** - Movie data and posters

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/yourusername/movie-recommendation-system.git
cd movie-recommendation-system
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your OMDB API key:
   - Get an API key from [OMDB](https://www.themoviedb.org/documentation/api)
   - Replace the API key in `preprocess.py`

4. Run the application:
```bash
streamlit run main.py
```

## Project Structure 📁

```
movie-recommendation-system/
├── main.py                 # Main Streamlit application
├── processing/
│   ├── preprocess.py      # Data preprocessing utilities
│   └── display.py         # Display handling functions
├── Files/
│   ├── tmdb_5000_credits.csv
│   ├── tmdb_5000_movies.csv
│   └── various .pkl files  # Cached data and similarity matrices
└── README.md
```

## How It Works 🔍

1. **Data Preprocessing:**
   - Processes movie and credit data from TMDB dataset
   - Creates similarity matrices using content-based filtering
   - Implements text preprocessing using NLTK
   
2. **Recommendation Engine:**
   - Uses cosine similarity to find similar movies
   - Considers multiple factors for recommendations
   - Caches results for better performance

3. **User Interface:**
   - Allows users to select movies from database
   - Shows detailed information about selected movies
   - Provides multiple recommendation views

## Future Improvements 🚀

- [ ] Add collaborative filtering
- [ ] Implement user authentication
- [ ] Add movie trailers
- [ ] Include user reviews
- [ ] Add search functionality
- [ ] Implement watchlist feature

## Contact 📧

[Nilogrib Ghosh] - [nilogribghosh@gmail.com]

Project Link: [https://drive.google.com/drive/folders/1ZmW3WbXiSmQk92ZJFMB_0QHbyBxJdKQG?usp=sharing](https://drive.google.com/drive/folders/1ZmW3WbXiSmQk92ZJFMB_0QHbyBxJdKQG?usp=sharing)
