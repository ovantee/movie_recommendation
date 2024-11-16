import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from gensim.models import Word2Vec
import numpy as np


def load_data(filepath):
    movie_data = pd.read_csv(filepath)
    movie_data['Des'].fillna('', inplace=True)
    movie_data['keywords'].fillna('', inplace=True)
    movie_data['combined_features'] = movie_data['Des'] + " " + movie_data['keywords']
    return movie_data

def create_tfidf_model(data):
    tfidf_vectorizer = TfidfVectorizer()
    combined_features = data['Des'] + " " + data['keywords']
    tfidf_matrix = tfidf_vectorizer.fit_transform(combined_features)
    cosine_sim = cosine_similarity(tfidf_matrix)
    return tfidf_matrix, cosine_sim, tfidf_vectorizer
    return tfidf_matrix, tfidf_vectorizer

def create_knn_model(tfidf_matrix, n_neighbors=5):
    knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
    knn_model.fit(tfidf_matrix)
    return knn_model

def train_word2vec(data):
    sentences = [row.split() for row in data['combined_features']]
    model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
    return model


def vectorize_text(text, model):
    words = text.split()
    word_vectors = [model.wv[word] for word in words if word in model.wv]
    return np.mean(word_vectors, axis=0) if word_vectors else np.zeros(model.vector_size)


def get_recommendations(title, movie_data, similarity_matrix, model, top_n=5):
    # Tìm chỉ số phim từ tiêu đề nhập vào
    idx = movie_data[movie_data['Name of movie'].str.lower() == title.lower()].index[0]

    if isinstance(model, NearestNeighbors):
        # Extract the TF-IDF vector for the input title
        title_feature = tfidf_matrix[idx].reshape(1, -1)  # Ensure the input is 2D

        # Find the nearest neighbors
        distances, indices = knn_model.kneighbors(title_feature, n_neighbors=top_n + 1)

        # Exclude the first index as it is the movie itself
        indices = indices[0][1:]
        distances = distances[0][1:]
    elif isinstance(model, Word2Vec):
        # Vectorize text using Word2Vec
        movie_data['combined_features'] = movie_data['Des'] + " " + movie_data['keywords']
        movie_vector = vectorize_text(movie_data.iloc[idx]['combined_features'], model)
        all_movie_vectors = np.vstack([vectorize_text(text, model) for text in movie_data['combined_features']])
        # Calculate cosine similarity
        similarity = cosine_similarity([movie_vector], all_movie_vectors)
        # Sắp xếp chỉ số theo độ tương tự giảm dần, loại bỏ phim đầu tiên là chính nó
        indices = np.argsort(similarity[0])[::-1][1:top_n + 1]
        distances = similarity[0][indices]
    else:
        # Handle TF-IDF cosine similarity directly
        sim_scores = list(enumerate(similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]  # Loại bỏ chính nó khỏi danh sách
        indices = [i[0] for i in sim_scores]
        distances = [i[1] for i in sim_scores]

    # Lấy dữ liệu của các phim được gợi ý
    recommended_movies = movie_data.iloc[indices]
    recommended_movies['Score'] = distances  # Thêm cột điểm độ tương đồng

    return recommended_movies[['Name of movie', 'Movie Rating', 'Score', 'Des', 'img_src']]




# Load and process data
data_path = 'movie_merged_output.csv'
movie_data = load_data(data_path)
tfidf_matrix, cosine_sim, tfidf_vectorizer = create_tfidf_model(movie_data)
knn_model = create_knn_model(tfidf_matrix)
w2v_model = train_word2vec(movie_data)

