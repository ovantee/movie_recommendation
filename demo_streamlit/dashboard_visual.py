import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

# Load your data
def load_data():
    # Load your dataset here
    df = pd.read_csv('movie_merged_output.csv')
    return df

df = load_data()

# Page title
st.title('IMDb Movies Data Dashboard')

# Define a list of options for different visualizations
options = ["Top Directors Bar Chart", "Rating Distribution Heatmap", "Censor Board Rating Frequency", "Total Movies by Year", "Movie Genre Popularity Word Cloud"]

# Dropdown menu for selecting the visualization
choice = st.selectbox("Choose a chart to display:", options)

# Logic to display the selected chart
if choice == "Top Directors Bar Chart":
    # Simple Plotly bar chart for Top Directors
    top_directors = df['Director'].value_counts().head(10).reset_index()
    top_directors.columns = ['Director', 'Movies']
    fig = px.bar(top_directors, x='Movies', y='Director', orientation='h', title='Top Directors by Movies Count')
    st.plotly_chart(fig, use_container_width=True)

elif choice == "Rating Distribution Heatmap":
    # Histogram with Plotly for Rating Distribution
    fig = px.density_heatmap(df, x="Year of release", y="Movie Rating", title='Density of IMDb Rating Vs. Release Year')
    st.plotly_chart(fig, use_container_width=True)

elif choice == "Censor Board Rating Frequency":
    # Frequency of Censor Board Rating
    plt.figure(figsize=(16,8))
    sns.countplot(x='Classification', data=df, order=df['Classification'].value_counts().index[:10], palette='viridis')
    plt.ylabel('Count', fontsize=12)
    plt.xlabel('Censor Board Rating', fontsize=12)
    plt.title('Frequency of Censor Board Rating', fontsize=18)
    st.pyplot(plt.gcf())

elif choice == "Total Movies by Year":
    # Creating the line chart for total movies by year
    plt.figure(figsize=(16, 8))
    df.groupby('Year of release').count()['Name of movie'].plot(linewidth=3)
    plt.title('Total Movies by Year')
    plt.ylabel("Total Movies")
    plt.xlabel("Year")
    plt.tight_layout()
    st.pyplot(plt.gcf())

elif choice == "Movie Genre Popularity Word Cloud":
    # Aggregate genre data and generate a word cloud
    genre_data = df['Genre'].str.split(', ').explode().value_counts().to_dict()
    wc = WordCloud(width=800, height=400, random_state=1, background_color='black', colormap='rainbow', contour_width=1, contour_color='steelblue').generate_from_frequencies(genre_data)
    plt.figure(figsize=(16, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.title('Movie Genre Popularity', fontsize=20)
    plt.axis('off')
    st.pyplot(plt.gcf())