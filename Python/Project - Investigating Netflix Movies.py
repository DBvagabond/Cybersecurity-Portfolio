# Netflix! What started in 1997 as a DVD rental service has since exploded into one of the largest entertainment and media companies.
#Given the large number of movies and series available on the platform, it is a perfect opportunity to flex your exploratory data analysis skills and dive into the entertainment industry. Our friend has also been brushing up on their Python skills and has taken a first crack at a CSV file containing Netflix data. They believe that the average duration of movies has been declining. Using your friends initial research, you'll delve into the Netflix data to see if you can determine whether movie lengths are actually getting shorter and explain some of the contributing factors, if any.

import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
netflix_df = pd.read_csv("netflix_data.csv")

# Filter data for movies
netflix_subset = netflix_df[netflix_df['type'] == 'Movie']

# Select specific columns
netflix_movies = netflix_subset[['title', 'country', 'genre', 'release_year', 'duration']]

# Filter short movies
short_movies = netflix_movies[netflix_movies['duration'] < 60]

# Assign colors based on genre
colors = []
for index, row in netflix_movies.iterrows():
    if row['genre'] == 'Children':
        colors.append('blue')
    elif row['genre'] == 'Documentaries':
        colors.append('red')
    elif row['genre'] == 'Stand-up':
        colors.append('yellow')
    else:
        colors.append('green')

# Initialize the figure
fig, ax = plt.subplots()
# Scatter plot
ax.scatter(x, y, c=colors)
ax.set_xlabel("Release year")
ax.set_ylabel("Duration (min)")
ax.set_title("Movie Duration by Year of Release")
ax.grid(True)

# Add legend
ax.legend()

# Show the plot
plt.show()
