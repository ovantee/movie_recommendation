import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import requests

# Assuming recommendation_model.py contains the necessary functions and model variables
from recommendation_model import get_recommendations, movie_data, cosine_sim, knn_model, w2v_model

# Set up the Streamlit page configuration
st.set_page_config(layout="wide")
st.title('Interactive Movie Recommendation Dashboard')

# Load data
data = pd.read_csv('movie_merged_output.csv')
data['Name of movie'] = data['Name of movie'].astype(str)
data['keywords'] = data['keywords'].astype(str)

# Load user input for movie selection
movie_title = st.selectbox('Select a movie:', data['Name of movie'].unique())

# Model selection
model_options = ['TF-IDF', 'KNN', 'Word2Vec']
model_option = st.selectbox('Select recommendation model:', model_options)

# Display the selected movie details
if movie_title:
    selected_movie = data[data['Name of movie'].str.lower() == movie_title.lower()].iloc[0]
    col1, col2 = st.columns([1, 4])
    with col1:
        # Check if 'img_src' is in the DataFrame and if the entry is not null
        if 'img_src' in data.columns and pd.notna(selected_movie['img_src']):
            img = Image.open(BytesIO(requests.get(selected_movie['img_src']).content))
            st.image(img, width=220)
        else:
            st.write("No image available")
    with col2:
        st.subheader(selected_movie['Name of movie'])
        st.write(f"Rating: {selected_movie['Movie Rating']}")
        st.write(f"Description: {selected_movie['Des']}")

# Recommendation button
if st.button('Get Submissions'):
    # Determine which model to use based on user selection
    model = None
    if model_option == 'TF-IDF':
        model = None  # Using cosine similarity matrix
    elif model_option == 'KNN':
        model = knn_model
    elif model_option == 'Word2Vec':
        model = w2v_model

    recommendations = get_recommendations(movie_title, data, cosine_sim, model, top_n=5)
    # if not recommendations.empty:
    #     st.write("Recommendations:")
    #     for rec in recommendations.itertuples():
    #         # Using index access due to spaces in column names
    #         st.write(f"{rec[1]} - Rating: {rec[2]} - Score: {rec[3]:.2f}")
    #         if 'img_src' in recommendations.columns and pd.notna(rec[5]):
    #             img = Image.open(BytesIO(requests.get(rec[5]).content))
    #             st.image(img, width=220)
    #         st.write(f"Description: {rec[4]}")
    # else:
    #     st.write("No submissions found.")
    import streamlit as st
    if not recommendations.empty:
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
                        st.image(img, width=220)
                    except Exception as e:
                        st.error("Error loading image.")
                st.write(f"Description: {rec[4]}")
                # Add a horizontal rule if it's not the last item in the column
                if (idx + 1) % num_cols != 0 or idx + 1 != len(recommendations):
                    st.markdown("---")
    else:
        st.write("No submissions found.")

# Sidebar instructions
st.sidebar.header('Instructions')
st.sidebar.text('1. Use the dropdown to select a movie.\n2. Select the model.\n3. Click "Get Submissions" to see related movies.')
