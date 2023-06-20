import heapq
import math
import random
import pymysql

# Connect to the database
connection = pymysql.connect(host='localhost', user='root', password='root', db='movielens')
cursor = connection.cursor(pymysql.cursors.DictCursor)


# Fetch user data
def fetch_users(cursor):
    cursor.execute("SELECT userId, gender, age, occupation FROM users")
    users = {}
    for row in cursor.fetchall():
        user_id = row['userId']
        age = row['age']
        if row['gender'] == 'F':
            gender = 0
        else:
            gender = 1
        occupation = row['occupation']
        users[user_id] = {"userId":user_id,'gender': gender, 'age': age, 'occupation': occupation}
    return users


# Fetch rated user data
def fetch_ratings(cursor):
    cursor.execute("SELECT DISTINCT userId, movieId, rating FROM ratings")
    ratings = []
    for row in cursor.fetchall():
        user_id = row['userId']
        movie_id = row['movieId']
        rating = row['rating']
        ratings.append({'userId': user_id, 'movieId': movie_id, 'rating': rating})
    return ratings



# Calculate user similarity (Pearson correlation)
def calculate_user_similarity(user1, user2):
    user1_gender = user1['gender']
    user1_age = user1['age']
    user1_occupation = user1['occupation']

    user2_gender = user2['gender']
    user2_age = user2['age']
    user2_occupation = user2['occupation']

    # Calculate Pearson correlation coefficient
    numerator = (user1_gender * user2_gender) + (user1_age * user2_age) + (user1_occupation * user2_occupation)
    denominator = math.sqrt(user1_gender ** 2 + user1_age ** 2 + user1_occupation ** 2) * math.sqrt(
        user2_gender ** 2 + user2_age ** 2 + user2_occupation ** 2)

    if denominator == 0:
        return 0.0

    similarity = numerator / denominator
    return similarity


# Find similar users
def find_similar_users(target_user, rated_users):
    similarities = {}
    for other_user in rated_users:
        if other_user['userId'] != target_user['userId']:
            similarity = calculate_user_similarity(target_user, other_user)
            similarities[other_user['userId']] = similarity
    similar_user_ids = heapq.nlargest(3, similarities, key=similarities.get)
    return similar_user_ids


# Get user recommendations
def get_recommendations_for_user(target_user_id, users):
    top_n = 5
    cursor.execute("SELECT DISTINCT movieId FROM ratings WHERE userId = %s", target_user_id)
    rated_movies = [row['movieId'] for row in cursor.fetchall()]

    # If the user has no rating data, recommend popular movies
    if not rated_movies:
        cursor.execute("SELECT movieId FROM ratings GROUP BY movieId ORDER BY COUNT(*) DESC LIMIT %s", top_n)
        recommended_movies = [row['movieId'] for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT DISTINCT userId FROM ratings WHERE movieId IN %s", (tuple(rated_movies),))
        rated_user_ids = [row['userId'] for row in cursor.fetchall()]

        target_user = users[target_user_id]
        rated_users = [users[user_id] for user_id in rated_user_ids]

        similar_user_ids = find_similar_users(target_user, rated_users)
        similar_rated_user_ids = list(set(similar_user_ids) & set(rated_user_ids))

        if not similar_rated_user_ids:
            # If no similar users have rating data, recommend popular movies
            cursor.execute("SELECT movieId FROM ratings GROUP BY movieId ORDER BY COUNT(*) DESC LIMIT %s", top_n)
            recommended_movies = [row['movieId'] for row in cursor.fetchall()]
        else:
            cursor.execute("SELECT movieId FROM ratings WHERE userId IN %s", (tuple(similar_rated_user_ids),))
            similar_user_ratings = [row['movieId'] for row in cursor.fetchall()]

            recommended_movies = random.sample(similar_user_ratings, min(top_n, len(similar_user_ratings)))

    return recommended_movies


def get_movies_info(movie_ids):
    movies_infos = {}
    for movie_id in movie_ids:
        cursor.execute("SELECT * FROM movies WHERE movieId = %s", movie_id)
        movie_info = cursor.fetchone()
        movie_info_list = list(movie_info.values())
        movies_infos[movie_info['movieId']] = {
            "movie_info": movie_info_list}
    return movies_infos


# Fetch user data
users = fetch_users(cursor)

# Fetch rated user data
rated_users = fetch_ratings(cursor)

# New user registration
target_user_id = 6043

# Get user recommendations
recommendations = get_recommendations_for_user(target_user_id, users)
print("Recommended movies for new user:")
print(recommendations)
movies_info = get_movies_info(recommendations)
print(movies_info)

