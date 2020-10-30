import config
import requests
import json
import pandas as pd
from tqdm import tqdm
import spotipy.util as util
import pandas_gbq
from google.oauth2 import service_account
from datetime import datetime,timezone, timedelta

credentials = service_account.Credentials.from_service_account_file(
    r'/Users/Nicholas/Desktop/GCP/GCP_Keys/spotify-project-287802-e5e6c43e8ecb.json'
)

client_id = config.client_id
client_secret = config.client_secret
username = config.username

# Access to Spotify API

username = config.username
client_id = config.client_id
client_secret = config.client_secret
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-recently-played, playlist-modify-public, playlist-modify-private'

auth_token = util.prompt_for_user_token(username=username,
                                   scope=scope,
                                   client_id=client_id,
                                   client_secret=client_secret,
                                   redirect_uri=redirect_uri)


def gcp_top5():
    '''
    Queries GCP BQ to pull your top 5 most played tracks for the month
    :return: top5_mtracks
    '''
    project_id = "spotify-project-287802"

    # Query GCP BQ for top 5 played tracks
    sql = """
    SELECT track_id
        , album_id
        , artist_id
        , track_name
        , count(track_id) AS track_count
        , artist_name
        , album_name
    FROM `spotify-project-287802.spotify_api.recently_played_tracks`
    WHERE CAST(CAST(local_time AS TIMESTAMP) AS DATE) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY track_id
        , album_id
        , artist_id
        , track_name
        , artist_name
        , album_name
    order by track_count DESC 
    """
    # Load table into df
    bq_df2 = pandas_gbq.read_gbq(sql, project_id=project_id, credentials=credentials)

    # Query the BQ table for case_ids
    project_id = "spotify-project-287802"

    sql = """
    SELECT track_id
    FROM `spotify-project-287802.spotify_api.spotify_python_playlist` 
    """
    # Load table into df
    track_check = pandas_gbq.read_gbq(sql, project_id=project_id, credentials=credentials)

    # Create list of dq_df case_ids
    case_to_drop = track_check['track_id'].tolist()
    # Compare case_ids from df1 if already in case_to_drop list
    bq_df2_clean = bq_df2[~bq_df2['track_id'].str.contains('|'.join(case_to_drop))]
    print('After duplicate check, there are now {} new Case IDs from the API.'.format(len(bq_df2_clean['track_id'])))

    top5_mtracks = bq_df2_clean.iloc[:5]
    return top5_mtracks


def gcp_dup_check(auth_token):
    '''
    Checks for duplicate songs already added to the playlist. If duplicated, it removes the song(s) from
    the dataframe.
    :param auth_token: Spotify auth token
    :return: spotify_urls_ls
    '''
    top5_mtracks = gcp_top5()
    # load data into GCP for later use
    print('Loading data into GCP BigQuery')
    # Load into GCP BigQuery
    # Connect to Google Cloud API and upload dataframe
    destinatoin_table = 'spotify_api.spotify_python_playlist'
    project_id = 'spotify-project-287802'


    pandas_gbq.to_gbq(top5_mtracks, destinatoin_table, project_id, if_exists='append',
                      credentials=credentials)
    print('Script is complete; check table for details.')

    track_id_ls=top5_mtracks['track_id'].tolist()

    track_data = []
    for id in tqdm(track_id_ls):
        base_url = f'https://api.spotify.com/v1/audio-features/{id}?'

        #2. Authentication
        #3. Parameters -- would be stored with authentication
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        r = requests.get(base_url, headers=headers)
        track_data.append(json.loads(r.text))

    track_df = pd.json_normalize(track_data)

    # Used to post songs to playlist
    spotify_urls_ls = track_df['uri'].tolist()
    return spotify_urls_ls


def pull_playlist_info():
    '''
    Pulls spotify playlist info
    :return: playlist_df
    '''
    # Check user's playlist
    username = config.username
    client_id = config.client_id
    client_secret = config.client_secret
    redirect_uri = 'http://localhost:7777/callback'
    scope = 'playlist-read-collaborative, playlist-read-private, playlist-modify-public, playlist-modify-private'

    auth_token = util.prompt_for_user_token(username=username,
                                       scope=scope,
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri=redirect_uri)

    base_url = f'https://api.spotify.com/v1/users/{username}/playlists?'

    #2. Authentication
    #3. Parameters -- would be stored with authentication
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    #4. Create an empty list
    personal_playlist_data = [] #would be good explore how to capture data at different points in time
    r = requests.get(base_url+"&limit=50", headers=headers)
    personal_playlist_data.append(json.loads(r.text))

    playlist_ids = []
    playlist_names = []
    playlist_descriptions = []
    playlist_owners = []
    playlist_publics = []

    for i in range(len(personal_playlist_data[0]['items'])):
        playlist_ids.append(personal_playlist_data[0]['items'][i]['id'])
        playlist_names.append(personal_playlist_data[0]['items'][i]['name'])
        playlist_descriptions.append(personal_playlist_data[0]['items'][i]['description'])
        playlist_owners.append(personal_playlist_data[0]['items'][i]['owner']['display_name'])
        playlist_publics.append(personal_playlist_data[0]['items'][i]['public'])

    list_dic4={'playlist_id':playlist_ids,
               'playlist_name':playlist_names,
               'playlist_description':playlist_descriptions,
               'playlist_owner':playlist_owners,
               'playlist_public':playlist_publics
        }

    playlist_df = pd.DataFrame(list_dic4)
    return playlist_df


def playlist_check():
    '''
    Checks to see if automated playlist already exist. If not, it creates it.
    :return: playlist_df
    '''
    playlist_df = pull_playlist_info()
    cur_year = datetime.today().strftime('%Y')
    # Check to verify if playlist exist, if not create it
    if f'Test Python Playlist {cur_year}' in set(playlist_df['playlist_name']):
        print("Playlist exist!")

        base_url = f'https://api.spotify.com/v1/users/{username}/playlists?'

        # 2. Authentication
        # 3. Parameters -- would be stored with authentication
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        # 4. Create an empty list
        personal_playlist_data = []  # would be good explore how to capture data at different points in time
        r = requests.get(base_url + "&limit=50", headers=headers)
        personal_playlist_data.append(json.loads(r.text))

        playlist_ids = []
        playlist_names = []
        playlist_descriptions = []
        playlist_owners = []
        playlist_publics = []

        for i in range(len(personal_playlist_data[0]['items'])):
            playlist_ids.append(personal_playlist_data[0]['items'][i]['id'])
            playlist_names.append(personal_playlist_data[0]['items'][i]['name'])
            playlist_descriptions.append(personal_playlist_data[0]['items'][i]['description'])
            playlist_owners.append(personal_playlist_data[0]['items'][i]['owner']['display_name'])
            playlist_publics.append(personal_playlist_data[0]['items'][i]['public'])

        list_dic4 = {'playlist_id': playlist_ids,
                     'playlist_name': playlist_names,
                     'playlist_description': playlist_descriptions,
                     'playlist_owner': playlist_owners,
                     'playlist_public': playlist_publics
                     }

        playlist_df = pd.DataFrame(list_dic4)
        return playlist_df

    else:
        print("Creating Playlist...")
        base_url = f'https://api.spotify.com/v1/users/{username}/playlists'

        # 2. Authentication
        # 3. Parameters -- would be stored with authentication
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        request_body = json.dumps({
            "name": f"Test Python Playlist {cur_year}",
            "description": f"This is a test playlist generated by Python for {cur_year}.",
            "public": False  # private
        })
        # 4. Create an empty list
        r = requests.post(url=base_url, data=request_body, headers=headers)
        print(r.text)

        base_url = f'https://api.spotify.com/v1/users/{username}/playlists?'

        # 2. Authentication
        # 3. Parameters -- would be stored with authentication
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        # 4. Create an empty list
        personal_playlist_data = []  # would be good explore how to capture data at different points in time
        r = requests.get(base_url + "&limit=50", headers=headers)
        personal_playlist_data.append(json.loads(r.text))

        playlist_ids = []
        playlist_names = []
        playlist_descriptions = []
        playlist_owners = []
        playlist_publics = []

        for i in range(len(personal_playlist_data[0]['items'])):
            playlist_ids.append(personal_playlist_data[0]['items'][i]['id'])
            playlist_names.append(personal_playlist_data[0]['items'][i]['name'])
            playlist_descriptions.append(personal_playlist_data[0]['items'][i]['description'])
            playlist_owners.append(personal_playlist_data[0]['items'][i]['owner']['display_name'])
            playlist_publics.append(personal_playlist_data[0]['items'][i]['public'])

        list_dic4 = {'playlist_id': playlist_ids,
                     'playlist_name': playlist_names,
                     'playlist_description': playlist_descriptions,
                     'playlist_owner': playlist_owners,
                     'playlist_public': playlist_publics
                     }

        playlist_df = pd.DataFrame(list_dic4)
        return playlist_df


def pull_playlist_id():
    '''
    Calls playlist API and pulls playlist ID to push tracks to in next function.
    :return: playlist_id
    '''
    playlist_df = playlist_check()
    # Pull playlist ID
    username = config.username
    client_id = config.client_id
    client_secret = config.client_secret
    redirect_uri = 'http://localhost:7777/callback'
    scope = 'playlist-read-private'

    auth_token = util.prompt_for_user_token(username=username,
                                       scope=scope,
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri=redirect_uri)

    base_url = f'https://api.spotify.com/v1/users/{username}/playlists?'

    #2. Authentication
    #3. Parameters -- would be stored with authentication
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    #4. Create an empty list
    personal_playlist_data = [] #would be good explore how to capture data at different points in time
    r = requests.get(base_url+"&limit=50", headers=headers)
    personal_playlist_data.append(json.loads(r.text))

    playlist_ids = []
    playlist_names = []
    playlist_descriptions = []
    playlist_owners = []
    playlist_publics = []

    for i in range(len(personal_playlist_data[0]['items'])):
        playlist_ids.append(personal_playlist_data[0]['items'][i]['id'])
        playlist_names.append(personal_playlist_data[0]['items'][i]['name'])
        playlist_descriptions.append(personal_playlist_data[0]['items'][i]['description'])
        playlist_owners.append(personal_playlist_data[0]['items'][i]['owner']['display_name'])
        playlist_publics.append(personal_playlist_data[0]['items'][i]['public'])

    list_dic4={'playlist_id':playlist_ids,
               'playlist_name':playlist_names,
               'playlist_description':playlist_descriptions,
               'playlist_owner':playlist_owners,
               'playlist_public':playlist_publics
        }

    playlist_df = pd.DataFrame(list_dic4)
    playlist_id = playlist_df.loc[playlist_df['playlist_name'] == 'Test Python Playlist 2020', 'playlist_id'].tolist()[0]
    return playlist_id


def add_songs():
    '''
    Adds top 5 new tracks to automated playlist
    :return: N/A
    '''
    playlist_id = pull_playlist_id()
    spotify_urls_ls = gcp_dup_check(auth_token)
    # Push songs to playlist
    #playlist_id = '79tXL4BD7MnqvpMZtKDho9'
    base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Must be in list to load into playlist
    uris = spotify_urls_ls

    # Authentication
    # Parameters -- would be stored with authentication
    headers = {
        "Content-Type":"application/json",
        "Authorization": f"Bearer {auth_token}"
    }

    request_body = json.dumps({
              "uris":uris
            })
    # Make request
    r = requests.post(url = base_url, data = request_body, headers=headers)
    r.text


add_songs()

