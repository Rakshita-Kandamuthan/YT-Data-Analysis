import streamlit as st
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Connect to MySQL database
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="rakshita",
    database="yt_env"
)

# Create a cursor object
cursor = conn.cursor()

# Function to retrieve video and channel data from MySQL

# Streamlit app
def main():
    st.title("In-Depth Analysis")
    st.sidebar.title("Analyze Any Channel")

    # Fetch all channel names from channel_info table
    cursor.execute("SELECT DISTINCT channel_name FROM channel_info")
    channel_names = cursor.fetchall()
    channel_names = [name[0] for name in channel_names]

    # Create dropdown to select a channel
    selected_channel = st.sidebar.selectbox("Select a Channel", channel_names)

    # Analyze button
    if st.sidebar.button("Analyze"):
        if selected_channel:
            # Retrieve details from channel_info table for the selected channel
            query = """
                SELECT distinct channel_name, subscribers, views, total_videos
                FROM channel_info
                WHERE channel_name = %s
            """

            # Execute the query with the selected channel name
            cursor.execute(query, (selected_channel,))
            results = cursor.fetchall()

            if results:
                # Convert the fetched data to a Pandas DataFrame
                df = pd.DataFrame(results, columns=["Channel Name", "Subscribers", "Views", "Total Videos"])

                # Display the DataFrame
                st.dataframe(df)
            else:
                st.write("No data found.")

    st.write("To know all the available Videos and its corresponding Channel Names, Click on 'View'")

    # Create a button to fetch data
    if st.button("View"):
        cursor.execute("SELECT distinct video_name, channel_name FROM video_info")
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=["Video Names", "Channel Names"])

            # Display the data in a table
            st.table(df)
        else:
            st.write("No data found.")

    st.write("To view channels that have the most number of videos, Click on 'Channels vs Videos'")
    # Create a button to fetch data
    if st.button("Channels vs Videos"):
        cursor.execute("SELECT distinct channel_name, total_videos FROM channel_info")
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=['Channel Name', 'Total Videos'])

            # Plot the data as a Line Chart
            plt.figure(figsize=(10, 6))
            sns.lineplot(x='Channel Name', y='Total Videos', data=df)
            plt.xlabel('Channel Name')
            plt.ylabel('Total Videos')
            plt.title('Channels vs Videos Line Chart')

            # Display the Line Chart
            st.pyplot(plt)
        else:
            st.write("No data found.")

    # st.write("To view the top 10 most viewed videos, Click on the button below")
    # # Create a button to fetch data
    # if st.button("Videos vs Views"):
    #     cursor.execute("SELECT distinct video_name, views FROM channels ORDER BY views DESC")
    #     videos = cursor.fetchall()
    #     if videos:
    #         # Display the data in a table
    #         st.table(videos)
    #     else:
    #         st.write("No data found.")

    st.write("To view how many comments were made on each video, Click on 'Videos vs Comments'")
    # Create a button to fetch data
    if st.button("Videos vs Comments"):
        cursor.execute(
            "SELECT video_info.video_name, max(comment_info.comment_count) AS total_comments FROM video_info JOIN comment_info ON video_info.video_id = comment_info.video_id GROUP BY video_info.video_name"
        )
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=["Video Name", "Total Comments"])

            # Display the data in a table
            st.table(df)
        else:
            st.write("No data found.")

    st.write("To view which videos have the highest number of likes, Click on 'Videos vs Likes'")
    # Create a button to fetch data
    if st.button("Videos vs Likes"):
        cursor.execute(
            "SELECT distinct video_info.video_name, video_info.like_count, channel_info.channel_name FROM video_info INNER JOIN channel_info ON video_info.channel_name = channel_info.channel_name")
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=['Video Name', 'Like Count', 'Channel Name'])

            # Group the data by channel name and calculate the total likes
            grouped_data = df.groupby('Channel Name')['Like Count'].sum()

            # Sort the DataFrame by Like Count in descending order
            df_sorted = df.sort_values('Like Count', ascending=False)

            # Convert DataFrame to HTML table without row numbers
            table_html = df_sorted.to_html(index=False)

            # Display the table without row numbers
            st.markdown(table_html, unsafe_allow_html=True)

        else:
            st.write("No data found.")

    st.write("To view the total number of views for each channel, Click on 'Video vs Views'")
    # Create a button to fetch data
    if st.button("Video vs Views"):
        cursor.execute("SELECT distinct channel_name, views FROM channel_info")
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=['Channel Name', 'Views'])

            # Plot the data as a Pie Chart
            plt.figure(figsize=(4,4))  # Adjust the figsize parameter to decrease the size of the chart
            plt.pie(df['Views'], labels=df['Channel Name'], autopct='%1.1f%%')
            plt.title('Video vs Views')

            # Display the Pie Chart
            st.pyplot(plt)
        else:
            st.write("No data found.")

    st.write("To know all the names of all the channels that have published videos in the year 2022, Click on '2022'")
    # Create a button to fetch data
    if st.button("2022"):
        cursor.execute(
            "SELECT distinct channel_name FROM video_info WHERE YEAR(DATE(video_info.video_published_date)) = 2022"
        )
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=["Channel Names"])

            # Display the data in a table
            st.table(df)
        else:
            st.write("No data found.")

    st.write("To know all average duration of all videos in each channel, Click on 'Avg Duration'")
    # Create a button to fetch data
    if st.button("Avg Duration"):
        cursor.execute(
            "SELECT channel_name, AVG(TIME_TO_SEC(SUBSTRING(video_duration, 3))) AS average_duration FROM video_info GROUP BY channel_name"
        )
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=["Channel Name", "Average Duration"])

            # Set the figure size
            plt.figure(figsize=(10, 6))  # Adjust the width and height as needed

            # Plot the data as a Bar Plot
            plt.bar(df["Channel Name"], df["Average Duration"])
            plt.xlabel("Channel Name")
            plt.ylabel("Average Duration")
            plt.xticks(rotation=90)
            plt.title("Average Durations by Channel")

            # Display the Bar Plot
            st.pyplot(plt)
        else:
            st.write("No data found.")

    st.write("To know which videos have the highest number of comments, Click on 'Most Comments'")
    if st.button("Most Comments"):
        cursor.execute("SELECT distinct channel_name, video_info.video_name, SUM(comment_info.comment_count) AS total_comments FROM video_info video_info JOIN comment_info comment_info ON video_info.video_id = comment_info.video_id GROUP BY video_info.channel_name, video_info.video_name ORDER BY total_comments DESC")
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=['Channel Name', 'Video Name', 'Total Comments'])

            # Convert the 'Total Comments' column to numeric datatype
            df['Total Comments'] = pd.to_numeric(df['Total Comments'])

            # Display the data as a bar plot
            st.bar_chart(df, x='Video Name', y='Total Comments')
            st.table(videos)
        else:
            st.write("No data found.")


    st.write("To know all the Channels and its corresponding Subscribers, Click on 'Channels vs Subscribers'")

    # Create a button to fetch data
    if st.button("Channels vs Subscribers"):
        cursor.execute("SELECT distinct channel_name, subscribers FROM channel_info")
        videos = cursor.fetchall()
        if videos:
            # Convert the fetched data to a Pandas DataFrame
            df = pd.DataFrame(videos, columns=["Channel Names", "Subscribers"])

            # Set the figure size
            plt.figure(figsize=(10, 6))  # Adjust the width and height as needed

            # Plot the data as an Area Chart
            plt.fill_between(df["Channel Names"], df["Subscribers"], alpha=0.5)
            plt.plot(df["Channel Names"], df["Subscribers"], marker="o")
            plt.xlabel("Channel Names")
            plt.ylabel("Subscribers")
            plt.xticks(rotation=45)
            plt.title("Channels vs Subscribers")

            # Display the Area Chart
            st.pyplot(plt)
        else:
            st.write("No data found.")

if __name__ == "__main__":
    main()
