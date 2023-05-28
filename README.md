# YouTube Data Analysis

This project aims to develop a user-friendly Streamlit application that extracts information on a YouTube channel and enables users to search for channel details and analyze data in the Streamlit app.

## Description

The project aims to develop a Streamlit application that allows users to access and analyze data from multiple YouTube channels. The application will utilize the Google API to retrieve relevant data such as channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, and comments for each video. The data will be stored in a MongoDB database as a data lake, and users will have the option to collect data for up to 10 different YouTube channels and store them in the data lake.

To provide further data analysis capabilities, the application will allow users to select a channel name and migrate its data from the data lake to a SQL database as tables. 

The overall approach involves setting up a Streamlit app to create a user-friendly interface, connecting to the YouTube API using the Google API client library for Python to retrieve data, storing the data in a MongoDB data lake, migrating the data to a SQL data warehouse, querying the SQL database using SQL queries, and displaying the retrieved data in the Streamlit app using data visualization features.

## Getting Started

### Requirements

* **Operating System:** Windows, macOS and Linux distributions.
* **Softwares:** Python, Git.
* **Python Libraries:** pymongo, googleapiclient.discovery, mysql.connector, datetime, streamlit, matplotlib.pyplot, matplotlib.pyplot and seaborn.

Once you have satisfied the prerequisites and installed the required libraries, you can proceed with running the YouTube Data Harvesting and Warehousing application on your system.



### Installing
Follow the below steps to step-up the environment.
* **Clone the GitHub repository:** Run the following command line in command:


   ```
   git clone <repository_url>
   ```

* **API Credentials:** To access the YouTube API, you need to obtain API credentials from the Google Developer Console. Follow the instructions provided by the YouTube API documentation (https://developers.google.com/youtube/v3/getting-started) to create a project, enable the YouTube Data API v3, and obtain the necessary API keys. Once you have the API keys, you will need to add them to the program's code. Open the file in a text editor and replace the placeholder values with your actual API keys.

### Executing program
To run the YouTube Data Harvesting and Warehousing program, follow these step-by-step instructions:

* Open a terminal or command prompt.

* Navigate to the directory where the program is located. For example:

   ```
   cd \YT_Analysis
   ```

* (Optional) If you're using a virtual environment, activate it. This step may not be necessary if you're running the program without a virtual environment.

* Run this command:

   ```
   streamlit run streamlit_ui.py
   ```
* You can now view your Streamlit app in your browser. 

