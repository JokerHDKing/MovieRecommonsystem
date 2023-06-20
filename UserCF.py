import heapq
import math
import random
import pymysql

# 链接数据库
connection = pymysql.connect(host='localhost', user='root', password='root', db='movielens',autocommit=True)
cursor = connection.cursor(pymysql.cursors.DictCursor)


# 获取用户数据
def fetch_users(cursor):
    # 从 'users' 表中获取用户数据
    sql="SELECT userId, gender, age, occupation FROM users"
    cursor.execute(sql)
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


# 获取已评分用户数据
def fetch_ratings(cursor):
    cursor.execute("SELECT DISTINCT userId, movieId, rating FROM ratings")
    ratings = []
    for row in cursor.fetchall():
        user_id = row['userId']
        movie_id = row['movieId']
        rating = row['rating']
        ratings.append({'userId': user_id, 'movieId': movie_id, 'rating': rating})
    return ratings



# 计算用户相似度（皮尔逊相关系数）
def calculate_user_similarity(user1, user2):
    user1_gender = user1['gender']
    user1_age = user1['age']
    user1_occupation = user1['occupation']

    user2_gender = user2['gender']
    user2_age = user2['age']
    user2_occupation = user2['occupation']

    # 计算皮尔逊相关系数
    numerator = (user1_gender * user2_gender) + (user1_age * user2_age) + (user1_occupation * user2_occupation)
    denominator = math.sqrt(user1_gender ** 2 + user1_age ** 2 + user1_occupation ** 2) * math.sqrt(
        user2_gender ** 2 + user2_age ** 2 + user2_occupation ** 2)

    if denominator == 0:
        return 0.0

    similarity = numerator / denominator
    return similarity


# 找到相似用户
def find_similar_users(target_user, rated_users):
    similarities = {}
    for other_user in rated_users:
        if other_user['userId'] != target_user['userId']:
            similarity = calculate_user_similarity(target_user, other_user)
            similarities[other_user['userId']] = similarity
    #选取前三个相似度最高的用户
    similar_user_ids = heapq.nlargest(3, similarities, key=similarities.get)
    return similar_user_ids


# 获取用户推荐
def get_recommendations_for_user(target_user_id, users):

    top_n = 5
    sql=f"SELECT DISTINCT movieId FROM ratings WHERE userId = {target_user_id}"
    print(sql)
    cursor.execute(sql)
    movieids=cursor.fetchall()
    rated_movies = [row['movieId'] for row in movieids]


    # 如果用户没有评分数据，则推荐热门电影
    if not rated_movies:
        cursor.execute("SELECT movieId FROM ratings GROUP BY movieId ORDER BY COUNT(*) DESC LIMIT %s", top_n)
        recommended_movies = [row['movieId'] for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT DISTINCT userId FROM ratings WHERE movieId IN %s", (tuple(rated_movies),))
        rated_user_ids = [row['userId'] for row in cursor.fetchall()]

        target_user = users[target_user_id]
        rated_users = [users[user_id] for user_id in rated_user_ids]

        similar_user_ids = find_similar_users(target_user, rated_users)
        #将用户特征相似的和拥有共同评分的用户取交集
        similar_rated_user_ids = list(set(similar_user_ids) & set(rated_user_ids))

        if not similar_rated_user_ids:
            # 如果用户没有评分数据，则推荐热门电影
            cursor.execute("SELECT movieId FROM ratings GROUP BY movieId ORDER BY COUNT(*) DESC LIMIT %s", top_n)
            recommended_movies = [row['movieId'] for row in cursor.fetchall()]
        else:
            cursor.execute("SELECT movieId FROM ratings WHERE userId IN %s", (tuple(similar_rated_user_ids),))
            similar_user_ratings = [row['movieId'] for row in cursor.fetchall()]

            recommended_movies = random.sample(similar_user_ratings, min(top_n, len(similar_user_ratings)))

    return recommended_movies


# 得到用户信息
rated_users = fetch_ratings(cursor)

def get_movies_info(usrid):
    users = fetch_users(cursor)
    movie_ids=get_recommendations_for_user(usrid,users)
    movies_infos = {}
    for movie_id in movie_ids:
        cursor.execute("SELECT * FROM movies WHERE movieId = %s", movie_id)
        movie_info = cursor.fetchone()
        movie_info_list = list(movie_info.values())
        movies_infos[movie_info['movieId']] = {
            "movie_info": movie_info_list}
    return movies_infos


# Fetch user data


# New user registration
target_user_id = 6047

# Get user recommendations
# recommendations = get_recommendations_for_user(target_user_id,users)
# print("Recommended movies for new user:")
# print(recommendations)
movies_info = get_movies_info(target_user_id)
print(movies_info)
# #
# cursor.close()
# connection.close()
