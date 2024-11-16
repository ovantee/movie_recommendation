import streamlit as st
import pandas as pd
import plotly.express as px
from recommendation_model import movie_data, cosine_sim, get_recommendations
from PIL import Image
from io import BytesIO
import requests
st.set_page_config(layout="wide")
from recommendation_model import get_recommendations, movie_data, cosine_sim, knn_model, w2v_model

# # Tiêu đề của dashboard
st.title('Interactive Movie Recommendation Dashboard Filter')

# Tải dữ liệu
data = pd.read_csv('movie_merged_output.csv')  # Đường dẫn tới file dữ liệu sau khi đã xử lý

# Ensure that columns are treated as strings
data['Name of movie'] = data['Name of movie'].astype(str)
data['keywords'] = data['keywords'].astype(str)

# Sidebar Filters
st.sidebar.header('Filter')
# search_query = st.sidebar.text_input("Search by keywords")
# Model selection
model_options = ['TF-IDF', 'KNN', 'Word2Vec']
selected_model = st.sidebar.selectbox('Chọn Model Recommendation', model_options)
search_query = st.sidebar.text_input("Search by movie title, keywords, or both:")
# Using the search bar to filter by movie title or keywords
# if search_query:
#     filtered_data = data[data.apply(lambda row: search_query.lower() in row['Name of movie'].lower() or
#                                     search_query.lower() in row['keywords'].lower(), axis=1)]
# else:
#     filtered_data = data
year = st.sidebar.slider('Năm phát hành', int(data['Year of release'].min()), int(data['Year of release'].max()), (int(data['Year of release'].min()), int(data['Year of release'].max())))
genre_options = set([g.strip() for sublist in data['Genre'].dropna().str.split(',') for g in sublist])
genre = st.sidebar.multiselect('Thể loại', options=list(genre_options))
classification = st.sidebar.multiselect('Phân loại', options=data['Classification'].dropna().unique())

metascore_range = st.sidebar.slider('Metascore', int(data['Metascore'].min()), int(data['Metascore'].max()), (int(data['Metascore'].min()), int(data['Metascore'].max())))
rating_range = st.sidebar.slider('Điểm phim', float(data['Movie Rating'].min()), float(data['Movie Rating'].max()), (float(data['Movie Rating'].min()), float(data['Movie Rating'].max())))

# Lọc dữ liệu dựa trên tiêu chí
filtered_data = data[(data['Year of release'] >= year[0]) & (data['Year of release'] <= year[1])]
if genre:
    filtered_data = filtered_data[filtered_data['Genre'].isin(genre)]
if classification:
    filtered_data = filtered_data[filtered_data['Classification'].isin(classification)]
filtered_data = filtered_data[(filtered_data['Metascore'] >= metascore_range[0]) & (filtered_data['Metascore'] <= metascore_range[1])]
filtered_data = filtered_data[(filtered_data['Movie Rating'] >= rating_range[0]) & (filtered_data['Movie Rating'] <= rating_range[1])]


# Display Movie Data with Images
for index, row in filtered_data.iterrows():
    cols = st.columns([1, 4])
    with cols[0]:
        st.image(row['img_src'], width=120)
    with cols[1]:
        st.subheader(row['Name of movie'])
        st.write(f"Rating: {row['Movie Rating']}")
        st.write(f"Description: {row['Des']}")
        # Use the DataFrame index as part of the key for uniqueness
        movie_clicked = st.button('Show Recommendations', key=f"{row['Name of movie']}_{index}")
        if movie_clicked:
        #     recommendations = get_recommendations(row['Name of movie'], movie_data, cosine_sim, top_n=5)
        #     for index_i, rec in recommendations.iterrows():
        #         # st.text(f"{rec['Name of movie']} - Rating: {rec['Movie Rating']} - Similarity Score: {rec['Similarity_Score']:.2f}")
        #         cols = st.columns([1, 3])
        #         with cols[0]:
        #             st.image(rec['img_src'], width=100, use_column_width=True)
        #         with cols[1]:
        #             st.subheader(rec['Name of movie'])
        #             st.write(f"Rating: {rec['Movie Rating']}")
        #             st.write(f"Description: {row['Des']}")
        #             st.write(f"Similarity Score: {rec['Similarity_Score']:.2f}")
        # Determine which model to use based on user selection
            model = None
            if selected_model == 'TF-IDF':
                model = None  # Using cosine similarity matrix
            elif selected_model == 'KNN':
                model = knn_model
            elif selected_model == 'Word2Vec':
                model = w2v_model

            recommendations = get_recommendations(row['Name of movie'], data, cosine_sim, model, top_n=5)

            st.write("Recommendations:")

            # Calculate the number of columns based on the smaller of 5 or the number of recommendations available
            num_cols = min(5, len(recommendations))
            cols = st.columns(num_cols)

            # Iterate over each recommendation and populate the columns
            for idx, rec in enumerate(recommendations.itertuples(), start=0):
                col = cols[idx % num_cols]  # Cycle through columns
                with col:
                    # Display movie information
                    st.write(f"**{rec[1]}**")
                    st.write(f"**Rating: {rec[2]}**")
                    st.write(f"**Score: {rec[3]:.2f}**")
                    if 'img_src' in recommendations.columns and pd.notna(rec[5]):
                        try:
                            # Try to load and display the image from the web
                            img = Image.open(BytesIO(requests.get(rec[5]).content))
                            st.image(img, width=120)
                        except Exception as e:
                            st.error("Error loading image.")
                    st.write(f"Description: {rec[4]}")
                    # Add a horizontal rule if it's not the last item in the column
                    if (idx + 1) % num_cols != 0 or idx + 1 != len(recommendations):
                        st.markdown("---")




# Display instructions
st.sidebar.header('Instructions')
st.sidebar.text('1. Use the dropdown to select a movie.\n2. Click "Show Recommendations" to see related movies.')




