import pymongo
import json
from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import mysql.connector
from bson import ObjectId
from pymongo import MongoClient
import googleapiclient.errors
import re
import datetime
from googleapiclient.errors import HttpError

# MongoDB configuration
mongodb_uri = 'mongodb://localhost:27017/'
mongodb_database = 'youtube_data'
mongodb_collection = 'channels'

# MySQL configuration
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'rakshita'
mysql_database = 'yt_env'

# Set up MongoDB client and database
mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongodb_db = mongodb_client.GUVI
mongodb_coll = mongodb_db['YT_env']

# Clear existing documents in the collection
mongodb_coll.delete_many({})

# Set up MySQL connection and cursor
mysql_conn = mysql.connector.connect(host="127.0.0.1",
                                     user="root",
                                     password="rakshita",
                                     database="yt_env")

mysql_cursor = mysql_conn.cursor()
# mysql_cursor.execute(create_table_query)

# Clear existing data in the MySQL table
mysql_cursor.execute("TRUNCATE TABLE channels")


# Custom function to convert timedelta to string representation of duration
def timedelta_to_string(timedelta):
    seconds = timedelta.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


# Function to store data in MongoDB and MySQL
def store_data(channel_data):
    # Store data in MongoDB
    mongodb_coll.insert_one(channel_data)

    # Convert comment_published_date to MySQL datetime format
    comment_published_date = datetime.datetime.strptime(channel_data['comment_published_date'],
                                                        "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

    # Convert comment_published_date to MySQL datetime format
    video_published_date = datetime.datetime.strptime(channel_data['video_published_date'],
                                                      "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

    # Create MySQL table
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_info (
        channel_name VARCHAR(255),
        subscribers INT,
        views BIGINT,
        total_videos INT,
        playlist_id VARCHAR(255),
        playlist_name VARCHAR(255)
        )
    """)

    # Store data in MySQL
    sql1 = '''
        INSERT INTO channel_info (channel_name, subscribers, views, total_videos, playlist_id, playlist_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    values = (
        channel_data['channel_name'],
        channel_data['subscribers'],
        channel_data['views'],
        channel_data['total_videos'],
        channel_data['playlist_id'],
        channel_data['playlist_name']
    )

    try:
        mysql_cursor.execute(sql1, values)
        mysql_conn.commit()
    except Exception as e:
        print(f"Error inserting data into MySQL: {e}")
        print(f"Failed values: {values}")

    # Create MySQL table
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_info (
        channel_name VARCHAR(255),
        video_name VARCHAR(255),
        video_id VARCHAR(255),
        like_count INT,
        video_duration VARCHAR(255),
        video_published_date DATETIME
        )
    """)

    sql2 = '''
        INSERT INTO video_info (channel_name, video_name, video_id, like_count, video_duration, video_published_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    values = (
        channel_data['channel_name'],
        channel_data['video_name'],
        channel_data['video_id'],
        channel_data['like_count'],
        channel_data['video_duration'],
        video_published_date
    )

    try:
        mysql_cursor.execute(sql2, values)
        mysql_conn.commit()
    except Exception as e:
        print(f"Error inserting data into MySQL: {e}")
        print(f"Failed values: {values}")

    # Create MySQL table
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS comment_info (
        video_id VARCHAR(255),
        comment_count INT,
        comment_text LONGTEXT,
        comment_author VARCHAR(255),
        comment_published_date DATETIME
        )
    """)

    sql3 = '''
        INSERT INTO comment_info (video_id, comment_count, comment_text, comment_author, comment_published_date)
        VALUES (%s, %s, %s, %s, %s)
    '''
    values = (
        channel_data['video_id'],
        channel_data['comment_count'],
        channel_data['comment_text'],
        channel_data['comment_author'],
        comment_published_date
    )

    try:
        mysql_cursor.execute(sql3, values)
        mysql_conn.commit()
    except Exception as e:
        print(f"Error inserting data into MySQL: {e}")
        print(f"Failed values: {values}")


# Set up the YouTube API client
def get_youtube_data(api_key, channel_ids):
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        # Retrieve channel information
        channel_data = youtube.channels().list(
            part='snippet, statistics',
            id=','.join(channel_ids)
        ).execute()

        for channel in channel_data['items']:
            channel_id = channel['id']
            channel_name = channel['snippet']['title']
            subscribers = channel['statistics'].get('subscriberCount', 'Unknown')
            views = channel['statistics'].get('viewCount', 'Unknown')
            total_videos = channel['statistics'].get('videoCount', 'Unknown')
            playlists = get_playlists(youtube, channel_id)

            for playlist_id, playlist_name in playlists.items():

                # Retrieve video information
                video_data = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=100  # Adjust as needed
                ).execute()

                for video in video_data['items']:
                    video_name = video['snippet']['title']
                    video_id = video['snippet']['resourceId']['videoId']

                    # Retrieve video statistics
                    video_stats = youtube.videos().list(
                        part='snippet, statistics, contentDetails',
                        id=video_id
                    ).execute()

                    if 'items' in video_stats and len(video_stats['items']) > 0:
                        like_count = video_stats['items'][0]['statistics'].get('likeCount', 'N/A')
                        video_duration = video_stats['items'][0]['contentDetails']['duration']
                        video_published_date = video_stats['items'][0]['snippet']['publishedAt']

                    else:
                        like_count = 'N/A'
                        duration = 'N/A'
                        publish_date = 'N/A'

                    #                     # Convert video duration to seconds
                    #                     duration_string = duration[2:]  # Remove the 'PT' prefix
                    #                     duration = datetime.timedelta()

                    #                     for match in re.finditer(r'(\d+)([HMS])', duration_string):
                    #                         value = int(match.group(1))
                    #                         unit = match.group(2)

                    #                         if unit == 'H':
                    #                             duration += datetime.timedelta(hours=value)
                    #                         elif unit == 'M':
                    #                             duration += datetime.timedelta(minutes=value)
                    #                         elif unit == 'S':
                    #                             duration += datetime.timedelta(seconds=value)

                    #                     video_duration = timedelta_to_seconds(duration)

                    try:
                        comment_data = youtube.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            maxResults=100  # Adjust as needed
                        ).execute()

                        comment_count = 0  # Initialize comment count

                        for comment in comment_data['items']:
                            comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                            comment_author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
                            comment_published_date = comment['snippet']['topLevelComment']['snippet']['publishedAt']
                            comment_count += 1  # Increment comment count

                            # Prepare data for storage
                            channel_data = {
                                'channel_name': channel_name,
                                'subscribers': subscribers,
                                'views': views,
                                'total_videos': total_videos,
                                'playlist_id': playlist_id,
                                'playlist_name': playlist_name,
                                'video_name': video_name,
                                'video_id': video_id,
                                'like_count': like_count,
                                'video_duration': str(video_duration),
                                'video_published_date': video_published_date,
                                'comment_count': comment_count,
                                'comment_text': comment_text,
                                'comment_author': comment_author,
                                'comment_published_date': comment_published_date
                            }
                            print(channel_data)

                            store_data(channel_data)

                            # channel_data2 = {'video_published_date': video_published_date,'comment_published_date': comment_published_date}

                    except HttpError as e:
                        error_message = e.content.decode("utf-8")
                        if "videoNotFound" in error_message:
                            print(f"Video not found: {video_id}")
                        else:
                            print(f"An error occurred while retrieving comments for video {video_id}: {error_message}")
                        continue

    except HttpError as e:
        print(f'An HTTP error occurred: {e}')


# Helper function to retrieve playlists for a given channel ID
def get_playlists(youtube, channel_id):
    playlists = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=50  # Adjust as needed
    ).execute()

    playlist_data = {}
    for playlist in playlists['items']:
        playlist_id = playlist['id']
        playlist_name = playlist['snippet']['title']
        playlist_data[playlist_id] = playlist_name

    return playlist_data


# Usage example
api_key = 'AIzaSyBe3WSs7fEKkvIUwF00ri_5HIa4F3qjh0o'
channel_ids = [
    # 'UCMq2xJaHsv6SkcE4iGZyong',  # Meri Bhakti My style
    # 'UCcMVnpA9L8lAusir6hiw8mg',  # vjdynamites
    # 'UC2m-tRC7D5uAviUSwd_jXnQ',  # Rahimbi's Kitchen
    'UCZyy5bQnOdS1NWgzt-LmNNg',  # The F2P Experience
    'UCotNp044q-UnNwhEKL-NALg',  # SearchWithin
    'UC6mUHiHcSj7j0sg6LwwQJ1Q',  # TARNISHED
    'UC3T5-Ja3PyxBgiH_XK2WIUA',  # ulearn
    'UCexvllJzm4K-QMVPXqSJQ6Q',  # Michael Báderson
    'UCBTsRGDfYxoXlTDGUeMLdXw'  # Arnie's Tech
]

get_youtube_data(api_key, channel_ids)